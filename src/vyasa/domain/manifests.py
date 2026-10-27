"""Pure parsers for the supported manifests. They receive text and return dependencies; nothing is evaluated.

Parsers use the standard library (`tomllib`, `json`) or small anchored regular expressions on bounded lines.
Every failure is a ``ManifestParseError`` with a fixed reason; no file text appears in an error.
"""

from __future__ import annotations

import json
import re
import tomllib
from collections.abc import Callable
from fnmatch import fnmatchcase

from vyasa.domain.frameworks import (
    BUILD,
    DEV,
    GO,
    JAVASCRIPT,
    OPTIONAL,
    PYTHON,
    RUNTIME,
    RUST,
    Dependency,
    ManifestParseError,
    ParsedManifest,
    normalize,
)

MAX_LINE = 1000
_REQUIREMENT = re.compile(r"^\s*([A-Za-z0-9](?:[A-Za-z0-9._-]{0,212}[A-Za-z0-9])?)\s*(?:\[[^\]]{0,200}\])?\s*(.*)$")
_COMMENT = re.compile(r"\s#.*$")
_GO_REQUIRE = re.compile(r"^(\S+)\s+(v\S+)\s*(//.*)?$")


def ecosystem_of(name: str) -> str | None:
    """The ecosystem a root file name belongs to, or None."""
    folded = name.casefold()
    if folded == "pyproject.toml" or fnmatchcase(folded, "requirements*.txt"):
        return PYTHON
    return {"package.json": JAVASCRIPT, "cargo.toml": RUST, "go.mod": GO}.get(folded)


def _requirement(text: str, scope: str) -> Dependency | None:
    """A PEP 508 style requirement. A direct reference keeps no URL, because URLs can carry credentials."""
    if len(text) > MAX_LINE:
        return None
    match = _REQUIREMENT.match(text)
    if not match:
        return None
    rest = match.group(2).split(";", 1)[0].strip().strip("()").strip()
    if rest.startswith("@"):
        constraint: str | None = "direct reference"
    else:
        constraint = rest or None
    return Dependency(normalize(PYTHON, match.group(1)), constraint, scope)


def _table(value: object) -> dict:
    if not isinstance(value, dict):
        raise ManifestParseError("structure")
    return value


def _loads_toml(text: str) -> dict:
    try:
        return tomllib.loads(text)
    except RecursionError as error:
        raise ManifestParseError("too_deep") from error
    except (tomllib.TOMLDecodeError, ValueError) as error:
        raise ManifestParseError("syntax") from error


def _loads_json(text: str) -> object:
    try:
        return json.loads(text)
    except RecursionError as error:
        raise ManifestParseError("too_deep") from error
    except ValueError as error:
        raise ManifestParseError("syntax") from error


def _requirement_list(values: object, scope: str, found: list[Dependency]) -> int:
    """Add requirement strings; return how many entries could not be recorded."""
    if not isinstance(values, list):
        raise ManifestParseError("structure")
    skipped = 0
    for value in values:
        dependency = _requirement(value, scope) if isinstance(value, str) else None
        if dependency is None:
            skipped += 1
        else:
            found.append(dependency)
    return skipped


def _poetry_table(table: object, scope: str, found: list[Dependency]) -> None:
    for name, spec in _table(table).items():
        if normalize(PYTHON, name) == "python":
            continue
        constraint = spec if isinstance(spec, str) else spec.get("version") if isinstance(spec, dict) else None
        found.append(Dependency(normalize(PYTHON, name), constraint if isinstance(constraint, str) else None, scope))


def _pyproject(text: str, _name: str) -> ParsedManifest:
    data = _loads_toml(text)
    found: list[Dependency] = []
    skipped = 0
    if "project" in data:
        project = _table(data["project"])
        if "dependencies" in project:
            skipped += _requirement_list(project["dependencies"], RUNTIME, found)
        for group in _table(project.get("optional-dependencies", {})).values():
            skipped += _requirement_list(group, OPTIONAL, found)
    for group in _table(data.get("dependency-groups", {})).values():
        skipped += _requirement_list(group, DEV, found)
    if "build-system" in data:
        skipped += _requirement_list(_table(data["build-system"]).get("requires", []), BUILD, found)
    poetry = _table(_table(data.get("tool", {})).get("poetry", {}))
    if "dependencies" in poetry:
        _poetry_table(poetry["dependencies"], RUNTIME, found)
    if "dev-dependencies" in poetry:
        _poetry_table(poetry["dev-dependencies"], DEV, found)
    for group in _table(poetry.get("group", {})).values():
        _poetry_table(_table(group).get("dependencies", {}), DEV, found)
    return ParsedManifest(tuple(found), skipped)


