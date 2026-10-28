"""Frameworks and technologies declared by a checkout's root manifests.

Everything here is plain data. Nothing touches the filesystem and no repository text is kept: only names,
declared constraints, scopes, counts, statuses, and fixed reason codes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PYTHON, JAVASCRIPT, RUST, GO = "python", "javascript", "rust", "go"
ECOSYSTEMS = (PYTHON, JAVASCRIPT, RUST, GO)

RUNTIME, DEV, OPTIONAL, BUILD = "runtime", "dev", "optional", "build"
SCOPES = (RUNTIME, DEV, OPTIONAL, BUILD)

PARSED, MALFORMED, TOO_LARGE, UNREADABLE = "parsed", "malformed", "too_large", "unreadable"
STATUSES = (PARSED, MALFORMED, TOO_LARGE, UNREADABLE)

MAX_DEPENDENCIES = 200
MANIFEST_LIMIT = 1024 * 1024  # bytes read from one manifest
KEY = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class RegistryError(ValueError):
    """The technology registry data is unreadable or malformed."""


class ManifestParseError(ValueError):
    """A manifest could not be parsed. ``reason`` is a fixed code; the message never contains file text."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True)
class Dependency:
    name: str
    constraint: str | None
    scope: str


@dataclass(frozen=True)
class ParsedManifest:
    """What a parser found: every direct dependency, how many entries it skipped, and a workspace flag."""

    dependencies: tuple[Dependency, ...]
    skipped: int = 0
    workspace: bool = False
    declared_name: str | None = None  # the package name the manifest declares, normalized; None when it declares none


@dataclass(frozen=True)
class ManifestResult:
    """One root manifest. ``dependencies`` holds at most ``MAX_DEPENDENCIES``; ``total_dependencies`` is the real count."""

    path: str
    ecosystem: str
    status: str
    reason: str | None
    dependencies: tuple[Dependency, ...]
    total_dependencies: int
    skipped: int
    workspace: bool
    declared_name: str | None = None


@dataclass(frozen=True)
class TechnologyEntry:
    key: str
    name: str
    category: str
    ecosystem: str
    dependencies: frozenset[str]


def normalize(ecosystem: str, name: str) -> str:
    """The form a dependency name is matched in: PEP 503 for Python, lower case otherwise."""
    if ecosystem == PYTHON:
        return re.sub(r"[-_.]+", "-", name).lower()
    return name.lower()


@dataclass(frozen=True)
class TechnologyRegistry:
    """Versioned map from (ecosystem, dependency name) to technology."""

    version: int
    entries: tuple[TechnologyEntry, ...]
    ubiquitous: frozenset[str]

    def keys(self) -> tuple[str, ...]:
        return tuple(sorted(e.key for e in self.entries))

    def entry(self, key: str) -> TechnologyEntry | None:
        return next((e for e in self.entries if e.key == key), None)

    def key_for(self, ecosystem: str, name: str) -> str | None:
        wanted = normalize(ecosystem, name)
        for e in self.entries:
            if e.ecosystem == ecosystem and wanted in e.dependencies:
                return e.key
        return None


@dataclass(frozen=True)
class TechnologyFound:
    """A technology a checkout declares: the scopes it was declared in and the manifests that declared it."""

    key: str
    scopes: tuple[str, ...]
    manifests: tuple[str, ...]


@dataclass(frozen=True)
class FrameworkReport:
    """Everything one scan learned from the root manifests. ``stopped_by`` is None for a complete walk."""

    manifests: tuple[ManifestResult, ...]
    nested: tuple[tuple[str, int], ...]
    technologies: tuple[TechnologyFound, ...]
    registry_version: int
    stopped_by: str | None

    @property
    def complete(self) -> bool:
        return self.stopped_by is None
