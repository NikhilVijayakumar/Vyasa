"""Load the versioned marker rules."""

from __future__ import annotations

import json
from pathlib import Path

from vyasa.domain.markers import MarkerRules, MarkerRulesError


def _name(value: object, field: str, source: str) -> str:
    if not isinstance(value, str) or not value or "/" in value or "\\" in value:
        raise MarkerRulesError(f"{source}: '{field}' has an invalid name {value!r}")
    return value


def _names(group: dict, key: str, field: str, source: str) -> list[str]:
    values = group.get(key)
    if not isinstance(values, list) or not values:
        raise MarkerRulesError(f"{source}: '{field}' must be a non-empty list")
    return [_name(v, field, source) for v in values]


def _group(data: dict, key: str, source: str) -> dict:
    group = data.get(key)
    if not isinstance(group, dict):
        raise MarkerRulesError(f"{source}: '{key}' must be an object")
    return group


def load_marker_rules(path: Path | str) -> MarkerRules:
    """Load and validate marker rules."""
    source = str(path)
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise MarkerRulesError(f"{source}: cannot be read as JSON ({error})") from error
    if not isinstance(data, dict):
        raise MarkerRulesError(f"{source}: must be a JSON object")
    version = data.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise MarkerRulesError(f"{source}: 'version' must be an integer of at least 1")
    readme, docs = _group(data, "readme", source), _group(data, "docs", source)
    agents, openspec = _group(data, "agent_instructions", source), _group(data, "openspec", source)
    tests = _group(data, "tests", source)
    return MarkerRules(
        version=version,
        readme_names=frozenset(n.casefold() for n in _names(readme, "names", "readme.names", source)),
        docs_directories=frozenset(n.casefold() for n in _names(docs, "directories", "docs.directories", source)),
        agent_files=frozenset(n.casefold() for n in _names(agents, "files", "agent_instructions.files", source)),
        openspec_directory=_name(openspec.get("directory"), "openspec.directory", source).casefold(),
        openspec_config=frozenset(n.casefold() for n in _names(openspec, "config", "openspec.config", source)),
        openspec_specs=_name(openspec.get("specs"), "openspec.specs", source).casefold(),
        openspec_changes=_name(openspec.get("changes"), "openspec.changes", source).casefold(),
        test_directories=frozenset(n.casefold() for n in _names(tests, "directories", "tests.directories", source)),
        test_patterns=tuple(_names(tests, "file_patterns", "tests.file_patterns", source)),
    )


def default_marker_rules() -> MarkerRules:
    """The marker rules shipped with the package."""
    return load_marker_rules(Path(__file__).resolve().parents[2] / "data" / "markers.json")
