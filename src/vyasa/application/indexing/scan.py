"""Scan the configured workspace roots and store what was found."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from vyasa.application.indexing.store import StoredRun, store_run
from vyasa.application.scanning.discovery import discover_repositories
from vyasa.domain.discovery import DiscoveryRun
from vyasa.domain.workspace_config import WorkspaceConfig


@dataclass(frozen=True)
class RootResult:
    root: Path
    run: DiscoveryRun
    stored: StoredRun


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def scan_workspace(
    config: WorkspaceConfig,
    connection: sqlite3.Connection,
    *,
    owner: str,
    discover: Callable[[Path], DiscoveryRun] = discover_repositories,
    now: Callable[[], datetime] = _utc_now,
) -> tuple[RootResult, ...]:
    """Discover and store each configured root in turn. Nothing outside the configured roots is visited.

    A root that cannot be read is stored as a failed run and the others still run. A held writer lock
    raises ``OPERATION_IN_PROGRESS``.
    """
    results = []
    for root in config.roots:
        run = discover(root)
        results.append(RootResult(root, run, store_run(connection, run, owner=owner, now=now)))
    return tuple(results)
