"""Project and checkout rows. Every value is a bound parameter."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from vyasa.domain.discovery import Candidate
from vyasa.domain.index import ACTIVE, INACCESSIBLE, MISSING

ADDED, ATTACHED, UPDATED, UNCHANGED, RESTORED, CONFLICT = "added", "attached", "updated", "unchanged", "restored", "conflicts"
REMOTE = "remote"


def path_key(path: Path) -> str:
    return os.path.normcase(str(path))


def _fields(candidate: Candidate) -> tuple:
    remote = candidate.remote
    return (
        candidate.kind,
        json.dumps(list(candidate.markers)),
        candidate.git,
        remote.provider if remote else None,
        remote.host if remote else None,
        remote.identity if remote else None,
        candidate.remote_status,
    )


def _event(connection: sqlite3.Connection, project_id: str, kind: str, detail: dict, run_id: str, stamp: str) -> None:
    connection.execute(
        "INSERT INTO identity_events (project_id, kind, detail, run_id, at) VALUES (?, ?, ?, ?, ?)",
        (project_id, kind, json.dumps(detail, sort_keys=True), run_id, stamp),
    )


def _alias_owner(connection: sqlite3.Connection, identity: str | None) -> str | None:
    if identity is None:
        return None
    row = connection.execute(
        "SELECT project_id FROM project_aliases WHERE alias_kind = ? AND alias_value = ?", (REMOTE, identity)
    ).fetchone()
    return row[0] if row else None


def _add_alias(connection: sqlite3.Connection, project_id: str, identity: str, stamp: str) -> None:
    connection.execute(
        "INSERT INTO project_aliases (alias_kind, alias_value, project_id, first_seen_at) VALUES (?, ?, ?, ?)",
        (REMOTE, identity, project_id, stamp),
    )


def refresh_state(connection: sqlite3.Connection, project_id: str, stamp: str) -> None:
    """A project is active while any checkout is, else inaccessible while any is, else missing."""
    states = {r[0] for r in connection.execute("SELECT state FROM checkouts WHERE project_id = ?", (project_id,))}
    state = ACTIVE if ACTIVE in states else INACCESSIBLE if INACCESSIBLE in states else MISSING
    connection.execute(
        "UPDATE projects SET state = ?, updated_at = CASE WHEN state = ? THEN updated_at ELSE ? END WHERE project_id = ?",
        (state, state, stamp, project_id),
    )


def upsert(connection: sqlite3.Connection, candidate: Candidate, root: Path, run_id: str, now: datetime) -> str:
    """Store one eligible repository in its own transaction. Returns what happened to it.

    The project is found by its remote identity alias, then by checkout path. When the two
    point at different projects nothing is merged or moved; the conflict is recorded.
    """
    stamp = now.isoformat()
    key = path_key(candidate.path)
    fields = _fields(candidate)
    identity = candidate.remote.identity if candidate.remote else None
    connection.execute("BEGIN IMMEDIATE")
    try:
        row = connection.execute(
            "SELECT checkout_id, project_id, state, kind, markers, git, remote_provider, remote_host,"
            " remote_identity, remote_status FROM checkouts WHERE path_key = ?",
            (key,),
        ).fetchone()
        owner = _alias_owner(connection, identity)
        if row is None:
            if owner is None:
                project_id = uuid.uuid4().hex
                connection.execute(
                    "INSERT INTO projects (project_id, display_name, state, identity_status, identity_source,"
                    " created_at, updated_at, last_seen_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (project_id, candidate.path.name or str(candidate.path), ACTIVE,
                     "resolved" if identity else "provisional", REMOTE if identity else "path", stamp, stamp, stamp),
                )
                if identity:
                    _add_alias(connection, project_id, identity, stamp)
                _event(connection, project_id, "created", {"alias": identity}, run_id, stamp)
                outcome = ADDED
            else:
                project_id, outcome = owner, ATTACHED
            connection.execute(
                "INSERT INTO checkouts (project_id, path, path_key, root, kind, markers, git, remote_provider,"
                " remote_host, remote_identity, remote_status, state, first_seen_at, last_seen_at, last_run_id)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (project_id, str(candidate.path), key, str(root), *fields, ACTIVE, stamp, stamp, run_id),
            )
        else:
            project_id = row["project_id"]
            if owner is not None and owner != project_id:
                detail = json.dumps({"alias": identity, "owner": owner}, sort_keys=True)
                if not connection.execute(
                    "SELECT 1 FROM identity_events WHERE project_id = ? AND kind = 'identity_conflict' AND detail = ?",
                    (project_id, detail),
                ).fetchone():
                    _event(connection, project_id, "identity_conflict", {"alias": identity, "owner": owner}, run_id, stamp)
                connection.execute(
                    "UPDATE checkouts SET last_seen_at = ?, last_run_id = ? WHERE checkout_id = ?",
                    (stamp, run_id, row["checkout_id"]),
                )
                connection.execute("COMMIT")
                return CONFLICT
            same = tuple(row[name] for name in (
                "kind", "markers", "git", "remote_provider", "remote_host", "remote_identity", "remote_status",
            )) == fields
            outcome = RESTORED if row["state"] != ACTIVE else UNCHANGED if same else UPDATED
            if identity and owner is None:
                _add_alias(connection, project_id, identity, stamp)
                _event(connection, project_id, "alias_added", {"alias": identity}, run_id, stamp)
                connection.execute(
                    "UPDATE projects SET identity_status = 'resolved', identity_source = 'remote' WHERE project_id = ?"
                    " AND identity_status = 'provisional'",
                    (project_id,),
                )
                outcome = UPDATED if outcome == UNCHANGED else outcome
            connection.execute(
                "UPDATE checkouts SET root = ?, kind = ?, markers = ?, git = ?, remote_provider = ?, remote_host = ?,"
                " remote_identity = ?, remote_status = ?, state = ?, last_seen_at = ?, last_run_id = ?"
                " WHERE checkout_id = ?",
                (str(root), *fields, ACTIVE, stamp, run_id, row["checkout_id"]),
            )
        refresh_state(connection, project_id, stamp)
        connection.execute("UPDATE projects SET last_seen_at = ? WHERE project_id = ?", (stamp, project_id))
        connection.execute("COMMIT")
        return outcome
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise


def mark_inaccessible(connection: sqlite3.Connection, path: Path, run_id: str, now: datetime) -> bool:
    """The run saw this stored path and could not read it."""
    return _set_state(connection, "path_key = ?", (path_key(path),), INACCESSIBLE, run_id, now) > 0


def mark_absent(connection: sqlite3.Connection, root: Path, run_id: str, now: datetime) -> int:
    """Checkouts of ``root`` that a complete run did not see become missing."""
    return _set_state(
        connection, "root = ? AND state != 'missing' AND COALESCE(last_run_id, '') != ?", (str(root), run_id), MISSING, None, now
    )


def _set_state(connection: sqlite3.Connection, where: str, args: tuple, state: str, run_id: str | None, now: datetime) -> int:
    """``where`` is one of the fixed clauses above; values are always bound."""
    stamp = now.isoformat()
    connection.execute("BEGIN IMMEDIATE")
    try:
        ids = [r[0] for r in connection.execute(f"SELECT project_id FROM checkouts WHERE {where}", args)]
        connection.execute(
            f"UPDATE checkouts SET state = ?, last_run_id = COALESCE(?, last_run_id) WHERE {where}", (state, run_id, *args)
        )
        for project_id in dict.fromkeys(ids):
            refresh_state(connection, project_id, stamp)
        connection.execute("COMMIT")
        return len(ids)
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise


def list_projects(connection: sqlite3.Connection, state: str | None = None) -> list[sqlite3.Row]:
    query = (
        "SELECT p.project_id, p.display_name, p.state, p.identity_status, p.identity_source, c.path, c.root, c.kind, c.remote_provider, c.remote_host,"
        " c.remote_identity, c.remote_status, c.last_seen_at FROM projects p JOIN checkouts c USING (project_id)"
    )
    if state is None:
        return connection.execute(query + " ORDER BY c.path_key").fetchall()
    return connection.execute(query + " WHERE p.state = ? ORDER BY c.path_key", (state,)).fetchall()


def list_aliases(connection: sqlite3.Connection, project_id: str) -> list[str]:
    rows = connection.execute(
        "SELECT alias_value FROM project_aliases WHERE project_id = ? ORDER BY first_seen_at, alias_value", (project_id,)
    )
    return [r[0] for r in rows]


def list_events(connection: sqlite3.Connection, project_id: str) -> list[sqlite3.Row]:
    return connection.execute(
        "SELECT kind, detail, run_id, at FROM identity_events WHERE project_id = ? ORDER BY event_id", (project_id,)
    ).fetchall()
