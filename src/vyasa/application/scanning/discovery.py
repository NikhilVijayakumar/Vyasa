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
    MAX_WARNING_EXAMPLES,
    OUTCOMES,
    PARTIAL,
    SKIP_ADVICE,
    SKIPPED_BY_POLICY,
    Candidate,
    DiscoveryOptions,
    DiscoveryRun,
    ScanWarning,
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
        skips: tuple[Candidate, ...] = ()
        ignore_warning = None
    else:
        findings = find_repositories(root, options)
        repositories = tuple(sorted(findings.repositories, key=_order))
        issues = tuple(c for c in findings.issues if c.outcome != SKIPPED_BY_POLICY)
        skips = tuple(c for c in findings.issues if c.outcome == SKIPPED_BY_POLICY)
        excluded = findings.excluded
        ignore_warning = _ignore_warning(findings.ignore_problems, root)
        # Only failures change the status; policy skips are warnings the person acts on.
        status = PARTIAL if issues else COMPLETE

    counted = Counter(issue.outcome for issue in (*issues, *skips))
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
        warnings=_warnings(skips, ignore_warning),
    )


def _warnings(skips: tuple[Candidate, ...], ignore_warning: ScanWarning | None) -> tuple[ScanWarning, ...]:
    """One warning per reason, counting every skipped directory and keeping a few examples."""
    by_reason: dict[str, list[Path]] = {}
    for skipped in skips:
        by_reason.setdefault(skipped.reason or "unknown", []).append(skipped.path)
    warnings = [
        ScanWarning(
            reason=reason,
            count=len(paths),
            examples=tuple(paths[:MAX_WARNING_EXAMPLES]),
            advice=SKIP_ADVICE.get(reason, "Review these directories."),
        )
        for reason, paths in by_reason.items()
    ]
    if ignore_warning is not None:
        warnings.append(ignore_warning)
    return tuple(sorted(warnings, key=lambda warning: warning.reason))


def _ignore_warning(problems: tuple[tuple[Path, str], ...], root: Path) -> ScanWarning | None:
    """Mistakes in repositories' ignore files: they never change the status, and valid lines still apply."""
    if not problems:
        return None
    files: list[Path] = []
    for directory, _ in problems:
        if directory not in files:
            files.append(directory)

    def where(directory: Path) -> str:
        relative = directory.relative_to(root).as_posix()
        return f"{relative}/.vyasaignore" if relative != "." else ".vyasaignore"

    return ScanWarning(
        reason="ignore_file",
        count=len(problems),
        examples=tuple(files[:MAX_WARNING_EXAMPLES]),
        advice=SKIP_ADVICE["ignore_file"],
        details=tuple(f"{where(d)}: {message}" for d, message in problems[:MAX_WARNING_EXAMPLES]),
    )
