"""The single-writer lock: one row with an owner and a heartbeat."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from vyasa.domain.index import INTERRUPTED, IN_PROGRESS, LOCK_TIMEOUT, RUNNING, UNAVAILABLE, IndexStoreError


def acquire(connection: sqlite3.Connection, owner: str, run_id: str, now: datetime) -> None:
    """Take the lock, or raise ``OPERATION_IN_PROGRESS`` when a live writer holds it.

    A lock whose heartbeat is older than the timeout is dead: it is replaced, and every run
    still ``running`` (its writer is gone) becomes ``interrupted``.
    """
    try:
        connection.execute("BEGIN IMMEDIATE")
    except sqlite3.OperationalError as error:
        raise IndexStoreError(UNAVAILABLE, f"the index is locked by another connection: {error}") from error
    try:
        held = connection.execute("SELECT heartbeat_at FROM index_lock WHERE id = 1").fetchone()
        if held and now - datetime.fromisoformat(held["heartbeat_at"]) <= LOCK_TIMEOUT:
            raise IndexStoreError(IN_PROGRESS, "another refresh is running")
        connection.execute("DELETE FROM index_lock")
        connection.execute(
            "UPDATE scan_runs SET status = ?, finished_at = ? WHERE status = ?",
            (INTERRUPTED, now.isoformat(), RUNNING),
        )
        connection.execute(
            "INSERT INTO index_lock (id, owner, run_id, heartbeat_at) VALUES (1, ?, ?, ?)",
            (owner, run_id, now.isoformat()),
        )
        connection.execute("COMMIT")
    except BaseException:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise


def heartbeat(connection: sqlite3.Connection, run_id: str, now: datetime) -> None:
    connection.execute("UPDATE index_lock SET heartbeat_at = ? WHERE run_id = ?", (now.isoformat(), run_id))


def release(connection: sqlite3.Connection, run_id: str) -> None:
    connection.execute("DELETE FROM index_lock WHERE run_id = ?", (run_id,))
