"""Read-only questions about the index: search, one project, and index status.

Every function takes a connection opened read-only and never writes or scans. Absolute paths and scanned
roots are left out unless the caller asks. Nothing here knows about MCP.
"""

from __future__ import annotations

import base64
import binascii
import json
import sqlite3
from collections.abc import Callable
from datetime import datetime, timezone

from vyasa.adapters.sqlite import projects, review
from vyasa.application.indexing.store import freshness
from vyasa.domain.index import (
    INVALID_CURSOR,
    INVALID_INPUT,
    PROJECT_NOT_FOUND,
    PROJECT_STATES,
    IndexStoreError,
)

SCHEMA_VERSION = "1"
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
MAX_QUERY = 200
IDENTITY_STATUSES = ("resolved", "provisional", "ambiguous")
PROVIDERS = ("github", "bitbucket", "gitlab", "other", "local", "none")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _envelope(connection: sqlite3.Connection, data: dict, now: datetime) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "data": data,
        "meta": {
            "generated_at": now.isoformat(),
            "index_version": connection.execute("PRAGMA user_version").fetchone()[0],
            "freshness": freshness(connection, now),
        },
    }


def _choices(name: str, value: object, allowed: tuple[str, ...]) -> list[str] | None:
    if value is None:
        return None
    values = [value] if isinstance(value, str) else value
    if not isinstance(values, (list, tuple)) or not all(isinstance(v, str) for v in values):
        raise IndexStoreError(INVALID_INPUT, f"{name} must be a string or a list of strings")
    bad = [v for v in values if v not in allowed]
    if bad:
        raise IndexStoreError(INVALID_INPUT, f"{name}: unknown value {bad[0]!r}; allowed: {', '.join(allowed)}")
    return sorted(set(values)) or None


def _like(text: str) -> str:
    """A LIKE pattern matching ``text`` literally anywhere."""
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _encode(name_key: str, project_id: str) -> str:
    return base64.urlsafe_b64encode(json.dumps([name_key, project_id]).encode()).decode()


def _decode(cursor: str) -> tuple[str, str]:
    try:
        key, project_id = json.loads(base64.urlsafe_b64decode(cursor.encode()))
        if isinstance(key, str) and isinstance(project_id, str):
            return key, project_id
    except (ValueError, TypeError, binascii.Error):
        pass
    raise IndexStoreError(INVALID_CURSOR, "the cursor was not issued by this server")


def search_projects(
    connection: sqlite3.Connection,
    *,
    query: str | None = None,
    state: object = None,
    provider: object = None,
    identity_status: object = None,
    limit: int = DEFAULT_LIMIT,
    cursor: str | None = None,
    now: Callable[[], datetime] = _utc_now,
) -> dict:
    if query is not None and (not isinstance(query, str) or not 1 <= len(query) <= MAX_QUERY):
        raise IndexStoreError(INVALID_INPUT, f"query must be 1 to {MAX_QUERY} characters")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_LIMIT:
        raise IndexStoreError(INVALID_INPUT, f"limit must be an integer from 1 to {MAX_LIMIT}")
    if cursor is not None and not isinstance(cursor, str):
        raise IndexStoreError(INVALID_INPUT, "cursor must be a string")
    states = _choices("state", state, PROJECT_STATES)
    providers = _choices("provider", provider, PROVIDERS)
    statuses = _choices("identity_status", identity_status, IDENTITY_STATUSES)
    after = _decode(cursor) if cursor else None

    # Clauses are fixed strings; every value is bound.
    where, args = ["1 = 1"], []
    needle = query.lower() if query else None
    if needle:
        where.append(
            "(lower(p.display_name) LIKE ? ESCAPE '\\' OR EXISTS (SELECT 1 FROM checkouts c WHERE"
            " c.project_id = p.project_id AND lower(c.remote_identity) LIKE ? ESCAPE '\\'))"
        )
        args += [_like(needle)] * 2
    if states:
        where.append(f"p.state IN ({', '.join('?' * len(states))})")
        args += states
    if statuses:
        where.append(f"p.identity_status IN ({', '.join('?' * len(statuses))})")
        args += statuses
    if providers:
        where.append(
            "EXISTS (SELECT 1 FROM checkouts c WHERE c.project_id = p.project_id AND"
            f" COALESCE(c.remote_provider, 'none') IN ({', '.join('?' * len(providers))}))"
        )
        args += providers
    if after:
        where.append("(lower(p.display_name), p.project_id) > (?, ?)")
        args += list(after)
    rows = connection.execute(
        "SELECT p.project_id, p.display_name, p.state, p.identity_status, lower(p.display_name) AS name_key"
        f" FROM projects p WHERE {' AND '.join(where)} ORDER BY name_key, p.project_id LIMIT ?",
        (*args, limit + 1),
    ).fetchall()

    page = rows[:limit]
    items = []
    for row in page:
        checkouts = connection.execute(
            "SELECT COALESCE(remote_provider, 'none') AS provider, remote_identity FROM checkouts WHERE project_id = ?",
            (row["project_id"],),
        ).fetchall()
        matched = []
        if needle and needle in row["display_name"].lower():
            matched.append("display_name")
        if needle and any(c["remote_identity"] and needle in c["remote_identity"].lower() for c in checkouts):
            matched.append("remote_identity")
        flagged = connection.execute(
            "SELECT 1 FROM review_flags WHERE project_id = ? AND state = 'open' LIMIT 1", (row["project_id"],)
        ).fetchone()
        items.append({
            "project_id": row["project_id"],
            "display_name": row["display_name"],
            "state": row["state"],
            "identity_status": row["identity_status"],
            "providers": sorted({c["provider"] for c in checkouts}),
            "has_open_candidates": flagged is not None,
            "matched": matched,
        })
    more = len(rows) > limit
    last = page[-1] if page else None
    data = {
        "projects": items,
        "page": {"limit": limit, "next_cursor": _encode(last["name_key"], last["project_id"]) if more and last else None, "has_more": more},
    }
    return _envelope(connection, data, now())


