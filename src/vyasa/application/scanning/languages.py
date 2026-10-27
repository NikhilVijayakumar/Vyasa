"""Detect the languages of one checkout."""

from __future__ import annotations

import os
import time
from collections.abc import Callable, Iterable
from pathlib import Path

from vyasa.adapters.filesystem.checkout_walk import walk_checkout
from vyasa.adapters.filesystem.ignore_file import read_ignore_file
from vyasa.domain.file_composition import DEFAULT_EXCLUSIONS, Evidence, FileTypes, IgnoreEvidence, WalkLimits
from vyasa.domain.languages import LanguageReport, languages_of


def detect_languages(
    root: Path | str,
    types: FileTypes,
    limits: WalkLimits = WalkLimits(),
    exclusions: Iterable[str] = DEFAULT_EXCLUSIONS,
    clock: Callable[[], float] = time.monotonic,
) -> LanguageReport:
    """Languages under ``root``. Raises ValueError if ``root`` is not a directory."""
    if not Path(root).is_dir():
        raise ValueError(f"not a directory: {root}")
    exclusions = frozenset(exclusions)
    ignore, _problems = read_ignore_file(os.fspath(root))
    walked = walk_checkout(root, limits, exclusions, clock, ignore)
    found, declared = languages_of(walked.names, types)
    return LanguageReport(
        files_detected=found,
        declared=declared,
        stopped_by=walked.stopped_by,
        evidence=Evidence(
            types_version=types.version,
            exclusions=tuple(sorted(exclusions)),
            limits=limits,
            ignore=None if ignore is None else IgnoreEvidence(len(ignore.patterns), ignore.digest),
        ),
    )
