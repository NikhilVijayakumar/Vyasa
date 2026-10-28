import hashlib
import io
import multiprocessing
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from vyasa.adapters.cli.main import main
from vyasa.adapters.sqlite import lock
from vyasa.adapters.sqlite.database import open_index
from vyasa.application.indexing.store import index_path

SRC = Path(__file__).resolve().parents[1] / "src"


def git_repo(path: Path, remote: str | None = None) -> Path:
    (path / ".git").mkdir(parents=True)
    (path / ".git" / "HEAD").write_text("ref: refs/heads/main\n")
    config = "[core]\n\tbare = false\n"
    if remote:
        config += f'[remote "origin"]\n\turl = {remote}\n'
    (path / ".git" / "config").write_text(config)
    (path / "README.md").write_text("hello\n")
    return path


@pytest.fixture
def env(tmp_path):
    home = tmp_path / "data"
    return {"VYASA_HOME": str(home), "HOME": str(tmp_path / "home")}, home


def configure(home: Path, *roots: Path):
    home.mkdir(parents=True, exist_ok=True)
    listing = ", ".join(f'"{r.as_posix()}"' for r in roots)
    (home / "config.toml").write_text(f"[workspace]\nroots = [{listing}]\n")


def scan(environ, *extra):
    out, err = io.StringIO(), io.StringIO()
    code = main(["scan", *extra], environ, out, err)
    return code, out.getvalue(), err.getvalue()


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(str(path.relative_to(root)).encode() + path.read_bytes())
    return digest.hexdigest()


def project_names(home: Path) -> list[str]:
    c = open_index(home / "index.sqlite3", read_only=True)
    names = [r[0] for r in c.execute("SELECT display_name FROM projects ORDER BY 1")]
    c.close()
    return names


# -- roots ----------------------------------------------------------------------------------------------


def test_only_configured_roots_are_scanned(tmp_path, env):
    environ, home = env
    a, b, outside = tmp_path / "a", tmp_path / "b", tmp_path / "outside"
    git_repo(a / "one"); git_repo(b / "two"); git_repo(outside / "three")
    configure(home, a, b)
    code, out, _ = scan(environ)
    assert code == 0 and project_names(home) == ["one", "two"]
    assert "outside" not in out


def test_nested_root_is_scanned_once(tmp_path, env):
    environ, home = env
    outer = tmp_path / "w"
    git_repo(outer / "inner" / "repo")
    configure(home, outer, outer / "inner")
    code, out, _ = scan(environ)
    assert code == 0 and project_names(home) == ["repo"]
    assert "was dropped" in out and "Scanning 1 workspace root" in out


def test_repositories_are_left_byte_identical(tmp_path, env):
    environ, home = env
    root = tmp_path / "w"
    git_repo(root / "r", "https://tok:secret@github.com/acme/r.git")
    configure(home, root)
    before = tree_hash(root)
    scan(environ)
    assert tree_hash(root) == before


def test_scan_never_rewrites_the_human_maintained_profile(tmp_path, env):
    environ, home = env
    root = tmp_path / "w"
    repo = git_repo(root / "r", "https://github.com/acme/r.git")
    (repo / ".vyasa").mkdir()
    profile = repo / ".vyasa" / "project-profile.toml"
    profile.write_text('schema_version = 1\nname = "Declared"\npurpose = "Mine."\n')
    configure(home, root)
    before = profile.read_bytes()
    scan(environ)
    scan(environ)
    assert profile.read_bytes() == before


# -- bootstrap and report ----------------------------------------------------------------------------------


def test_first_scan_creates_the_index_then_repeats_cleanly(tmp_path, env):
    environ, home = env
    root = tmp_path / "w"
    git_repo(root / "r", "git@github.com:Acme/r.git")
    configure(home, root)
    assert not (home / "index.sqlite3").exists()
    code, out, _ = scan(environ)
    assert code == 0 and "Created the index." in out and "1 added" in out
    assert f"{root}: completed - 1 repositories" in out
    code, out, _ = scan(environ)
    assert code == 0 and "Created the index." not in out and "1 unchanged" in out and "Indexed 1 projects" in out


