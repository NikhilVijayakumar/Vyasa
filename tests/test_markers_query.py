import shutil
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest
from test_language_query import report, scanned  # noqa: F401
from test_local_index import LATEST, ROOT, T0, db, make_run, repo, store  # noqa: F401

from vyasa.adapters.sqlite.database import open_index
from vyasa.application import query
from vyasa.application.indexing.scan import scan_workspace
from vyasa.application.scanning.markers import default_marker_rules
from vyasa.domain.discovery import PARTIAL
from vyasa.domain.git_remote import GitRemote
from vyasa.domain.index import INVALID_INPUT, IndexStoreError
from vyasa.domain.languages import CheckoutScan, LanguageOutcome
from vyasa.domain.markers import MARKERS, MarkerFound, MarkerReport
from vyasa.domain.workspace_config import WorkspaceConfig

NOW = lambda: T0 + timedelta(hours=1)  # noqa: E731
VERSION = default_marker_rules().version


def found(marker, *paths, rules=("r",), total=None, scope=None):
    return MarkerFound(marker, total or len(paths), rules, tuple((p, scope) for p in paths))


def marked(name, *finds, stopped_by=None, identity=None, languages=()):
    outcome = LanguageOutcome(report(languages, stopped_by=stopped_by), markers=MarkerReport(tuple(finds), VERSION, stopped_by))
    remote = GitRemote("origin", "github", "github.com", identity) if identity else None
    return replace(repo(name, remote), languages=outcome)


def rows(db, name):
    return [tuple(r) for r in db.execute(
        "SELECT o.markers_version, m.marker, m.total, m.rules, m.paths FROM language_observations o JOIN checkouts c USING (checkout_id)"
        " LEFT JOIN checkout_markers m USING (observation_id) WHERE c.path LIKE ? ORDER BY o.observation_id, m.marker", (f"%{name}",)
    )]


# --- store ---

def test_version_7_index_upgrades_with_null_versions(tmp_path):
    steps = tmp_path / "old"
    steps.mkdir()
    for file in sorted(Path(__file__).parents[1].joinpath("src/vyasa/adapters/sqlite/migrations").glob("000[1-7]_*.sql")):
        shutil.copy(file, steps / file.name)
    old = open_index(tmp_path / "i.sqlite3", migrations=steps)
    store(old, make_run([repo("a")]))
    old.execute("INSERT INTO language_observations (checkout_id, run_id, observed_at, status, types_version)"
                " SELECT checkout_id, last_run_id, ?, 'complete', 2 FROM checkouts", (T0.isoformat(),))
    old.close()
    new = open_index(tmp_path / "i.sqlite3")
    assert new.execute("PRAGMA user_version").fetchone()[0] == LATEST >= 8
    assert [tuple(r) for r in new.execute("SELECT markers_version FROM language_observations")] == [(None,)]


def test_markers_are_stored_with_a_version(db):
    store(db, make_run([marked("a", found("readme", "README.md", rules=("readme_file",)), found("tests", "tests", "x_test.go", rules=("a", "b")))]))
    assert rows(db, "a") == [
        (VERSION, "readme", 1, '["readme_file"]', '[{"path": "README.md"}]'),
        (VERSION, "tests", 2, '["a", "b"]', '[{"path": "tests"}, {"path": "x_test.go"}]'),
    ]


def test_scope_is_stored_with_the_path(db):
    store(db, make_run([marked("a", found("agent_instructions", "pkg/CLAUDE.md", scope="pkg"))]))
    assert rows(db, "a")[0][4] == '[{"path": "pkg/CLAUDE.md", "scope": "pkg"}]'


def test_complete_scan_without_markers_still_has_a_version(db):
    store(db, make_run([marked("a")]))
    assert rows(db, "a") == [(VERSION, None, None, None, None)]


def test_partial_walk_stores_found_markers(db):
    store(db, make_run([marked("a", found("tests", "tests"), stopped_by="entries")]))
    assert [(r[0], r[1]) for r in rows(db, "a")] == [(VERSION, "tests")]


def test_failed_and_unmarked_outcomes_store_no_version(db):
    store(db, make_run([replace(repo("f"), languages=LanguageOutcome(failed="detection_error")),
                        replace(repo("u"), languages=LanguageOutcome(report()))]))
    assert rows(db, "f") == [(None, None, None, None, None)] and rows(db, "u") == [(None, None, None, None, None)]


