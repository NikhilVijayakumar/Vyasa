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

ADDED, UPDATED, UNCHANGED, RESTORED = "added", "updated", "unchanged", "restored"


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


def upsert(connection: sqlite3.Connection, candidate: Candidate, root: Path, run_id: str, now: datetime) -> str:
    """Store one eligible repository in its own transaction. Returns what happened to it."""
    stamp = now.isoformat()
    key = path_key(candidate.path)
    fields = _fields(candidate)
    connection.execute("BEGIN IMMEDIATE")
    try:
        row = connection.execute(
            "SELECT checkout_id, project_id, state, kind, markers, git, remote_provider, remote_host,"
            " remote_identity, remote_status FROM checkouts WHERE path_key = ?",
            (key,),
        ).fetchone()
        if row is None:
            project_id = uuid.uuid4().hex
            connection.execute(
                "INSERT INTO projects (project_id, display_name, state, created_at, updated_at, last_seen_at)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (project_id, candidate.path.name or str(candidate.path), ACTIVE, stamp, stamp, stamp),
            )
            connection.execute(
                "INSERT INTO checkouts (project_id, path, path_key, root, kind, markers, git, remote_provider,"
                " remote_host, remote_identity, remote_status, state, first_seen_at, last_seen_at, last_run_id)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (project_id, str(candidate.path), key, str(root), *fields, ACTIVE, stamp, stamp, run_id),
            )
            outcome = ADDED
        else:
            same = tuple(row[name] for name in (
                "kind", "markers", "git", "remote_provider", "remote_host", "remote_identity", "remote_status",
            )) == fields
            outcome = RESTORED if row["state"] != ACTIVE else UNCHANGED if same else UPDATED
            connection.execute(
                "UPDATE checkouts SET root = ?, kind = ?, markers = ?, git = ?, remote_provider = ?, remote_host = ?,"
                " remote_identity = ?, remote_status = ?, state = ?, last_seen_at = ?, last_run_id = ?"
                " WHERE checkout_id = ?",
                (str(root), *fields, ACTIVE, stamp, run_id, row["checkout_id"]),
            )
            connection.execute(
                "UPDATE projects SET state = ?, last_seen_at = ?,"
                " updated_at = CASE WHEN ? THEN updated_at ELSE ? END WHERE project_id = ?",
                (ACTIVE, stamp, outcome == UNCHANGED, stamp, row["project_id"]),
            )
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
        for project_id in ids:
            connection.execute("UPDATE projects SET state = ?, updated_at = ? WHERE project_id = ?", (state, stamp, project_id))
        connection.execute(
            f"UPDATE checkouts SET state = ?, last_run_id = COALESCE(?, last_run_id) WHERE {where}", (state, run_id, *args)
        )
        connection.execute("COMMIT")
        return len(ids)
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise


def list_projects(connection: sqlite3.Connection, state: str | None = None) -> list[sqlite3.Row]:
    query = (
        "SELECT p.project_id, p.display_name, p.state, c.path, c.root, c.kind, c.remote_provider, c.remote_host,"
        " c.remote_identity, c.remote_status, c.last_seen_at FROM projects p JOIN checkouts c USING (project_id)"
    )
    if state is None:
        return connection.execute(query + " ORDER BY c.path_key").fetchall()
    return connection.execute(query + " WHERE p.state = ? ORDER BY c.path_key", (state,)).fetchall()
