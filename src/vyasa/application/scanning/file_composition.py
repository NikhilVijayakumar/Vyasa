"""Count code, documentation, and other files of one checkout."""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Iterable
from pathlib import Path

from vyasa.application.scanning.checkout_scan import scan_checkout
from vyasa.domain.file_composition import (
    DEFAULT_EXCLUSIONS,
    FileComposition,
    FileTypeDataError,
    FileTypes,
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


def _labels(data: dict, field: str, source: str) -> dict[str, str]:
    values = data.get(field, {})
    if not isinstance(values, dict):
        raise FileTypeDataError(f"{source}: '{field}' must be an object")
    found = {}
    for key, label in values.items():
        if not isinstance(label, str) or not label.strip():
            raise FileTypeDataError(f"{source}: '{field}' has an invalid label for {key!r}")
        found[key.casefold()] = label
    return found


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
    languages = _labels(data, "languages", source)
    manifests = _labels(data, "manifests", source)
    if languages and set(languages) != code:
        raise FileTypeDataError(f"{source}: 'languages' differs from 'code_extensions' at {sorted(set(languages) ^ code)[0]!r}")
    return FileTypes(version, code, documentation, languages, manifests)


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
    return scan_checkout(root, types, limits, exclusions, clock).composition