def test_retention_keeps_two_observations_with_their_markers(db):
    for i, marker in enumerate(["readme", "docs", "tests"]):
        store(db, make_run([marked("a", found(marker, "x"))]), at=T0 + timedelta(minutes=i))
    assert [r[1] for r in rows(db, "a")] == ["docs", "tests"]
    assert db.execute("SELECT count(*) FROM checkout_markers").fetchone()[0] == 2


# --- scan ---

def config(tmp_path):
    return WorkspaceConfig(roots=(ROOT,), source=tmp_path / "c.toml")


def test_scan_stores_markers_from_the_scan_result(db, tmp_path):
    def detect(path):
        scan = scanned(report())
        return CheckoutScan(scan.composition, scan.languages, MarkerReport((found("docs", "docs"),), VERSION, None))

    scan_workspace(config(tmp_path), db, owner="o", discover=lambda r: make_run([repo("a")]), detect=detect)
    assert [r[1] for r in rows(db, "a")] == ["docs"]


def test_failing_detection_is_isolated_and_marks_the_run_partial(db, tmp_path):
    def detect(path):
        if path.name == "bad":
            raise RuntimeError("secret")
        scan = scanned(report())
        return CheckoutScan(scan.composition, scan.languages, MarkerReport((found("docs", "docs"),), VERSION, None))

    (result,) = scan_workspace(config(tmp_path), db, owner="o", discover=lambda r: make_run([repo("good"), repo("bad")]), detect=detect)
    assert result.stored.status == "partial" and result.run.status == PARTIAL
    assert rows(db, "bad") == [(None, None, None, None, None)] and rows(db, "good")[0][1] == "docs"


def test_real_scan_detects_markers_from_a_real_tree(db, tmp_path):
    root = tmp_path / "ws" / "proj"
    for name in ("README.md", "docs/index.md", "tests/test_a.py", "AGENTS.md", "openspec/specs/a.md"):
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text("", encoding="utf-8")
    from vyasa.domain.discovery import Candidate

    cand = Candidate(root, "eligible", kind="repository", markers=("pyproject.toml",), git=".", remote=None, remote_status="none")
    scan_workspace(WorkspaceConfig(roots=(tmp_path / "ws",), source=tmp_path / "c"), db, owner="o",
                   discover=lambda r: replace(make_run([]), repositories=(cand,), root=tmp_path / "ws"))
    names = [r[1] for r in rows(db, "proj")]
    assert names == sorted(["agent_instructions", "docs", "openspec_directory", "openspec_specs", "readme", "tests"])


# --- search ---

@pytest.fixture
def reader(db):
    def run(with_gone):
        runs = [
            marked("app", found("readme", "README.md"), found("tests", "tests")),
            marked("bare"),
            marked("cut", found("tests", "tests"), stopped_by="entries"),
            replace(repo("old"), languages=LanguageOutcome(report())), repo("plain"),
            replace(repo("broken"), languages=LanguageOutcome(failed="detection_error")),
            marked("both1", found("docs", "docs"), identity="github.com/acme/both"),
            marked("both2", found("tests", "t"), identity="github.com/acme/both", languages=(("Python", 1),)),
            marked("agents", found("agent_instructions", "AGENTS.md", "pkg/CLAUDE.md", total=2, scope="root", rules=("agent_file",))),
        ]
        return runs + ([marked("gone", found("tests", "tests"))] if with_gone else [])

    store(db, make_run(run(True)))
    store(db, make_run(run(False)), at=T0 + timedelta(minutes=5))
    return db


def search(db, **kw):
    return query.search_projects(db, now=NOW, **kw)


def names(result):
    return sorted(p["display_name"] for p in result["data"]["projects"])


def details(db, name):
    pid = next(p["project_id"] for p in search(db)["data"]["projects"] if p["display_name"] == name)
    return query.get_project(db, pid, now=NOW)["data"]


def code(db, **kw):
    with pytest.raises(IndexStoreError) as caught:
        search(db, **kw)
    return caught.value


def test_detected_is_the_default(reader):
    assert names(search(reader, marker="tests")) == ["app", "both1", "cut"]


def test_not_detected_needs_a_complete_assessed_observation(reader):
    assert names(search(reader, marker="readme", marker_state="not_detected")) == ["agents", "bare", "both1"]


