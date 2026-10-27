"""Bounded, link-safe listing of the file names in one checkout.

Only directory and file names are read; no file is opened and no path is returned.
The behaviour is the same on every platform: ``os.path.isjunction`` is False off Windows.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from vyasa.domain.file_composition import WalkLimits


@dataclass(frozen=True)
class WalkResult:
    names: tuple[str, ...]
    stopped_by: str | None


def walk_checkout(
    root: Path | str,
    limits: WalkLimits,
    exclusions: Iterable[str],
    clock: Callable[[], float] = time.monotonic,
) -> WalkResult:
    """List file names under ``root`` within ``limits``.

    Directory symlinks and junctions are never entered. Directories whose name
    matches ``exclusions`` (case-insensitively) are skipped, except the root.
    Names are visited in sorted order so a partial result is repeatable.
    """
    top = os.fspath(root)
    excluded = {name.casefold() for name in exclusions}
    started = clock()
    names: list[str] = []
    entries = 0
    cause: str | None = None

    def first(reason: str) -> None:
        nonlocal cause
        if cause is None:
            cause = reason

    def unreadable(_error: OSError) -> None:
        first("unreadable")

    for dirpath, dirnames, filenames in os.walk(top, topdown=True, onerror=unreadable, followlinks=False):
        if clock() - started > limits.max_seconds:
            first("time")
            break

        kept = []
        for name in sorted(dirnames):
            full = os.path.join(dirpath, name)
            if name.casefold() in excluded or os.path.islink(full) or os.path.isjunction(full):
                continue
            kept.append(name)

        depth = len(Path(dirpath).relative_to(top).parts)
        if kept and depth >= limits.max_depth:
            first("depth")
            kept = []
        dirnames[:] = kept

        over = False
        for name in sorted(filenames):
            entries += 1
            if entries > limits.max_entries:
                over = True
                break
            names.append(name)
        entries += len(kept)
        if over or entries > limits.max_entries:
            first("entries")
            break

    return WalkResult(names=tuple(names), stopped_by=cause)