def test_skipped_directories_are_reported_with_advice(tmp_path, env):
    environ, home = env
    root = tmp_path / "w"
    deep = root
    for i in range(10):
        deep = deep / f"d{i}"
    git_repo(deep)
    git_repo(root / "shallow")
    configure(home, root)
    code, out, _ = scan(environ)
    assert "skipped max_depth x" in out and "raise max_depth" in out


def test_missing_root_fails_alone(tmp_path, env):
    environ, home = env
    good = tmp_path / "good"
    git_repo(good / "r")
    configure(home, tmp_path / "gone", good)
    code, out, _ = scan(environ)
    assert code == 1
    assert "gone: failed" in out and "could not scan: root_not_found" in out
    assert f"{good}: completed" in out and project_names(home) == ["r"]


def test_failed_root_marks_nothing_missing(tmp_path, env):
    environ, home = env
    root = tmp_path / "w"
    git_repo(root / "r")
    configure(home, root)
    scan(environ)
    configure(home, tmp_path / "w2")  # w vanishes from config; w2 does not exist
    code, out, _ = scan(environ)
    assert code == 1
    c = open_index(home / "index.sqlite3", read_only=True)
    assert c.execute("SELECT state FROM projects").fetchone()[0] == "active"
    c.close()


# -- exit codes ---------------------------------------------------------------------------------------------


def test_no_configuration_scans_and_creates_nothing(tmp_path, env):
    environ, home = env
    code, out, err = scan(environ)
    assert code == 2 and "config.toml" in err and "roots" in err and out == ""
    assert not home.exists()


def test_invalid_configuration_lists_every_problem(tmp_path, env):
    environ, home = env
    home.mkdir()
    (home / "config.toml").write_text('mystery = 1\n[workspace]\nroots = ["relative/path"]\n')
    code, out, err = scan(environ)
    assert code == 2 and "unknown key 'mystery'" in err and "must be an absolute path" in err
    assert not (home / "index.sqlite3").exists()


def test_explicit_missing_config_file(tmp_path, env):
    environ, home = env
    code, _, err = scan(environ, "--config", str(tmp_path / "nope.toml"))
    assert code == 2 and "not found" in err


def test_unknown_command_is_a_usage_error(env):
    environ, _ = env
    assert main(["bogus"], environ, io.StringIO(), io.StringIO()) == 2


def _hold(path, started, release):
    c = open_index(path)
    lock.acquire(c, "other", "r", datetime.now(timezone.utc))
    started.set()
    release.wait(15)
    c.close()


def test_concurrent_scan_exits_3_without_writing(tmp_path, env):
    environ, home = env
    root = tmp_path / "w"
    git_repo(root / "r")
    configure(home, root)
    started, release = multiprocessing.Event(), multiprocessing.Event()
    child = multiprocessing.Process(target=_hold, args=(index_path(environ), started, release))
    child.start()
    try:
        assert started.wait(15)
        code, out, err = scan(environ)
        assert code == 3 and "OPERATION_IN_PROGRESS" in err
    finally:
        release.set()
        child.join(15)
    assert project_names(home) == []


def test_old_schema_too_new_exits_4(tmp_path, env):
    environ, home = env
    import sqlite3
    home.mkdir()
    raw = sqlite3.connect(home / "index.sqlite3")
    raw.execute("PRAGMA user_version = 99")
    raw.close()
    configure(home, tmp_path)
    code, _, err = scan(environ)
    assert code == 4 and "INDEX_SCHEMA_TOO_NEW" in err


# -- entry points ---------------------------------------------------------------------------------------------


def test_python_dash_m_runs_the_command(tmp_path, env):
    environ, home = env
    root = tmp_path / "w"
    git_repo(root / "r")
    configure(home, root)
    done = subprocess.run([sys.executable, "-m", "vyasa", "scan"], capture_output=True, text=True, timeout=60,
                          env={**os.environ, **environ, "PYTHONPATH": str(SRC)})
    assert done.returncode == 0 and "Indexed 1 projects" in done.stdout, done.stderr
