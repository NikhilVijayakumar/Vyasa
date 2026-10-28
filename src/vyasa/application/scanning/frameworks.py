"""The technology registry and the technologies a set of parsed manifests declares."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path

from vyasa.adapters.filesystem.manifest_reader import READ, ManifestRead, read_manifest

from vyasa.domain.frameworks import (
    ECOSYSTEMS,
    KEY,
    MANIFEST_LIMIT,
    MAX_DEPENDENCIES,
    MALFORMED,
    PARSED,
    UNREADABLE,
    FrameworkReport,
    ManifestParseError,
    ManifestResult,
    RegistryError,
    TechnologyEntry,
    TechnologyFound,
    TechnologyRegistry,
    normalize,
)
from vyasa.domain.manifests import ecosystem_of, parse_manifest


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


def _manifest(root: Path | str, name: str, ecosystem: str, limit: int, reader: Callable[..., ManifestRead]) -> ManifestResult:
    """Read and parse one root manifest. Whatever goes wrong becomes a status with a fixed reason; no text is kept."""
    try:
        read = reader(root, name, limit)
    except Exception:  # one unreadable file must not stop the others
        return ManifestResult(name, ecosystem, UNREADABLE, "io", (), 0, 0, False)
    if read.status != READ or read.text is None:
        return ManifestResult(name, ecosystem, read.status, read.reason, (), 0, 0, False)
    try:
        parsed = parse_manifest(name, read.text)
    except ManifestParseError as error:
        return ManifestResult(name, ecosystem, MALFORMED, error.reason, (), 0, 0, False)
    except Exception:
        return ManifestResult(name, ecosystem, MALFORMED, "structure", (), 0, 0, False)
    dependencies = tuple(sorted(parsed.dependencies, key=lambda d: (d.name, d.scope)))
    return ManifestResult(name, ecosystem, PARSED, None, dependencies, len(dependencies), parsed.skipped, parsed.workspace, parsed.declared_name)


def detect_frameworks(
    root: Path | str,
    files: Iterable[str],
    stopped_by: str | None,
    registry: TechnologyRegistry,
    limit: int = MANIFEST_LIMIT,
    reader: Callable[..., ManifestRead] = read_manifest,
) -> FrameworkReport:
    """Technologies declared by the supported manifests among the walk's relative file paths.

    Only files directly in the checkout root are read; supported names below it are counted and left alone.
    """
    root_names: list[tuple[str, str]] = []
    nested: Counter[str] = Counter()
    for path in files:
        parent, _, name = path.rpartition("/")
        ecosystem = ecosystem_of(name)
        if ecosystem is None:
            continue
        if parent:
            nested[ecosystem] += 1
        else:
            root_names.append((name, ecosystem))
    results = tuple(_manifest(root, name, ecosystem, limit, reader) for name, ecosystem in sorted(root_names))
    technologies = technologies_of(results, registry)  # from every dependency, before the storage cap
    capped = tuple(
        ManifestResult(m.path, m.ecosystem, m.status, m.reason, m.dependencies[:MAX_DEPENDENCIES], m.total_dependencies, m.skipped, m.workspace, m.declared_name)
        for m in results
    )
    return FrameworkReport(capped, tuple(sorted(nested.items())), technologies, registry.version, stopped_by)
