"""Detect the languages of one checkout."""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from pathlib import Path

from vyasa.application.scanning.checkout_scan import scan_checkout
from vyasa.domain.file_composition import DEFAULT_EXCLUSIONS, FileTypes, WalkLimits
from vyasa.domain.languages import LanguageReport


def detect_languages(
    root: Path | str,
    types: FileTypes,
    limits: WalkLimits = WalkLimits(),
    exclusions: Iterable[str] = DEFAULT_EXCLUSIONS,
    clock: Callable[[], float] = time.monotonic,
) -> LanguageReport:
    """Languages under ``root``. Raises ValueError if ``root`` is not a directory."""
    return scan_checkout(root, types, limits, exclusions, clock).languages