def _requirements(text: str, name: str) -> ParsedManifest:
    folded = name.casefold()
    scope = DEV if "dev" in folded or "test" in folded else RUNTIME
    found: list[Dependency] = []
    skipped = 0
    for raw in text.splitlines():
        line = _COMMENT.sub("", raw).strip()
        if not line or line.startswith("#"):
            continue
        dependency = None
        if not line.startswith("-") and "://" not in line.split(None, 1)[0] and not line.startswith(("git+", "hg+", "svn+", "bzr+")):
            dependency = _requirement(line, scope)
        if dependency is None:
            skipped += 1
        else:
            found.append(dependency)
    return ParsedManifest(tuple(found), skipped)


_PACKAGE_SECTIONS = (("dependencies", RUNTIME), ("devDependencies", DEV), ("optionalDependencies", OPTIONAL), ("peerDependencies", OPTIONAL))


def _package_json(text: str, _name: str) -> ParsedManifest:
    data = _loads_json(text)
    if not isinstance(data, dict):
        raise ManifestParseError("structure")
    found: list[Dependency] = []
    for section, scope in _PACKAGE_SECTIONS:
        if section not in data:
            continue
        for name, constraint in _table(data[section]).items():
            found.append(Dependency(str(name), constraint if isinstance(constraint, str) else None, scope))
    return ParsedManifest(tuple(found), 0, "workspaces" in data)


_CARGO_SECTIONS = (("dependencies", RUNTIME), ("dev-dependencies", DEV), ("build-dependencies", BUILD))


def _cargo(text: str, _name: str) -> ParsedManifest:
    data = _loads_toml(text)
    found: list[Dependency] = []
    for section, scope in _CARGO_SECTIONS:
        if section not in data:
            continue
        for name, spec in _table(data[section]).items():
            if isinstance(spec, dict):
                real = spec.get("package") if isinstance(spec.get("package"), str) else name
                constraint = spec.get("version") if isinstance(spec.get("version"), str) else None
            else:
                real, constraint = name, spec if isinstance(spec, str) else None
            found.append(Dependency(real, constraint, scope))
    skipped = 0
    for platform in _table(data.get("target", {})).values():
        for section, _scope in _CARGO_SECTIONS:
            skipped += len(_table(_table(platform).get(section, {})))
    return ParsedManifest(tuple(found), skipped, "workspace" in data)


def _go_mod(text: str, _name: str) -> ParsedManifest:
    found: list[Dependency] = []
    skipped = 0
    in_block = False
    for raw in text.splitlines():
        line = raw.strip()
        if len(line) > MAX_LINE or not line or line.startswith("//"):
            continue
        if in_block:
            if line.startswith(")"):
                in_block = False
                continue
        elif line.startswith("require"):
            rest = line[len("require"):].strip()
            if rest == "(":
                in_block = True
                continue
            line = rest
        else:
            continue
        match = _GO_REQUIRE.match(line)
        if not match:
            continue
        if match.group(3) and "indirect" in match.group(3):
            skipped += 1
        else:
            found.append(Dependency(match.group(1), match.group(2), RUNTIME))
    return ParsedManifest(tuple(found), skipped)


_PARSERS: dict[str, Callable[[str, str], ParsedManifest]] = {
    "pyproject.toml": _pyproject, "package.json": _package_json, "cargo.toml": _cargo, "go.mod": _go_mod,
}


def parse_manifest(name: str, text: str) -> ParsedManifest:
    """Parse one supported root manifest. Raises ``ManifestParseError`` with a fixed reason."""
    folded = name.casefold()
    parser = _PARSERS.get(folded) or (_requirements if ecosystem_of(name) == PYTHON else None)
    if parser is None:
        raise ManifestParseError("structure")
    return parser(text, name)
