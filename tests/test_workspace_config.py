import json
import os
from pathlib import Path

import pytest

from vyasa.application.configuration.workspace import check_roots, data_directory, load_workspace_config
from vyasa.domain.workspace_config import (
    ACCESSIBLE,
    MISSING,
    NOT_A_DIRECTORY,
    UNREADABLE,
    ConfigError,
    NotConfigured,
    WorkspaceConfig,
)


def toml_roots(*roots):
    """A TOML file body; JSON string escaping is valid TOML, so Windows paths survive."""
    return "[workspace]\nroots = [" + ", ".join(json.dumps(str(r)) for r in roots) + "]\n"


def write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def load(tmp_path, body=None, **kwargs):
    """Load an explicit file written under tmp_path with a controlled environment."""
    file = write(tmp_path / "cfg" / "config.toml", body) if body is not None else None
    kwargs.setdefault("environ", {})
    kwargs.setdefault("home", tmp_path / "home")
    return load_workspace_config(file, **kwargs)


# -- data directory ----------------------------------------------------------------


def test_windows_data_directory(tmp_path):
    local = tmp_path / "local"
    assert data_directory({"LOCALAPPDATA": str(local)}, tmp_path / "h", "win32") == local / "Vyasa"
    assert data_directory({}, tmp_path / "h", "win32") == tmp_path / "h" / "AppData" / "Local" / "Vyasa"


def test_macos_data_directory(tmp_path):
    expected = tmp_path / "h" / "Library" / "Application Support" / "Vyasa"
    assert data_directory({}, tmp_path / "h", "darwin") == expected


def test_linux_data_directory(tmp_path):
    xdg = tmp_path / "xdg"
    assert data_directory({"XDG_DATA_HOME": str(xdg)}, tmp_path / "h", "linux") == xdg / "vyasa"
    assert data_directory({}, tmp_path / "h", "linux") == tmp_path / "h" / ".local" / "share" / "vyasa"


@pytest.mark.parametrize("platform", ["win32", "darwin", "linux"])
def test_home_override_wins_on_every_platform(tmp_path, platform):
    override = tmp_path / "custom"
    environ = {"VYASA_HOME": str(override), "LOCALAPPDATA": str(tmp_path / "ignored")}
    assert data_directory(environ, tmp_path / "h", platform) == override


def test_empty_home_override_is_ignored(tmp_path):
    assert data_directory({"VYASA_HOME": ""}, tmp_path / "h", "linux") == tmp_path / "h" / ".local" / "share" / "vyasa"


# -- locating the file -----------------------------------------------------------------


