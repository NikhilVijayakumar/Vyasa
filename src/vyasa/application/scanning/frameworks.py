"""The technology registry and the technologies a set of parsed manifests declares."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from vyasa.domain.frameworks import (
    ECOSYSTEMS,
    KEY,
    PARSED,
    ManifestResult,
    RegistryError,
    TechnologyEntry,
    TechnologyFound,
    TechnologyRegistry,
    normalize,
)


def _text(value: object, field: str, source: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{source}: '{field}' must be a non-empty string")
    return value


def load_registry(path: Path | str) -> TechnologyRegistry:
    """Load and validate the technology registry."""
    source = str(path)
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise RegistryError(f"{source}: cannot be read as JSON ({error})") from error
    if not isinstance(data, dict):
        raise RegistryError(f"{source}: must be a JSON object")
    version = data.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise RegistryError(f"{source}: 'version' must be an integer of at least 1")
    listed = data.get("technologies")
    if not isinstance(listed, list):
        raise RegistryError(f"{source}: 'technologies' must be a list")
    entries: list[TechnologyEntry] = []
    keys: set[str] = set()
    claimed: dict[tuple[str, str], str] = {}
    for item in listed:
        if not isinstance(item, dict):
            raise RegistryError(f"{source}: each technology must be an object")
        key = _text(item.get("key"), "key", source)
        if not KEY.match(key):
            raise RegistryError(f"{source}: invalid key {key!r}")
        if key in keys:
            raise RegistryError(f"{source}: duplicate key {key!r}")
        keys.add(key)
        ecosystem = item.get("ecosystem")
        if not isinstance(ecosystem, str) or ecosystem not in ECOSYSTEMS:
            raise RegistryError(f"{source}: {key!r} has an unknown ecosystem {ecosystem!r}")
        dependencies = item.get("dependencies")
        if not isinstance(dependencies, list) or not dependencies or not all(isinstance(d, str) and d for d in dependencies):
            raise RegistryError(f"{source}: {key!r} needs a non-empty list of 'dependencies'")
        names = frozenset(normalize(ecosystem, d) for d in dependencies)
        for name in names:
            if (ecosystem, name) in claimed:
                raise RegistryError(f"{source}: dependency {name!r} is claimed by {claimed[(ecosystem, name)]!r} and {key!r}")
            claimed[(ecosystem, name)] = key
        entries.append(TechnologyEntry(
            key, _text(item.get("name"), "name", source), _text(item.get("category"), "category", source), ecosystem, names))
    ubiquitous = data.get("ubiquitous", [])
    if not isinstance(ubiquitous, list) or not all(isinstance(k, str) and k in keys for k in ubiquitous):
        raise RegistryError(f"{source}: 'ubiquitous' must list keys that exist")
    return TechnologyRegistry(version, tuple(entries), frozenset(ubiquitous))


def default_registry() -> TechnologyRegistry:
    """The registry shipped with the package."""
    return load_registry(Path(__file__).resolve().parents[2] / "data" / "technologies.json")


def technologies_of(manifests: tuple[ManifestResult, ...], registry: TechnologyRegistry) -> tuple[TechnologyFound, ...]:
    """Technologies declared by parsed manifests: one per key, with the scopes and manifests that declared it."""
    scopes: dict[str, set[str]] = defaultdict(set)
    sources: dict[str, set[str]] = defaultdict(set)
    for manifest in manifests:
        if manifest.status != PARSED:
            continue
        for dependency in manifest.dependencies:
            key = registry.key_for(manifest.ecosystem, dependency.name)
            if key:
                scopes[key].add(dependency.scope)
                sources[key].add(manifest.path)
    return tuple(TechnologyFound(k, tuple(sorted(scopes[k])), tuple(sorted(sources[k]))) for k in sorted(scopes))
