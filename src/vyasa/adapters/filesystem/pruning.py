"""Which subdirectories a walk may enter.

``os.walk(followlinks=False)`` still descends into Windows junctions, so links and
junctions are filtered here. Both checks exist on every platform and are False
where the thing does not exist.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Pruned:
    kept: list[str]
    excluded: int
    linked: list[str]


def prune(dirpath: str, dirnames: Iterable[str], excluded: set[str]) -> Pruned:
    """Split ``dirnames`` into those to enter, an excluded count, and links not followed.

    ``excluded`` holds case-folded names. The result lists are sorted.
    """
    kept: list[str] = []
    linked: list[str] = []
    skipped = 0
    for name in sorted(dirnames):
        if name.casefold() in excluded:
            skipped += 1
            continue
        full = os.path.join(dirpath, name)
        if os.path.islink(full) or os.path.isjunction(full):
            linked.append(name)
            continue
        kept.append(name)
    return Pruned(kept=kept, excluded=skipped, linked=linked)