def test_partial_not_assessed_and_failed_match_neither_state(reader):
    for state in ("detected", "not_detected"):
        found_names = names(search(reader, marker=list(MARKERS), marker_state=state))
        assert not {"old", "plain", "broken"} & set(found_names)
    assert "cut" not in names(search(reader, marker="readme", marker_state="not_detected"))
    assert "cut" not in names(search(reader, marker="readme"))


def test_several_names_are_or(reader):
    assert names(search(reader, marker=["docs", "agent_instructions"])) == ["agents", "both1"]


def test_any_active_checkout_matches(reader):
    assert "both1" in names(search(reader, marker="tests")) and "both1" in names(search(reader, marker="docs"))


def test_missing_checkout_does_not_match(reader):
    assert "gone" not in names(search(reader, marker="tests"))


def test_combined_with_a_language_filter(reader):
    assert names(search(reader, marker="tests", language="Python")) == ["both1"]


def test_unknown_name_lists_the_allowed(reader):
    error_ = code(reader, marker="readmee")
    assert error_.code == INVALID_INPUT and "readmee" in str(error_) and "openspec_config" in str(error_)


def test_unknown_state_lists_the_allowed(reader):
    error_ = code(reader, marker="readme", marker_state="maybe")
    assert error_.code == INVALID_INPUT and "not_detected" in str(error_) and "detected" in str(error_)


@pytest.mark.parametrize("kw", [{"marker": 3}, {"marker": ""}, {"marker": []}, {"marker": "readme", "marker_state": 1}])
def test_wrong_types_are_rejected(reader, kw):
    assert code(reader, **kw).code == INVALID_INPUT


def test_state_without_a_marker_is_rejected(reader):
    assert code(reader, marker_state="not_detected").code == INVALID_INPUT


# --- details ---

def markers(db, name):
    return [c["markers"] for c in details(db, name)["checkouts"]]


def states(m):
    return {i["marker"]: i["state"] for i in m["items"]}


def test_complete_observation_states_every_marker(reader):
    (m,) = markers(reader, "app")
    assert (m["status"], m["rules_version"], m["stopped_by"]) == ("complete", VERSION, None)
    assert len(m["items"]) == 8 and states(m)["readme"] == states(m)["tests"] == "detected"
    assert states(m)["docs"] == "not_detected"


def test_evidence_for_detected_markers(reader):
    (m,) = markers(reader, "agents")
    (item,) = [i for i in m["items"] if i["marker"] == "agent_instructions"]
    assert item["total"] == 2 and item["rules"] == ["agent_file"] and item["more"] == 0
    assert item["paths"] == [{"path": "AGENTS.md", "scope": "root"}, {"path": "pkg/CLAUDE.md", "scope": "root"}]


def test_more_counts_matches_beyond_the_stored_paths(db):
    store(db, make_run([marked("a", found("tests", *[f"t{i}" for i in range(20)], total=30))]))
    (item,) = [i for i in markers(db, "a")[0]["items"] if i["marker"] == "tests"]
    assert item["total"] == 30 and len(item["paths"]) == 20 and item["more"] == 10


def test_partial_shows_unknown_for_what_was_not_found(reader):
    (m,) = markers(reader, "cut")
    assert m["status"] == "partial" and m["stopped_by"] == "entries"
    assert states(m)["tests"] == "detected" and states(m)["readme"] == "unknown"
    assert "not_detected" not in states(m).values()


def test_not_assessed_for_old_failed_and_unscanned(reader):
    for name in ("old", "broken", "plain"):
        (m,) = markers(reader, name)
        assert (m["status"], m["rules_version"], m["items"]) == ("not_assessed", None, [])


def test_markers_per_checkout_without_combining(reader):
    data = details(reader, "both1")
    assert sorted(tuple(sorted(k for k, v in states(c["markers"]).items() if v == "detected")) for c in data["checkouts"]) == [("docs",), ("tests",)]
    assert "markers" not in data


def test_missing_checkout_keeps_its_markers(reader):
    (checkout,) = details(reader, "gone")["checkouts"]
    assert checkout["state"] == "missing" and states(checkout["markers"])["tests"] == "detected"


def test_no_absolute_path_in_markers(reader):
    text = str(markers(reader, "agents")) + str(markers(reader, "app"))
    assert "/ws" not in text and ":\\" not in text


def test_queries_do_not_touch_the_filesystem(reader, monkeypatch):
    import os

    def boom(*a, **k):
        raise AssertionError("filesystem walked by a query")

    monkeypatch.setattr(os, "walk", boom)
    search(reader, marker="tests")
    details(reader, "app")
