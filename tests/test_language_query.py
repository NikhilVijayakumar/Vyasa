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
from vyasa.domain.file_composition import Evidence, FileComposition, WalkLimits
from vyasa.domain.languages import CheckoutScan, LanguageOutcome, LanguageReport
from vyasa.domain.workspace_config import WorkspaceConfig


def report(found=(("Python", 2),), declared=(), stopped_by=None, version=2):
    return LanguageReport(tuple(found), tuple(declared), stopped_by, Evidence(version, (), WalkLimits()))


def scanned(r, doc=0, other=0):
    """A CheckoutScan whose code count is the sum of the report's files_detected."""
    code = sum(n for _, n in r.files_detected)
    return CheckoutScan(FileComposition(code, doc, other, r.stopped_by, r.evidence), r)


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
        return scanned(report(found=(("Go", 1),)))

    (result,) = scan_workspace(config(tmp_path), db, owner="o", discover=discover_two, detect=detect)
    assert sorted(seen_paths) == ["bad", "good"]
    assert result.run.status == COMPLETE
    assert rows(db, observations(db, "good")[0]["observation_id"]) == [("Go", "files_detected", 1)]


def test_failing_detector_is_isolated_and_marks_run_partial(db, tmp_path):
    def detect(path):
        if path.name == "bad":
            raise RuntimeError("secret detail")
        return scanned(report())

    (result,) = scan_workspace(config(tmp_path), db, owner="o", discover=discover_two, detect=detect)
    assert result.stored.status == "partial"
    (bad,) = observations(db, "bad")
    assert (bad["status"], bad["reason"]) == ("failed", "detection_error")
    assert "secret" not in str(bad["reason"])
    assert observations(db, "good")[0]["status"] == "complete"
    assert any(w.reason == "language_detection" for w in result.run.warnings)


def test_partial_report_is_stored_partial(db, tmp_path):
    scan_workspace(config(tmp_path), db, owner="o", discover=discover_two, detect=lambda p: scanned(report(stopped_by="time")))
    assert observations(db, "good")[0]["stopped_by"] == "time"


def test_scan_does_not_detect_ineligible_candidates(db, tmp_path):
    called = []
    run = replace(make_run([repo("a")]), issues=(replace(repo("x"), outcome="inaccessible"),))
    scan_workspace(config(tmp_path), db, owner="o", discover=lambda r: run, detect=lambda p: called.append(p) or scanned(report()))
    assert [p.name for p in called] == ["a"]


# --- search ---

from vyasa.application import query  # noqa: E402
from vyasa.domain.git_remote import GitRemote  # noqa: E402
from vyasa.domain.index import INVALID_INPUT, IndexStoreError  # noqa: E402

NOW = lambda: T0 + timedelta(hours=1)  # noqa: E731


def remote(identity):
    return GitRemote("origin", "github", "github.com", identity)


def lang(name, found=(), declared=(), stopped_by=None, identity=None):
    outcome = LanguageOutcome(report(found, declared, stopped_by))
    return replace(repo(name, remote(identity) if identity else None), languages=outcome)


@pytest.fixture
def reader(db):
    store(db, make_run([
        lang("py", (("Python", 3),)),
        lang("decl", (), ("Python",)),
        lang("rust", (("Rust", 4),), ("Rust",)),
        lang("both1", (("Go", 2),), identity="github.com/acme/both"),
        lang("both2", (("Python", 1),), identity="github.com/acme/both"),
        lang("gone", (("Go", 9),)),
        lang("cut", (("Rust", 1),), stopped_by="entries"),
        repo("plain"),
    ]))
    store(db, make_run([r for r in [
        lang("py", (("Python", 3),)), lang("decl", (), ("Python",)), lang("rust", (("Rust", 4),), ("Rust",)),
        lang("both1", (("Go", 2),), identity="github.com/acme/both"), lang("both2", (("Python", 1),), identity="github.com/acme/both"),
        lang("cut", (("Rust", 1),), stopped_by="entries"), repo("plain"),
    ]]), at=T0 + timedelta(minutes=5))  # "gone" is now missing
    return db


def search(db, **kw):
    return query.search_projects(db, now=NOW, **kw)


def names(result):
    return sorted(p["display_name"] for p in result["data"]["projects"])


def code(fn, *a, **kw):
    with pytest.raises(IndexStoreError) as e:
        fn(*a, **kw)
    return e.value


def test_search_by_one_language(reader):
    assert names(search(reader, language="Python")) == ["both1", "decl", "py"]


def test_search_several_labels_is_or(reader):
    assert names(search(reader, language=["Rust", "Go"])) == ["both1", "cut", "rust"]


def test_label_case_is_ignored(reader):
    assert names(search(reader, language="python")) == names(search(reader, language="Python"))


def test_language_combines_with_other_filters_by_and(reader):
    assert names(search(reader, language="Python", state="active", query="py")) == ["py"]


def test_status_files_detected_excludes_a_bare_declaration(reader):
    assert names(search(reader, language="Python", language_status="files_detected")) == ["both1", "py"]


def test_status_declared_includes_it(reader):
    result = search(reader, language="Python", language_status="declared")
    assert names(result) == ["decl"]
    (item,) = result["data"]["projects"]
    assert item["language_matches"] == [{"label": "Python", "statuses": ["declared"]}]


