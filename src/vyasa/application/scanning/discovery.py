"""Discover the Git repositories under one workspace root."""

from __future__ import annotations

import uuid
from collections import Counter
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from vyasa import __version__
from vyasa.adapters.filesystem.repository_walk import find_repositories
from vyasa.application.configuration.workspace import check_root
from vyasa.domain.discovery import (
    COMPLETE,
    EXCLUDED,
    FAILED,
    INACCESSIBLE,
    MALFORMED,
    OUTCOMES,
    PARTIAL,
    SKIPPED_BY_POLICY,
    Candidate,
    DiscoveryOptions,
    DiscoveryRun,
)
from vyasa.domain.workspace_config import ACCESSIBLE, MISSING, NOT_A_DIRECTORY

ROOT_REASONS = {MISSING: "root_not_found", NOT_A_DIRECTORY: "root_not_a_directory"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex


def _order(candidate: Candidate) -> tuple[str, ...]:
    return tuple(part.casefold() for part in candidate.path.parts)


def discover_repositories(
    root: Path | str,
    options: DiscoveryOptions = DiscoveryOptions(),
    now: Callable[[], datetime] = _utc_now,
    new_id: Callable[[], str] = _new_id,
) -> DiscoveryRun:
    """Find repositories under ``root`` and record what happened. Never raises for a filesystem problem."""
    root = Path(root)
    started = now()
    root_state = check_root(root)

    if root_state != ACCESSIBLE:
        repositories: tuple[Candidate, ...] = ()
        issues = (Candidate(root, INACCESSIBLE, reason=ROOT_REASONS.get(root_state, "root_unreadable")),)
        excluded = 0
        status = FAILED
    else:
        findings = find_repositories(root, options)
        repositories = tuple(sorted(findings.repositories, key=_order))
        # Real problems first, so a full list never hides one behind policy skips (sort is stable).
        issues = tuple(sorted(findings.issues, key=lambda c: c.outcome == SKIPPED_BY_POLICY))
        excluded = findings.excluded
        status = PARTIAL if issues else COMPLETE

    counted = Counter(issue.outcome for issue in issues)
    counts = {outcome: counted[outcome] for outcome in (INACCESSIBLE, MALFORMED, SKIPPED_BY_POLICY)}
    counts[EXCLUDED] = excluded
    counts["eligible"] = len(repositories)
    shown = issues[: options.max_issues]
    return DiscoveryRun(
        run_id=new_id(),
        root=root,
        started_at=started,
        finished_at=now(),
        status=status,
        tool_version=__version__,
        options=options,
        counts={outcome: counts[outcome] for outcome in OUTCOMES},
        repositories=repositories,
        issues=shown,
        issues_omitted=len(issues) - len(shown),
    )
