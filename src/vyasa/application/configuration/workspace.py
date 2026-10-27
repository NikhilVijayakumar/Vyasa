"""Locate, read, validate, and check the workspace roots.

Environment, home directory, and platform are parameters that default to the running
process, so every platform layout can be exercised on any system.
"""

from __future__ import annotations

import os
import sys
import tomllib
from collections.abc import Mapping
from pathlib import Path

from vyasa.domain.workspace_config import (
    ACCESSIBLE,
    MISSING,
    NOT_A_DIRECTORY,
    UNREADABLE,
    ConfigError,
    NotConfigured,
    RootCheck,
    WorkspaceConfig,
)

CONFIG_FILE = "config.toml"
HOME_VARIABLE = "VYASA_HOME"
CONFIG_VARIABLE = "VYASA_CONFIG"


def data_directory(
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform: str | None = None,
) -> Path:
    """The directory holding Vyasa's per-user data."""
    environ = os.environ if environ is None else environ
    home = Path.home() if home is None else home
    platform = sys.platform if platform is None else platform
    override = environ.get(HOME_VARIABLE)
    if override:
        return Path(override)
    if platform.startswith("win"):
        return Path(environ.get("LOCALAPPDATA") or home / "AppData" / "Local") / "Vyasa"
    if platform == "darwin":
        return home / "Library" / "Application Support" / "Vyasa"
    return Path(environ.get("XDG_DATA_HOME") or home / ".local" / "share") / "vyasa"


def _locate(explicit: Path | str | None, environ: Mapping[str, str], home: Path, platform: str | None) -> tuple[Path, bool]:
    """Return the file to read and whether the user named it (so it must exist)."""
    if explicit is not None:
        return Path(explicit), True
    named = environ.get(CONFIG_VARIABLE)
    if named:
        return Path(named), True
    return data_directory(environ, home, platform) / CONFIG_FILE, False


def _expand_home(value: str, home: Path) -> str:
    if value == "~" or (value.startswith("~") and value[1] in "/\\"):
        return os.path.join(home, value[2:])
    return value


def _roots(raw: object, home: Path, source: Path, problems: list[str]) -> list[Path]:
    if not isinstance(raw, list):
        problems.append(f"{source}: workspace.roots must be a list of paths")
        return []
    roots: list[Path] = []
    seen: set[str] = set()
    for value in raw:
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{source}: workspace.roots has an invalid entry {value!r}")
            continue
        expanded = _expand_home(value.strip(), home)
        if not Path(expanded).is_absolute():
            problems.append(f"{source}: workspace root {value!r} must be an absolute path")
            continue
        root = Path(os.path.normpath(expanded))
        key = os.path.normcase(root)
        if key not in seen:
            seen.add(key)
            roots.append(root)
    return roots


def _drop_nested(roots: list[Path]) -> tuple[list[Path], tuple[str, ...]]:
    """Keep the outer root of any nested pair so no repository is scanned twice."""
    keys = [Path(os.path.normcase(root)) for root in roots]
    kept: list[Path] = []
    warnings: list[str] = []
    for i, root in enumerate(roots):
        outer = next((roots[j] for j in range(len(roots)) if j != i and keys[i].is_relative_to(keys[j])), None)
        if outer is None:
            kept.append(root)
        else:
            warnings.append(f"workspace root {root} is inside workspace root {outer} and was dropped")
    return kept, tuple(warnings)


def load_workspace_config(
    explicit: Path | str | None = None,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform: str | None = None,
) -> WorkspaceConfig | NotConfigured:
    """Load the configured workspace roots.

    Returns ``NotConfigured`` when there is no file at the default location or it lists no
    roots. Raises ``ConfigError`` listing every problem when the file is invalid, or when a
    file the user named does not exist.
    """
    environ = os.environ if environ is None else environ
    home = Path.home() if home is None else home
    source, named = _locate(explicit, environ, home, platform)
    if not source.is_file():
        if named:
            raise ConfigError((f"configuration file not found: {source}",))
        return NotConfigured(f"no configuration file at {source}")
    try:
        data = tomllib.loads(source.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise ConfigError((f"{source}: cannot be read as TOML ({error})",)) from error

    problems = [f"{source}: unknown key '{key}'" for key in data if key != "workspace"]
    workspace = data.get("workspace", {})
    if not isinstance(workspace, dict):
        problems.append(f"{source}: 'workspace' must be a table")
        workspace = {}
    problems += [f"{source}: unknown key 'workspace.{key}'" for key in workspace if key != "roots"]
    roots = _roots(workspace.get("roots", []), home, source, problems)
    if problems:
        raise ConfigError(tuple(problems))
    if not roots:
        return NotConfigured(f"{source}: workspace.roots lists no roots")
    kept, warnings = _drop_nested(roots)
    return WorkspaceConfig(roots=tuple(kept), source=source, warnings=warnings)


def check_root(root: Path) -> str:
    """The state of one root: accessible, missing, not a directory, or unreadable."""
    if not root.exists():
        return MISSING
    if not root.is_dir():
        return NOT_A_DIRECTORY
    try:
        with os.scandir(root):
            return ACCESSIBLE
    except OSError:
        return UNREADABLE


def check_roots(config: WorkspaceConfig) -> tuple[RootCheck, ...]:
    """Report each root on its own as accessible, missing, not a directory, or unreadable."""
    return tuple(RootCheck(root=root, status=check_root(root)) for root in config.roots)
