import shutil
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest
from test_local_index import LATEST, ROOT, T0, db, make_run, repo, store  # noqa: F401

from vyasa.adapters.sqlite.database import open_index
from vyasa.application.indexing.scan import scan_workspace
from vyasa.application.scanning.file_composition import default_file_types
from vyasa.domain.discovery import COMPLETE, PARTIAL
from vyasa.domain.file_composition import Evidence, WalkLimits
from vyasa.domain.languages import LanguageOutcome, LanguageReport
from vyasa.domain.workspace_config import WorkspaceConfig


def report(found=(("Python", 2),), declared=(), stopped_by=None, version=2):
    return LanguageReport(tuple(found), tuple(declared), stopped_by, Evidence(version, (), WalkLimits()))


def with_languages(name, outcome, **kw):
    return replace(repo(name, **kw), languages=outcome)


def seen(name, found=(("Python", 2),), declared=(), stopped_by=None):
    return with_languages(name, LanguageOutcome(report(found, declared, stopped_by), seconds=0.25))


def observations(db, name):
    return db.execute(
        "SELECT o.observation_id, o.status, o.stopped_by, o.reason, o.types_version, o.duration_ms FROM language_observations o"
        " JOIN checkouts c USING (checkout_id) WHERE c.path LIKE ? ORDER BY o.observation_id",
        (f"%{name}",),
    ).fetchall()


def rows(db, observation_id):
    return [tuple(r) for r in db.execute(
        "SELECT label, status, files FROM checkout_languages WHERE observation_id = ? ORDER BY label, status", (observation_id,)
    )]


# --- migration ---

def test_version_5_index_upgrades_with_data_intact(tmp_path):
    steps = tmp_path / "old"
    steps.mkdir()
    for file in sorted(Path(__file__).parents[1].joinpath("src/vyasa/adapters/sqlite/migrations").glob("000[1-5]_*.sql")):
        shutil.copy(file, steps / file.name)
    old = open_index(tmp_path / "i.sqlite3", migrations=steps)
    store(old, make_run([repo("a")]))
    old.close()
    new = open_index(tmp_path / "i.sqlite3")
    assert new.execute("PRAGMA user_version").fetchone()[0] == LATEST >= 6
    assert new.execute("SELECT count(*) FROM checkouts").fetchone()[0] == 1
    assert new.execute("SELECT count(*) FROM language_observations").fetchone()[0] == 0


# --- store ---

def test_scan_result_is_stored_with_rows(db):
    store(db, make_run([seen("a", (("Python", 2), ("Rust", 1)), declared=("Rust",))]))
    (obs,) = observations(db, "a")
    assert (obs["status"], obs["stopped_by"], obs["reason"], obs["types_version"], obs["duration_ms"]) == ("complete", None, None, 2, 250)
    assert rows(db, obs["observation_id"]) == [
        ("Python", "files_detected", 2), ("Rust", "declared", None), ("Rust", "files_detected", 1)
    ]


def test_candidate_without_outcome_is_not_observed(db):
    store(db, make_run([repo("a")]))
    assert observations(db, "a") == []


def test_third_store_keeps_two_observations(db):
    for i, found in enumerate([(("Go", 1),), (("Python", 2),), (("Rust", 3),)]):
        store(db, make_run([seen("a", found)]), at=T0 + timedelta(minutes=i))
    obs = observations(db, "a")
    assert len(obs) == 2
    assert [rows(db, o["observation_id"])[0][0] for o in obs] == ["Python", "Rust"]
    assert db.execute("SELECT count(*) FROM checkout_languages").fetchone()[0] == 2


def test_unchanged_tree_still_gets_a_new_current_observation(db):
    store(db, make_run([seen("a")]))
    store(db, make_run([seen("a")]), at=T0 + timedelta(minutes=1))
    one, two = observations(db, "a")
    assert two["observation_id"] > one["observation_id"] and rows(db, one["observation_id"]) == rows(db, two["observation_id"])


def test_partial_rescan_is_current_and_keeps_previous(db):
    store(db, make_run([seen("a")]))
    store(db, make_run([seen("a", found=(), stopped_by="entries")]), at=T0 + timedelta(minutes=1))
    previous, current = observations(db, "a")
    assert (current["status"], current["stopped_by"]) == ("partial", "entries")
    assert rows(db, current["observation_id"]) == []
    assert rows(db, previous["observation_id"]) == [("Python", "files_detected", 2)]


def test_failed_outcome_stores_a_reason_and_no_rows(db):
    store(db, make_run([with_languages("a", LanguageOutcome(failed="detection_error"))]))
    (obs,) = observations(db, "a")
    assert (obs["status"], obs["reason"]) == ("failed", "detection_error")
    assert rows(db, obs["observation_id"]) == []


def test_unreached_checkout_keeps_its_observations(db):
    store(db, make_run([seen("a")]))
    store(db, make_run([], status=COMPLETE), at=T0 + timedelta(minutes=1))  # a is now missing
    assert len(observations(db, "a")) == 1


# --- scan ---

def config(tmp_path):
    return WorkspaceConfig(roots=(ROOT,), source=tmp_path / "c.toml")


def discover_two(_root):
    return make_run([repo("good"), repo("bad")])


def test_scan_attaches_languages_per_eligible_candidate(db, tmp_path):
    seen_paths = []

    def detect(path):
        seen_paths.append(path.name)
        return report(found=(("Go", 1),))

    (result,) = scan_workspace(config(tmp_path), db, owner="o", discover=discover_two, detect=detect)
    assert sorted(seen_paths) == ["bad", "good"]
    assert result.run.status == COMPLETE
    assert rows(db, observations(db, "good")[0]["observation_id"]) == [("Go", "files_detected", 1)]


def test_failing_detector_is_isolated_and_marks_run_partial(db, tmp_path):
    def detect(path):
        if path.name == "bad":
            raise RuntimeError("secret detail")
        return report()

    (result,) = scan_workspace(config(tmp_path), db, owner="o", discover=discover_two, detect=detect)
    assert result.stored.status == "partial"
    (bad,) = observations(db, "bad")
    assert (bad["status"], bad["reason"]) == ("failed", "detection_error")
    assert "secret" not in str(bad["reason"])
    assert observations(db, "good")[0]["status"] == "complete"
    assert any(w.reason == "language_detection" for w in result.run.warnings)


def test_partial_report_is_stored_partial(db, tmp_path):
    scan_workspace(config(tmp_path), db, owner="o", discover=discover_two, detect=lambda p: report(stopped_by="time"))
    assert observations(db, "good")[0]["stopped_by"] == "time"


def test_scan_does_not_detect_ineligible_candidates(db, tmp_path):
    called = []
    run = replace(make_run([repo("a")]), issues=(replace(repo("x"), outcome="inaccessible"),))
    scan_workspace(config(tmp_path), db, owner="o", discover=lambda r: run, detect=lambda p: called.append(p) or report())
    assert [p.name for p in called] == ["a"]