def get_project(
    connection: sqlite3.Connection,
    project_id: str,
    *,
    include_paths: bool = False,
    now: Callable[[], datetime] = _utc_now,
) -> dict:
    if not isinstance(project_id, str) or not project_id:
        raise IndexStoreError(INVALID_INPUT, "project_id must be a non-empty string")
    row = connection.execute(
        "SELECT project_id, display_name, state, identity_status, identity_source, created_at, updated_at, last_seen_at"
        " FROM projects WHERE project_id = ?",
        (project_id,),
    ).fetchone()
    if row is None:
        raise IndexStoreError(PROJECT_NOT_FOUND, "no project has that identifier")
    checkouts = []
    for c in connection.execute("SELECT * FROM checkouts WHERE project_id = ? ORDER BY first_seen_at, checkout_id", (project_id,)):
        checkout = {
            "state": c["state"],
            "kind": c["kind"],
            "markers": json.loads(c["markers"]),
            "git": c["git"],
            "remote": {
                "provider": c["remote_provider"] or "none",
                "host": c["remote_host"],
                "identity": c["remote_identity"],
                "status": c["remote_status"],
            },
            "first_seen_at": c["first_seen_at"],
            "last_seen_at": c["last_seen_at"],
        }
        if include_paths:
            checkout["path"] = c["path"]
        checkouts.append(checkout)
    candidates = [
        {k: c[k] for k in ("kind", "rule", "confidence", "criteria", "review_status")}
        for c in review.list_candidates(connection)
        if c["project_id"] == project_id
    ]
    data = {
        "project_id": row["project_id"],
        "display_name": row["display_name"],
        "state": row["state"],
        "identity": {
            "status": row["identity_status"],
            "source": row["identity_source"],
            "aliases": sorted(projects.list_aliases(connection, project_id)),
        },
        "checkouts": checkouts,
        "profile": projects.project_profile(connection, project_id),
        "review_candidates": candidates,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "last_seen_at": row["last_seen_at"],
    }
    return _envelope(connection, data, now())


def get_index_status(connection: sqlite3.Connection, *, now: Callable[[], datetime] = _utc_now) -> dict:
    run = connection.execute(
        "SELECT status, finished_at, counts FROM scan_runs ORDER BY started_at DESC, rowid DESC LIMIT 1"
    ).fetchone()
    counts = {s: 0 for s in PROJECT_STATES}
    for r in connection.execute("SELECT state, COUNT(*) AS n FROM projects GROUP BY state"):
        counts[r["state"]] = r["n"]
    data = {
        "latest_run": {"status": run["status"], "finished_at": run["finished_at"], "counts": json.loads(run["counts"])} if run else None,
        "projects": {"total": sum(counts.values()), **counts},
        "open_candidates": connection.execute("SELECT COUNT(*) FROM review_flags WHERE state = 'open'").fetchone()[0],
    }
    return _envelope(connection, data, now())
