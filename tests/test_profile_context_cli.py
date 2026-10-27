import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from test_profile_context_live import make_project

from vyasa.adapters.cli.main import INDEX, OK, USAGE, main
from vyasa.application import profile_context as pc

SRC = Path(__file__).resolve().parents[1] / "src"


def run(argv, environ=None):
    out, err = io.StringIO(), io.StringIO()
    code = main(argv, environ if environ is not None else {}, out, err)
    return code, out.getvalue(), err.getvalue()


def tree_hash(directory):
    digest = hashlib.sha256()
    for current, folders, files in sorted(os.walk(directory)):
        folders.sort()
        for name in sorted(files) + folders:
            path = os.path.join(current, name)
            digest.update(os.path.relpath(path, directory).encode())
            if os.path.isfile(path):
                digest.update(Path(path).read_bytes())
    return digest.hexdigest()


def test_prints_the_bundle_as_json_for_a_path(tmp_path):
    root = make_project(tmp_path / "app")
    code, out, err = run(["profile-context", str(root)])
    assert (code, err) == (OK, "")
    bundle = json.loads(out)
    assert bundle["data"]["source"]["kind"] == "live_scan" and bundle["data"]["display_name"] == "app"
    assert bundle["data"]["checkouts"][0]["differences"] and bundle["data"]["workflow"]
    assert out.isascii() and out.endswith("\n")


def test_the_default_path_is_the_current_directory(tmp_path, monkeypatch):
    root = make_project(tmp_path / "app")
    monkeypatch.chdir(root)
    code, out, err = run(["profile-context"])
    assert (code, err) == (OK, "") and json.loads(out)["data"]["display_name"] == "app"


def test_the_bundle_matches_the_library_function(tmp_path):
    root = make_project(tmp_path / "app")
    _, out, _ = run(["profile-context", str(root)])
    data = json.loads(out)["data"]
    again = pc.live_context(root)["data"]
    assert set(data) == set(again) and data["profile"] == again["profile"] and data["workflow"] == again["workflow"]


def test_no_absolute_path_is_printed(tmp_path):
    root = make_project(tmp_path / "app")
    _, out, _ = run(["profile-context", str(root)])
    for variant in (str(root), root.as_posix(), str(tmp_path), tmp_path.as_posix()):
        assert variant not in out and variant.replace("\\", "\\\\") not in out


def test_a_missing_path_is_a_usage_error(tmp_path):
    code, out, err = run(["profile-context", str(tmp_path / "missing")])
    assert code == USAGE and out == "" and "not a directory" in err
    assert str(tmp_path) not in err


def test_a_directory_that_is_not_a_project_is_a_usage_error(tmp_path):
    (tmp_path / "empty").mkdir()
    code, out, err = run(["profile-context", str(tmp_path / "empty")])
    assert code == USAGE and out == "" and "No project was recognized" in err


def test_an_internal_failure_exits_with_a_generic_message(tmp_path, monkeypatch):
    def boom(path):
        raise RuntimeError("secret detail from the repository")

    monkeypatch.setattr(pc, "live_context", boom)
    code, out, err = run(["profile-context", str(make_project(tmp_path / "app"))])
    assert code == INDEX and out == "" and "internal error" in err and "secret" not in err


def test_nothing_is_written_to_the_repository_or_the_data_directory(tmp_path):
    root = make_project(tmp_path / "app")
    data = tmp_path / "data"
    before = tree_hash(root)
    code, _, _ = run(["profile-context", str(root)], {"VYASA_DATA_DIR": str(data), "XDG_DATA_HOME": str(data), "LOCALAPPDATA": str(data), "APPDATA": str(data)})
    assert code == OK and tree_hash(root) == before and not data.exists()


def test_the_profile_with_differences_is_left_byte_identical(tmp_path):
    root = make_project(tmp_path / "app")
    path = root / ".vyasa" / "project-profile.toml"
    before = path.read_bytes()
    code, out, _ = run(["profile-context", str(root)])
    assert code == OK and path.read_bytes() == before
    assert json.loads(out)["data"]["checkouts"][0]["differences"]


def test_no_process_is_started(tmp_path, monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("a process was started")

    monkeypatch.setattr(subprocess, "Popen", refuse)
    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(os, "system", refuse)
    code, out, _ = run(["profile-context", str(make_project(tmp_path / "app"))])
    assert code == OK and json.loads(out)["data"]["checkouts"]


def test_a_real_subprocess_run_works_without_a_configuration(tmp_path):
    root = make_project(tmp_path / "app")
    env = {**os.environ, "PYTHONPATH": str(SRC), "VYASA_DATA_DIR": str(tmp_path / "data")}
    result = subprocess.run([sys.executable, "-m", "vyasa", "profile-context", str(root)], capture_output=True, text=True, env=env, cwd=tmp_path, timeout=60)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["data"]["source"]["kind"] == "live_scan"
    assert not (tmp_path / "data").exists()

