"""File composition: how many files of a checkout are code, documentation, or other.

Classification looks at the file name only. Nothing here touches the filesystem.
"""

from __future__ import annotations

from dataclasses import dataclass

CODE = "code"
DOCUMENTATION = "documentation"
OTHER = "other"

DEFAULT_EXCLUSIONS: frozenset[str] = frozenset(
    {".git", "node_modules", ".venv", "venv", "__pycache__", "target", "build", "dist"}
)


class FileTypeDataError(ValueError):
    """The file-type data is unreadable or malformed."""


def extension(name: str) -> str:
    """Return the lower-cased extension of a file name, or '' when it has none.

    A leading dot alone (``.gitignore``) is not an extension.
    """
    dot = name.rfind(".")
    return name[dot:].casefold() if dot > 0 else ""


@dataclass(frozen=True)
class FileTypes:
    """Versioned extension lists. The two lists are disjoint."""

    version: int
    code_extensions: frozenset[str]
    documentation_extensions: frozenset[str]

    def classify(self, name: str) -> str:
        """Classify one file name as code, documentation, or other."""
        ext = extension(name)
        if ext in self.code_extensions:
            return CODE
        if ext in self.documentation_extensions:
            return DOCUMENTATION
        return OTHER


@dataclass(frozen=True)
class WalkLimits:
    """Bounds on one count. See the file composition decision for the defaults."""

    max_depth: int = 20
    max_entries: int = 50_000
    max_seconds: float = 60.0


@dataclass(frozen=True)
class Evidence:
    """How a count was made."""

    types_version: int
    exclusions: tuple[str, ...]
    limits: WalkLimits


@dataclass(frozen=True)
class FileComposition:
    """Counts for one checkout.

    ``stopped_by`` is None for a complete count; otherwise the counts are lower
    bounds and it names the first cause observed: ``depth``, ``entries``,
    ``time`` or ``unreadable``.
    """

    code: int
    documentation: int
    other: int
    stopped_by: str | None
    evidence: Evidence

    @property
    def total(self) -> int:
        return self.code + self.documentation + self.other

    @property
    def complete(self) -> bool:
        return self.stopped_by is None

    @property
    def documentation_only(self) -> bool | None:
        """True when documentation exists and code does not; unknown for a partial count."""
        if not self.complete:
            return None
        return self.documentation > 0 and self.code == 0
