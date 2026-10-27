"""Walk one checkout once and derive both the file counts and the languages from the same file names."""

from __future__ import annotations

import os
import time
from collections import Counter
from collections.abc import Callable, Iterable
from pathlib import Path

from vyasa.adapters.filesystem.checkout_walk import walk_checkout
from vyasa.adapters.filesystem.ignore_file import read_ignore_file
from vyasa.domain.file_composition import (
    CODE,
    DEFAULT_EXCLUSIONS,
    DOCUMENTATION,
    OTHER,
    Evidence,
    FileComposition,
    FileTypes,
    IgnoreEvidence,
    WalkLimits,
)
from vyasa.domain.languages import CheckoutScan, LanguageReport, languages_of
from vyasa.domain.markers import MarkerRules, markers_of


def scan_checkout(
    root: Path | str,
    types: FileTypes,
    limits: WalkLimits = WalkLimits(),
    exclusions: Iterable[str] = DEFAULT_EXCLUSIONS,
    clock: Callable[[], float] = time.monotonic,
    rules: MarkerRules | None = None,
) -> CheckoutScan:
    """Counts and languages under ``root``. Raises ValueError if ``root`` is not a directory."""
    if not Path(root).is_dir():
        raise ValueError(f"not a directory: {root}")
    exclusions = frozenset(exclusions)
    ignore, _problems = read_ignore_file(os.fspath(root))
    walked = walk_checkout(root, limits, exclusions, clock, ignore)
    evidence = Evidence(
        types_version=types.version,
        exclusions=tuple(sorted(exclusions)),
        limits=limits,
        ignore=None if ignore is None else IgnoreEvidence(len(ignore.patterns), ignore.digest),
    )
    counts = Counter(types.classify(name) for name in walked.names)
    found, declared = languages_of(walked.names, types)
    return CheckoutScan(
        composition=FileComposition(counts[CODE], counts[DOCUMENTATION], counts[OTHER], walked.stopped_by, evidence),
        languages=LanguageReport(found, declared, walked.stopped_by, evidence),
        markers=markers_of(walked.files, walked.directories, rules, walked.stopped_by) if rules else None,
    )
