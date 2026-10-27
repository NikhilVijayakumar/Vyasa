import json
import os
from datetime import timedelta

import pytest
from test_language_query import report, scanned
from test_local_index import LATEST, T0, make_run, repo

from vyasa.adapters.sqlite.database import open_index, open_memory_index
from vyasa.application import profile_context as pc
from vyasa.application.indexing.scan import enrich_run, scan_workspace
from vyasa.application.indexing.store import store_run
from vyasa.domain.workspace_config import WorkspaceConfig

NOW = lambda: T0 + timedelta(hours=1)  # noqa: E731

PROFILE = """schema_version = 2

[project]
summary = "A tiny web app."

[project.technology]
declared_languages = ["JavaScript", "Rust"]
declared_frameworks = ["React", "Express"]

[project.engineering.openspec]
enabled = true
"""


def make_project(root, profile=PROFILE):
    files = {
        "package.json": json.dumps({"dependencies": {"react": "^18", "left-pad": "1"}, "devDependencies": {"jest": "^29"}}),
        "README.md": "# app\n", "src/app.js": "", "tests/app.test.js": "", "AGENTS.md": "rules",
    }
    if profile:
        files[".vyasa/project-profile.toml"] = profile
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def observed(checkout):
    """The observed facts of a checkout without the times, which differ between two scans."""
    return {key: {k: v for k, v in checkout[key].items() if k != "observed_at"} for key in ("languages", "composition", "markers", "frameworks")}


def snapshot(directory):
    found = {}
    for current, folders, files in os.walk(directory):
        for name in files + folders:
            path = os.path.join(current, name)
            found[path] = (os.path.getsize(path), os.stat(path).st_mtime_ns) if os.path.isfile(path) else None
    return found


# --- the in-memory index ---

def test_the_memory_index_is_migrated_and_has_no_file():
    connection = open_memory_index()
    try:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == LATEST
        assert all(r["file"] == "" for r in connection.execute("PRAGMA database_list"))
        assert connection.execute("SELECT count(*) FROM projects").fetchone()[0] == 0
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        connection.close()


def test_two_memory_indexes_do_not_share_data():
    one, two = open_memory_index(), open_memory_index()
    try:
        store_run(one, make_run([repo("a")]), owner="o", now=NOW)
        assert two.execute("SELECT count(*) FROM projects").fetchone()[0] == 0
    finally:
        one.close()
        two.close()


def test_enrich_run_attaches_results_and_marks_failures_partial():
    def detect(path):
        if path.name == "bad":
            raise RuntimeError("secret")
        return scanned(report())

    run = enrich_run(make_run([repo("good"), repo("bad")]), detect)
    assert run.status == "partial" and [c.languages.failed for c in run.repositories] == [None, "detection_error"]


# --- the live context ---

def test_a_live_scan_gives_the_bundle_of_an_unindexed_repository(tmp_path):
    data = pc.live_context(make_project(tmp_path / "app"), now=NOW)["data"]
    assert data["source"]["kind"] == "live_scan" and data["project_id"] is None and data["display_name"] == "app"
    (checkout,) = data["checkouts"]
    assert "JavaScript" in {i["label"] for i in checkout["languages"]["items"]} and checkout["composition"]["status"] == "complete"
    states = {i["marker"]: i["state"] for i in checkout["markers"]["items"]}
    assert states["readme"] == states["tests"] == states["agent_instructions"] == "detected" and states["openspec_directory"] == "not_detected"
    assert {t["key"] for t in checkout["frameworks"]["technologies"]} == {"react", "jest"}
    assert data["profile"]["status"] == "valid" and data["workflow"] == list(pc.WORKFLOW)


def test_the_differences_in_the_live_bundle(tmp_path):
    (checkout,) = pc.live_context(make_project(tmp_path / "app"), now=NOW)["data"]["checkouts"]
    assert {(f["code"], f["subject"]) for f in checkout["differences"]} == {
        ("declared_language_not_detected", "Rust"), ("declared_framework_not_detected", "Express"),
        ("declared_openspec_not_detected", "openspec"), ("detected_technology_not_declared", "jest"),
    }


def test_the_live_bundle_has_the_same_facts_as_the_stored_one(tmp_path):
    root = tmp_path / "ws"
    make_project(root / "app")
    live = pc.live_context(root / "app", now=NOW)["data"]
    connection = open_index(tmp_path / "data" / "index.sqlite3")
    try:
        scan_workspace(WorkspaceConfig(roots=(root,), source=tmp_path / "c.toml"), connection, owner="o")
        pid = connection.execute("SELECT project_id FROM projects").fetchone()[0]
        stored = pc.profile_context(connection, pid, now=NOW)["data"]
    finally:
        connection.close()
    assert stored["source"]["kind"] == "index" and observed(live["checkouts"][0]) == observed(stored["checkouts"][0])
    assert live["checkouts"][0]["differences"] == stored["checkouts"][0]["differences"]
    assert live["profile"] == stored["profile"] and set(live) == set(stored)


def test_the_live_bundle_has_no_absolute_path(tmp_path):
    root = make_project(tmp_path / "app")
    text = json.dumps(pc.live_context(root, now=NOW))
    for variant in (str(root), str(root.resolve()), root.resolve().as_posix(), str(tmp_path), tmp_path.as_posix()):
        assert variant not in text


def test_manifest_text_never_reaches_the_bundle(tmp_path):
    root = tmp_path / "app"
    root.mkdir()
    (root / "package.json").write_text('{"dependencies": {"x": "https://user:hunter2@host/x"}, "oops', encoding="utf-8")
    text = json.dumps(pc.live_context(root, now=NOW))
    assert "hunter2" not in text and "oops" not in text and '"reason": "syntax"' in text


def test_a_subdirectory_or_empty_directory_is_not_a_project(tmp_path):
    (tmp_path / "empty").mkdir()
    with pytest.raises(pc.NotAProject):
        pc.live_context(tmp_path / "empty", now=NOW)
    root = make_project(tmp_path / "app")
    with pytest.raises(pc.NotAProject):
        pc.live_context(root / "src", now=NOW)


def test_a_missing_path_or_a_file_is_not_a_project(tmp_path):
    with pytest.raises(pc.NotAProject):
        pc.live_context(tmp_path / "missing", now=NOW)
    (tmp_path / "file.txt").write_text("x", encoding="utf-8")
    with pytest.raises(pc.NotAProject):
        pc.live_context(tmp_path / "file.txt", now=NOW)


def test_the_live_scan_writes_nothing(tmp_path):
    root = make_project(tmp_path / "app")
    before = snapshot(tmp_path)
    pc.live_context(root, now=NOW)
    assert snapshot(tmp_path) == before
