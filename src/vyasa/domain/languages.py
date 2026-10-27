"""Languages of a checkout: found by file extension, or declared by a manifest file name.

The two statuses are kept apart (see the language evidence decision). Names only; nothing is read.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from vyasa.domain.file_composition import Evidence, FileTypes, extension


@dataclass(frozen=True)
class LanguageReport:
    """``files_detected`` is (label, count) pairs; ``declared`` is labels. Both sorted.

    ``stopped_by`` is None for a complete walk; otherwise results are lower bounds.
    """

    files_detected: tuple[tuple[str, int], ...]
    declared: tuple[str, ...]
    stopped_by: str | None
    evidence: Evidence

    @property
    def complete(self) -> bool:
        return self.stopped_by is None

    def is_absent(self, label: str) -> bool | None:
        """False when found either way; True when complete and not found; None when partial and not found."""
        if label in self.declared or any(found == label for found, _ in self.files_detected):
            return False
        return True if self.complete else None


def languages_of(names: Iterable[str], types: FileTypes) -> tuple[tuple[tuple[str, int], ...], tuple[str, ...]]:
    """Count language labels by extension and collect labels declared by manifest names."""
    counts: Counter[str] = Counter()
    declared: set[str] = set()
    for name in names:
        label = types.languages.get(extension(name))
        if label:
            counts[label] += 1
        label = types.manifests.get(name.casefold())
        if label:
            declared.add(label)
    return tuple(sorted(counts.items())), tuple(sorted(declared))