def test_explicit_path_wins_over_environment(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    explicit = write(tmp_path / "explicit.toml", toml_roots(a))
    named = write(tmp_path / "named.toml", toml_roots(b))
    result = load_workspace_config(explicit, environ={"VYASA_CONFIG": str(named)}, home=tmp_path)
    assert result.source == explicit and result.roots == (a,)


def test_environment_variable_is_used_without_an_explicit_path(tmp_path):
    a = tmp_path / "a"
    named = write(tmp_path / "named.toml", toml_roots(a))
    result = load_workspace_config(None, environ={"VYASA_CONFIG": str(named)}, home=tmp_path)
    assert result.source == named


def test_default_location_is_the_data_directory(tmp_path):
    a = tmp_path / "a"
    data = tmp_path / "data"
    write(data / "config.toml", toml_roots(a))
    result = load_workspace_config(None, environ={"VYASA_HOME": str(data)}, home=tmp_path)
    assert result.source == data / "config.toml" and result.roots == (a,)


def test_missing_explicit_file_is_an_error(tmp_path):
    with pytest.raises(ConfigError, match="missing.toml"):
        load_workspace_config(tmp_path / "missing.toml", environ={}, home=tmp_path)


def test_missing_environment_file_is_an_error(tmp_path):
    with pytest.raises(ConfigError, match="gone.toml"):
        load_workspace_config(None, environ={"VYASA_CONFIG": str(tmp_path / "gone.toml")}, home=tmp_path)


# -- loading roots ---------------------------------------------------------------------


def test_several_roots_are_returned_in_order(tmp_path):
    a, b = tmp_path / "one", tmp_path / "two" / "deeper"
    result = load(tmp_path, toml_roots(b, a))
    assert isinstance(result, WorkspaceConfig)
    assert result.roots == (b, a)
    assert result.warnings == ()


def test_duplicate_roots_are_merged(tmp_path):
    a = tmp_path / "one"
    redundant = f"{a}{os.sep}sub{os.sep}.."
    result = load(tmp_path, toml_roots(a, f"{a}{os.sep}", redundant))
    assert result.roots == (a,)


def test_home_is_expanded(tmp_path):
    home = tmp_path / "home"
    result = load(tmp_path, toml_roots("~/work", "~/other"), home=home)
    assert result.roots == (Path(os.path.normpath(home / "work")), Path(os.path.normpath(home / "other")))
    assert load(tmp_path, toml_roots("~"), home=home).roots == (Path(os.path.normpath(home)),)


def test_nested_root_is_dropped_and_reported(tmp_path):
    outer, inner = tmp_path / "outer", tmp_path / "outer" / "inner"
    result = load(tmp_path, toml_roots(outer, inner))
    assert result.roots == (outer,)
    assert len(result.warnings) == 1 and "dropped" in result.warnings[0]


def test_the_outer_root_wins_whatever_the_order(tmp_path):
    outer, inner = tmp_path / "outer", tmp_path / "outer" / "inner"
    assert load(tmp_path, toml_roots(inner, outer)).roots == (outer,)


def test_sibling_roots_with_a_common_prefix_are_not_nested(tmp_path):
    result = load(tmp_path, toml_roots(tmp_path / "work", tmp_path / "work2"))
    assert result.warnings == ()


# -- not configured -----------------------------------------------------------------------


def test_no_file_at_the_default_location_is_not_configured(tmp_path):
    result = load_workspace_config(None, environ={"VYASA_HOME": str(tmp_path / "empty")}, home=tmp_path)
    assert isinstance(result, NotConfigured)
    assert "config.toml" in result.reason


@pytest.mark.parametrize("body", ["", "[workspace]\n", "[workspace]\nroots = []\n"])
def test_empty_roots_are_not_configured(tmp_path, body):
    result = load(tmp_path, body)
    assert isinstance(result, NotConfigured)
    assert "roots" in result.reason


# -- invalid ----------------------------------------------------------------------------------


def test_syntax_error_is_reported_with_the_file_name(tmp_path):
    with pytest.raises(ConfigError, match="config.toml"):
        load(tmp_path, "[workspace\nroots = ")


def test_non_utf8_file_is_reported(tmp_path):
    file = tmp_path / "bad.toml"
    file.write_bytes(b"\xff\xfe\x00bad")
    with pytest.raises(ConfigError, match="bad.toml"):
        load_workspace_config(file, environ={}, home=tmp_path)


def test_unknown_keys_are_rejected(tmp_path):
    with pytest.raises(ConfigError) as error:
        load(tmp_path, toml_roots(tmp_path) + 'depth = 3\n[other]\nx = 1\n')
    text = str(error.value)
    assert "workspace.depth" in text and "'other'" in text


@pytest.mark.parametrize("body", ['[workspace]\nroots = "x"\n', "[workspace]\nroots = [1]\n", 'workspace = "x"\n'])
def test_wrong_types_are_rejected(tmp_path, body):
    with pytest.raises(ConfigError) as error:
        load(tmp_path, body)
    assert error.value.problems


def test_relative_root_is_rejected_naming_the_value(tmp_path):
    with pytest.raises(ConfigError, match="relative/path"):
        load(tmp_path, toml_roots("relative/path"))


def test_all_problems_are_reported_together(tmp_path):
    with pytest.raises(ConfigError) as error:
        load(tmp_path, toml_roots("relative", tmp_path) + "extra = 1\n")
    assert len(error.value.problems) == 2


def test_nothing_is_applied_when_invalid(tmp_path):
    with pytest.raises(ConfigError):
        load(tmp_path, toml_roots(tmp_path, "relative"))


# -- checking roots ------------------------------------------------------------------------------


def config(*roots):
    return WorkspaceConfig(roots=tuple(roots), source=Path("config.toml"))


def test_each_root_is_checked_on_its_own(tmp_path):
    good = tmp_path / "good"
    good.mkdir()
    gone = tmp_path / "gone"
    plain = tmp_path / "plain.txt"
    plain.write_text("x", encoding="utf-8")
    checks = check_roots(config(good, gone, plain))
    assert [(c.root, c.status) for c in checks] == [(good, ACCESSIBLE), (gone, MISSING), (plain, NOT_A_DIRECTORY)]


def test_unreadable_root_does_not_affect_the_others(tmp_path, monkeypatch):
    blocked, fine = tmp_path / "blocked", tmp_path / "fine"
    blocked.mkdir()
    fine.mkdir()
    real = os.scandir

    def scandir(path="."):
        if os.fspath(path) == os.fspath(blocked):
            raise PermissionError(13, "denied", os.fspath(blocked))
        return real(path)

    monkeypatch.setattr(os, "scandir", scandir)
    checks = check_roots(config(blocked, fine))
    assert [c.status for c in checks] == [UNREADABLE, ACCESSIBLE]


def test_checking_opens_no_file(tmp_path, monkeypatch):
    import builtins

    root = tmp_path / "r"
    root.mkdir()
    (root / "secret.txt").write_text("x", encoding="utf-8")

    def refuse(*_a, **_k):
        raise AssertionError("a file was opened")

    monkeypatch.setattr(builtins, "open", refuse)
    assert check_roots(config(root))[0].status == ACCESSIBLE


# -- found by the grill --------------------------------------------------------------------------------------


def test_utf8_byte_order_mark_is_accepted(tmp_path):
    file = tmp_path / "bom.toml"
    file.write_bytes(b"\xef\xbb\xbf" + toml_roots(tmp_path).encode("utf-8"))
    result = load_workspace_config(file, environ={}, home=tmp_path)
    assert result.roots == (tmp_path,)


def test_windows_line_endings_are_accepted(tmp_path):
    file = tmp_path / "crlf.toml"
    file.write_bytes(toml_roots(tmp_path).replace("\n", "\r\n").encode("utf-8"))
    assert load_workspace_config(file, environ={}, home=tmp_path).roots == (tmp_path,)


def test_single_quoted_literal_paths_load_without_escaping(tmp_path):
    result = load(tmp_path, f"[workspace]\nroots = ['{tmp_path}']\n")
    assert result.roots == (tmp_path,)


def test_environment_variables_in_paths_are_not_expanded(tmp_path):
    with pytest.raises(ConfigError, match="absolute"):
        load(tmp_path, '[workspace]\nroots = ["$HOME/work"]\n')


def test_frozen_executable_uses_the_data_folder_beside_its_folder(tmp_path):
    exe = tmp_path / "root" / "vyasa-mcp" / "vyasa-mcp.exe"
    assert data_directory({}, tmp_path, "win32", frozen_executable=exe) == tmp_path / "root" / "data"


def test_home_override_beats_a_frozen_executable(tmp_path):
    exe = tmp_path / "root" / "vyasa" / "vyasa.exe"
    assert data_directory({"VYASA_HOME": str(tmp_path / "h")}, tmp_path, "win32", frozen_executable=exe) == tmp_path / "h"


def test_source_run_keeps_the_platform_directory(tmp_path):
    local = tmp_path / "Local"
    assert data_directory({"LOCALAPPDATA": str(local)}, tmp_path, "win32", frozen_executable=None) == local / "Vyasa"
