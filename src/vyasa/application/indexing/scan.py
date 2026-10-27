"""Scan the configured workspace roots and store what was found."""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

from vyasa.application.indexing.store import StoredRun, store_run
from vyasa.application.scanning.discovery import discover_repositories
from vyasa.application.scanning.checkout_scan import scan_checkout
from vyasa.application.scanning.file_composition import default_file_types
from vyasa.application.scanning.frameworks import default_registry
from vyasa.application.scanning.markers import default_marker_rules
from vyasa.domain.discovery import COMPLETE, ELIGIBLE, PARTIAL, DiscoveryRun, ScanWarning
from vyasa.domain.languages import DETECTION_ERROR, CheckoutScan, LanguageOutcome
from vyasa.domain.workspace_config import WorkspaceConfig

NOT_DETECTED_ADVICE = "Languages could not be detected for these checkouts; their other data was stored. Rescan to retry."


@dataclass(frozen=True)
class RootResult:
    root: Path
    run: DiscoveryRun
    stored: StoredRun


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def default_detect() -> Callable[[Path], CheckoutScan]:
    """The scanner every scan uses: counts, languages, markers, and frameworks from one walk."""
    types, rules, registry = default_file_types(), default_marker_rules(), default_registry()
    return lambda path: scan_checkout(path, types, rules=rules, frameworks=registry)


def enrich_run(run: DiscoveryRun, detect: Callable[[Path], CheckoutScan] | None = None) -> DiscoveryRun:
    """Attach what the scan learns to each eligible checkout. A failure is kept for that checkout and makes the run partial."""
    detect = detect or default_detect()
    found, failed = [], []
    for candidate in run.repositories:
        if candidate.outcome != ELIGIBLE:
            found.append(candidate)
            continue
        started = time.monotonic()
        try:
            scan = detect(candidate.path)
            outcome = LanguageOutcome(report=scan.languages, composition=scan.composition, markers=scan.markers, frameworks=scan.frameworks,
                                   seconds=time.monotonic() - started)
        except Exception:  # one checkout must not stop the others; the reason is a fixed code, never the message
            outcome = LanguageOutcome(failed=DETECTION_ERROR, seconds=time.monotonic() - started)
            failed.append(candidate.path)
        found.append(replace(candidate, languages=outcome))
    if not failed:
        return replace(run, repositories=tuple(found))
    warning = ScanWarning("language_detection", len(failed), tuple(failed[:5]), NOT_DETECTED_ADVICE)
    return replace(run, repositories=tuple(found), status=PARTIAL if run.status == COMPLETE else run.status,
                   warnings=(*run.warnings, warning))


def scan_workspace(
    config: WorkspaceConfig,
    connection: sqlite3.Connection,
    *,
    owner: str,
    discover: Callable[[Path], DiscoveryRun] = discover_repositories,
    detect: Callable[[Path], CheckoutScan] | None = None,
    now: Callable[[], datetime] = _utc_now,
) -> tuple[RootResult, ...]:
    """Discover and store each configured root in turn. Nothing outside the configured roots is visited.

    A root that cannot be read is stored as a failed run and the others still run. A held writer lock
    raises ``OPERATION_IN_PROGRESS``.
    """
    detect = detect or default_detect()
    results = []
    for root in config.roots:
        run = enrich_run(discover(root), detect)
        results.append(RootResult(root, run, store_run(connection, run, owner=owner, now=now)))
    return tuple(results)
