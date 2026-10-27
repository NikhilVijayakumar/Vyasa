"""Repository discovery: candidates, outcomes, and the run record. Nothing here touches the filesystem."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

ELIGIBLE = "eligible"
EXCLUDED = "excluded"
INACCESSIBLE = "inaccessible"
MALFORMED = "malformed"
SKIPPED_BY_POLICY = "skipped_by_policy"
OUTCOMES = (ELIGIBLE, EXCLUDED, INACCESSIBLE, MALFORMED, SKIPPED_BY_POLICY)

KIND_REPOSITORY = "repository"
KIND_SUBMODULE = "submodule"
KIND_LINKED_WORKTREE = "linked_worktree"

COMPLETE = "complete"
PARTIAL = "partial"
FAILED = "failed"

DISCOVERY_EXCLUSIONS: frozenset[str] = frozenset(
    {
        ".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", "target",
        ".tox", ".idea", ".vscode", ".cache", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    }
)


@dataclass(frozen=True)
class DiscoveryOptions:
    """Bounds for one discovery. See the repository recognition decision."""

    max_depth: int = 8
    exclusions: frozenset[str] = DISCOVERY_EXCLUSIONS
    max_issues: int = 100


@dataclass(frozen=True)
class Candidate:
    """One thing discovery looked at. ``reason`` is set for every outcome except eligible."""

    path: Path
    outcome: str
    kind: str | None = None
    reason: str | None = None


MAX_WARNING_EXAMPLES = 5

SKIP_ADVICE: dict[str, str] = {
    "max_depth": "Directories below the depth limit were not searched. If they hold nothing to scan, "
    "list them in the repository's .vyasaignore; otherwise raise max_depth.",
    "symlink": "Directory links are not followed. If the target should be scanned, "
    "add its real location as a workspace root.",
    "git_link": "A .git entry that is a link is not followed. Replace it with a real .git directory or file.",
}


@dataclass(frozen=True)
class ScanWarning:
    """Directories skipped by policy for one reason, with a few examples and what to do about it."""

    reason: str
    count: int
    examples: tuple[Path, ...]
    advice: str


@dataclass(frozen=True)
class DiscoveryRun:
    """What one discovery did. Contains absolute local paths: local state only."""

    run_id: str
    root: Path
    started_at: datetime
    finished_at: datetime
    status: str
    tool_version: str
    options: DiscoveryOptions
    counts: Mapping[str, int]
    repositories: tuple[Candidate, ...]
    issues: tuple[Candidate, ...]
    issues_omitted: int = field(default=0)
    warnings: tuple[ScanWarning, ...] = ()
