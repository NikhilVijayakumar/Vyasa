"""Count code, documentation, and other files of one checkout."""

from __future__ import annotations

import json
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
    FileTypeDataError,
    FileTypes,
    IgnoreEvidence,
    WalkLimits,
)


def _extensions(data: dict, field: str, source: str) -> frozenset[str]:
    values = data.get(field)
    if not isinstance(values, list):
        raise FileTypeDataError(f"{source}: '{field}' must be a list")
    found = set()
    for value in values:
        if not isinstance(value, str) or len(value) < 2 or not value.startswith("."):
            raise FileTypeDataError(f"{source}: '{field}' has an invalid extension {value!r}")
        found.add(value.casefold())
    return frozenset(found)


def load_file_types(path: Path | str) -> FileTypes:
    """Load and validate file-type data."""
    source = str(path)
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise FileTypeDataError(f"{source}: cannot be read as JSON ({error})") from error
    if not isinstance(data, dict):
        raise FileTypeDataError(f"{source}: must be a JSON object")
    version = data.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise FileTypeDataError(f"{source}: 'version' must be an integer of at least 1")
    code = _extensions(data, "code_extensions", source)
    documentation = _extensions(data, "documentation_extensions", source)
    overlap = sorted(code & documentation)
    if overlap:
        raise FileTypeDataError(f"{source}: extension {overlap[0]!r} is in both lists")
    return FileTypes(version=version, code_extensions=code, documentation_extensions=documentation)


def default_file_types() -> FileTypes:
    """The file-type data shipped with the package."""
    return load_file_types(Path(__file__).resolve().parents[2] / "data" / "file_types.json")


def compose(
    root: Path | str,
    types: FileTypes,
    limits: WalkLimits = WalkLimits(),
    exclusions: Iterable[str] = DEFAULT_EXCLUSIONS,
    clock: Callable[[], float] = time.monotonic,
) -> FileComposition:
    """Count the files under ``root`` by category. Raises ValueError if ``root`` is not a directory."""
    if not Path(root).is_dir():
        raise ValueError(f"not a directory: {root}")
    exclusions = frozenset(exclusions)
    ignore, _problems = read_ignore_file(os.fspath(root))
    walked = walk_checkout(root, limits, exclusions, clock, ignore)
    counts = Counter(types.classify(name) for name in walked.names)
    return FileComposition(
        code=counts[CODE],
        documentation=counts[DOCUMENTATION],
        other=counts[OTHER],
        stopped_by=walked.stopped_by,
        evidence=Evidence(
            types_version=types.version,
            exclusions=tuple(sorted(exclusions)),
            limits=limits,
            ignore=None if ignore is None else IgnoreEvidence(len(ignore.patterns), ignore.digest),
        ),
    )
