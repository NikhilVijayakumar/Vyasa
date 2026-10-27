"""Project markers: README, documentation, agent instructions, OpenSpec, and tests, found from names only.

Everything here works on repository-relative POSIX paths. Nothing touches the filesystem and no file is read.
"""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatchcase

README = "readme"
DOCS = "docs"
AGENT_INSTRUCTIONS = "agent_instructions"
OPENSPEC_DIRECTORY = "openspec_directory"
OPENSPEC_CONFIG = "openspec_config"
OPENSPEC_SPECS = "openspec_specs"
OPENSPEC_CHANGES = "openspec_changes"
TESTS = "tests"
MARKERS = (README, DOCS, AGENT_INSTRUCTIONS, OPENSPEC_DIRECTORY, OPENSPEC_CONFIG, OPENSPEC_SPECS, OPENSPEC_CHANGES, TESTS)

MAX_PATHS = 20
ROOT_SCOPE = "root"


class MarkerRulesError(ValueError):
    """The marker rules data is unreadable or malformed."""


@dataclass(frozen=True)
class MarkerRules:
    """Versioned names. Fixed names and directories are stored lower-cased; file patterns keep their case."""

    version: int
    readme_names: frozenset[str]
    docs_directories: frozenset[str]
    agent_files: frozenset[str]
    openspec_directory: str
    openspec_config: frozenset[str]
    openspec_specs: str
    openspec_changes: str
    test_directories: frozenset[str]
    test_patterns: tuple[str, ...]


@dataclass(frozen=True)
class MarkerFound:
    """One detected marker: the total matches, the rules that matched, and at most ``MAX_PATHS`` (path, scope) pairs."""

    marker: str
    total: int
    rules: tuple[str, ...]
    paths: tuple[tuple[str, str | None], ...]


@dataclass(frozen=True)
class MarkerReport:
    """The markers found in one walk. ``stopped_by`` is None for a complete walk."""

    found: tuple[MarkerFound, ...]
    rules_version: int
    stopped_by: str | None

    @property
    def complete(self) -> bool:
        return self.stopped_by is None


def _split(path: str) -> tuple[str, str]:
    parent, _, name = path.rpartition("/")
    return parent, name


def markers_of(
    files: tuple[str, ...] | list[str],
    directories: tuple[str, ...] | list[str],
    rules: MarkerRules,
    stopped_by: str | None = None,
) -> MarkerReport:
    """Detect the markers among relative file and directory paths."""
    hits: dict[str, dict[str, set[tuple[str, str | None]]]] = {}

    def add(marker: str, rule: str, path: str, scope: str | None = None) -> None:
        hits.setdefault(marker, {}).setdefault(rule, set()).add((path, scope))

    for path in files:
        parent, name = _split(path)
        folded = name.casefold()
        if not parent and folded in rules.readme_names:
            add(README, "readme_file", path)
        if folded in rules.agent_files:
            add(AGENT_INSTRUCTIONS, "agent_file", path, parent or ROOT_SCOPE)
        if parent.casefold() == rules.openspec_directory and folded in rules.openspec_config:
            add(OPENSPEC_CONFIG, "openspec_config_file", path)
        for pattern in rules.test_patterns:
            if fnmatchcase(name, pattern):
                add(TESTS, f"file_pattern:{pattern}", path)
    for path in directories:
        parent, name = _split(path)
        folded = name.casefold()
        if not parent and folded in rules.docs_directories:
            add(DOCS, "docs_directory", path)
        if not parent and folded == rules.openspec_directory:
            add(OPENSPEC_DIRECTORY, "openspec_directory", path)
        if folded in rules.test_directories:
            add(TESTS, "test_directory", path)
    # specs and changes are entries (files or directories) directly inside the OpenSpec directory
    for path in (*files, *directories):
        parent, name = _split(path)
        if parent.casefold() == rules.openspec_directory:
            if name.casefold() == rules.openspec_specs:
                add(OPENSPEC_SPECS, "openspec_specs_entry", path)
            if name.casefold() == rules.openspec_changes:
                add(OPENSPEC_CHANGES, "openspec_changes_entry", path)

    found = []
    for marker in MARKERS:
        by_rule = hits.get(marker)
        if not by_rule:
            continue
        everything = sorted({hit for matches in by_rule.values() for hit in matches}, key=lambda h: (h[0], h[1] or ""))
        found.append(MarkerFound(marker, len(everything), tuple(sorted(by_rule)), tuple(everything[:MAX_PATHS])))
    return MarkerReport(tuple(found), rules.version, stopped_by)