def test_both_statuses_reported_when_both_match(reader):
    (item,) = [p for p in search(reader, language="Rust")["data"]["projects"] if p["display_name"] == "rust"]
    assert item["language_matches"] == [{"label": "Rust", "statuses": ["declared", "files_detected"]}]


def test_unknown_label_lists_allowed_labels(reader):
    error = code(search, reader, language="Pyhton")
    assert error.code == INVALID_INPUT and "Pyhton" in str(error) and "Python" in str(error) and "Rust" in str(error)


def test_unknown_status_is_rejected_listing_allowed(reader):
    error = code(search, reader, language="Python", language_status="maybe")
    assert error.code == INVALID_INPUT and "files_detected" in str(error) and "declared" in str(error)


@pytest.mark.parametrize("value", [["declared", 3], 3])
def test_wrong_status_type_is_rejected(reader, value):
    assert code(search, reader, language="Python", language_status=value).code == INVALID_INPUT


@pytest.mark.parametrize("value", [3, [1], ""])
def test_bad_language_type_is_rejected(reader, value):
    assert code(search, reader, language=value).code == INVALID_INPUT


def test_any_present_checkout_matches(reader):
    assert "both1" in names(search(reader, language="Go"))  # only one of the two checkouts holds Go


def test_missing_checkout_does_not_match(reader):
    assert "gone" not in names(search(reader, language="Go"))


def test_partial_observation_matches_positives(reader):
    assert "cut" in names(search(reader, language="Rust"))


def test_items_list_the_union_of_labels_without_a_filter(reader):
    items = {p["display_name"]: p for p in search(reader)["data"]["projects"]}
    assert items["both1"]["languages"] == ["Go", "Python"]
    assert items["plain"]["languages"] == []
    assert "language_matches" not in items["plain"]


def test_filter_value_is_bound_not_executed(reader):
    assert code(search, reader, language="x'; DROP TABLE projects; --").code == INVALID_INPUT
    assert reader.execute("SELECT count(*) FROM projects").fetchone()[0] > 0


# --- details ---

def details(db, name):
    pid = next(p["project_id"] for p in search(db)["data"]["projects"] if p["display_name"] == name)
    return query.get_project(db, pid, now=NOW)["data"]


def test_details_give_languages_per_checkout_without_a_total(reader):
    data = details(reader, "both1")
    by_state = sorted(c["languages"]["items"][0]["label"] for c in data["checkouts"])
    assert by_state == ["Go", "Python"]
    assert all(set(c["languages"]) >= {"status", "stopped_by", "observed_at", "types_version", "items"} for c in data["checkouts"])
    assert "languages" not in data and all("total" not in c["languages"] for c in data["checkouts"])


def test_item_shape(reader):
    (checkout,) = details(reader, "rust")["checkouts"]
    assert checkout["languages"]["status"] == "complete"
    assert checkout["languages"]["items"] == [
        {"label": "Rust", "status": "declared", "files": None}, {"label": "Rust", "status": "files_detected", "files": 4}
    ]


def test_partial_observation_shows_its_bound(reader):
    languages = details(reader, "cut")["checkouts"][0]["languages"]
    assert (languages["status"], languages["stopped_by"]) == ("partial", "entries")


def test_never_observed_is_not_empty(reader):
    languages = details(reader, "plain")["checkouts"][0]["languages"]
    assert languages == {"status": "not_observed", "stopped_by": None, "observed_at": None, "types_version": None, "items": []}


def test_failed_observation_shows_a_fixed_reason(db):
    store(db, make_run([replace(repo("f"), languages=LanguageOutcome(failed="detection_error"))]))
    languages = details(db, "f")["checkouts"][0]["languages"]
    assert (languages["status"], languages["reason"], languages["items"]) == ("failed", "detection_error", [])


def test_missing_checkout_keeps_its_last_observation(reader):
    (checkout,) = details(reader, "gone")["checkouts"]
    assert checkout["state"] == "missing"
    assert checkout["languages"]["items"] == [{"label": "Go", "status": "files_detected", "files": 9}]


def test_profile_technologies_are_untouched(db):
    from vyasa.domain.profile import ProfileResult

    candidate = replace(repo("p"), languages=LanguageOutcome(report((("Python", 1),))),
                        profile=ProfileResult("valid", {"technologies": ["Rust"]}))
    store(db, make_run([candidate]))
    data = details(db, "p")
    assert "Rust" in str(data["profile"]) and "Rust" not in str(data["checkouts"][0]["languages"])
    assert data["checkouts"][0]["languages"]["items"][0]["label"] == "Python"


def test_queries_do_not_touch_the_filesystem(reader, monkeypatch):
    import os

    def boom(*a, **k):
        raise AssertionError("filesystem walked by a query")

    monkeypatch.setattr(os, "walk", boom)
    monkeypatch.setattr("vyasa.application.scanning.languages.detect_languages", boom)
    search(reader, language="Python")
    details(reader, "py")


def test_no_path_in_languages(reader):
    for checkout in details(reader, "py")["checkouts"]:
        assert "path" not in checkout and "/ws" not in str(checkout["languages"])
