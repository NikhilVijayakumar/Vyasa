"""Store a discovery run in the index."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from vyasa.adapters.sqlite import lock, projects
from vyasa.application.configuration.workspace import data_directory
from vyasa.domain.discovery import COMPLETE, FAILED, INACCESSIBLE, PARTIAL, DiscoveryRun
from vyasa.domain.index import (
    COMPLETED,
    FAILED as RUN_FAILED,
    INTERRUPTED,
    PARTIAL as RUN_PARTIAL,
    RUNNING,
    freshness as _freshness,
)

INDEX_FILE = "index.sqlite3"
STATUS = {COMPLETE: COMPLETED, PARTIAL: RUN_PARTIAL, FAILED: RUN_FAILED}
# Skips that hide directories from the walk. An ignore-file mistake hides nothing.
BENIGN_WARNINGS = frozenset({"ignore_file"})


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def index_path(environ: Mapping[str, str] | None = None, home: Path | None = None, platform: str | None = None) -> Path:
    return data_directory(environ, home, platform) / INDEX_FILE


@dataclass(frozen=True)
class StoredRun:
    run_id: str
    status: str
    counts: Mapping[str, int]


def store_run(
    connection: sqlite3.Connection,
    run: DiscoveryRun,
    *,
    owner: str,
    now: Callable[[], datetime] = _utc_now,
) -> StoredRun:
    """Store ``run`` as the one writer. Each project commits alone; nothing is ever deleted."""
    lock.acquire(connection, owner, run.run_id, now())
    counts: Counter[str] = Counter()
    try:
        connection.execute(
            "INSERT INTO scan_runs (run_id, root, status, tool_version, started_at) VALUES (?, ?, ?, ?, ?)",
            (run.run_id, str(run.root), RUNNING, run.tool_version, run.started_at.isoformat()),
        )
        for candidate in run.repositories:
            counts[projects.upsert(connection, candidate, run.root, run.run_id, now())] += 1
            lock.heartbeat(connection, run.run_id, now())
        for issue in run.issues:
            if issue.outcome == INACCESSIBLE and projects.mark_inaccessible(connection, issue.path, run.run_id, now()):
                counts[INACCESSIBLE] += 1
        # Absence is only known when the whole tree was seen.
        if run.status == COMPLETE and all(w.reason in BENIGN_WARNINGS for w in run.warnings):
            gone = projects.mark_absent(connection, run.root, run.run_id, now())
            if gone:
                counts["missing"] = gone
        projects.sync_duplicates(connection, run.run_id, now())
        status = STATUS[run.status]
        connection.execute(
            "UPDATE scan_runs SET status = ?, finished_at = ?, counts = ? WHERE run_id = ?",
            (status, now().isoformat(), json.dumps(dict(counts)), run.run_id),
        )
    except BaseException:
        connection.execute(
            "UPDATE scan_runs SET status = ?, finished_at = ? WHERE run_id = ?", (INTERRUPTED, now().isoformat(), run.run_id)
        )
        raise
    finally:
        lock.release(connection, run.run_id)
    return StoredRun(run.run_id, status, dict(counts))


def freshness(connection: sqlite3.Connection, now: datetime | None = None) -> str:
    """Read-only: how current the index is."""
    row = connection.execute("SELECT status, finished_at FROM scan_runs ORDER BY started_at DESC, rowid DESC LIMIT 1").fetchone()
    if row is None:
        return _freshness(None, None, now or _utc_now())
    finished = datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None
    return _freshness(row["status"], finished, now or _utc_now())
