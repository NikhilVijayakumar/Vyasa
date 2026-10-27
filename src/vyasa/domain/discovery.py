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
KIND_PROJECT = "project"  # recognized by a manifest, with Git elsewhere or not at all
KIND_DOCUMENTATION = "documentation"  # a README and a docs folder, nothing else yet

COMPLETE = "complete"
PARTIAL = "partial"
FAILED = "failed"

DISCOVERY_EXCLUSIONS: frozenset[str] = frozenset(
    {
        ".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist", "target",
        ".tox", ".idea", ".vscode", ".cache", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    }
)


# A directory holding one of these files is a project even without Git. Names compare case-insensitively.
DISCOVERY_MARKERS: frozenset[str] = frozenset(
    {"pyproject.toml", "requirements.txt", "setup.py", "package.json", "cargo.toml", "go.mod"}
)
DISCOVERY_MARKER_SUFFIXES: tuple[str, ...] = (".uproject",)

# A README together with one of these directories marks a project that has not started yet.
DOCUMENTATION_DIRS: frozenset[str] = frozenset({"docs", "doc", "documentation"})


@dataclass(frozen=True)
class DiscoveryOptions:
    """Bounds for one discovery. See the repository recognition decision."""

    max_depth: int = 8
    exclusions: frozenset[str] = DISCOVERY_EXCLUSIONS
    max_issues: int = 100
    markers: frozenset[str] = DISCOVERY_MARKERS
    marker_suffixes: tuple[str, ...] = DISCOVERY_MARKER_SUFFIXES
    descend_into_repositories: bool = False


@dataclass(frozen=True)
class Candidate:
    """One thing discovery looked at. ``reason`` is set for every outcome except eligible.

    ``markers`` are the manifest files found in the project directory; ``git`` is where its Git
    entry is: ``"."`` for the directory itself, the name of a child directory (Unreal keeps it in
    ``Source``), or ``None``.
    """

    path: Path
    outcome: str
    kind: str | None = None
    reason: str | None = None
    markers: tuple[str, ...] = ()
    git: str | None = None


MAX_WARNING_EXAMPLES = 5

SKIP_ADVICE: dict[str, str] = {
    "max_depth": "Directories below the depth limit were not searched. If they hold nothing to scan, "
    "list them in the repository's .vyasaignore; otherwise raise max_depth.",
    "symlink": "Directory links are not followed. If the target should be scanned, "
    "add its real location as a workspace root.",
    "git_link": "A .git entry that is a link is not followed. Replace it with a real .git directory or file.",
    "ignore_file": "Fix or remove the listed lines in the repository's .vyasaignore. "
    "Invalid lines are skipped; valid lines still apply.",
}


@dataclass(frozen=True)
class ScanWarning:
    """Directories skipped by policy for one reason, with a few examples and what to do about it."""

    reason: str
    count: int
    examples: tuple[Path, ...]
    advice: str
    details: tuple[str, ...] = ()


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
