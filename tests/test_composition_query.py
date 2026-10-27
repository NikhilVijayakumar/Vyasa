import shutil
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest
from test_language_query import report, scanned  # noqa: F401
from test_local_index import LATEST, ROOT, T0, db, make_run, repo, store  # noqa: F401

from vyasa.adapters.sqlite.database import open_index
from vyasa.application import query
from vyasa.domain.file_composition import FileComposition
from vyasa.domain.git_remote import GitRemote
from vyasa.domain.index import INVALID_INPUT, IndexStoreError
from vyasa.domain.languages import LanguageOutcome

NOW = lambda: T0 + timedelta(hours=1)  # noqa: E731


def counted(name, code, doc, other=0, stopped_by=None, identity=None):
    found = (("Python", code),) if code else ()
    scan = scanned(report(found, stopped_by=stopped_by), doc, other)
    remote = GitRemote("origin", "github", "github.com", identity) if identity else None
    return replace(repo(name, remote), languages=LanguageOutcome(scan.languages, composition=scan.composition))


def columns(db, name):
    return [tuple(r) for r in db.execute(
        "SELECT o.code_files, o.documentation_files, o.other_files, o.status FROM language_observations o"
        " JOIN checkouts c USING (checkout_id) WHERE c.path LIKE ? ORDER BY o.observation_id", (f"%{name}",)
    )]


# --- store ---

def test_version_6_index_upgrades_with_null_counts(tmp_path):
    steps = tmp_path / "old"
    steps.mkdir()
    for file in sorted(Path(__file__).parents[1].joinpath("src/vyasa/adapters/sqlite/migrations").glob("000[1-6]_*.sql")):
        shutil.copy(file, steps / file.name)
    old = open_index(tmp_path / "i.sqlite3", migrations=steps)
    store(old, make_run([repo("a")]))
    old.execute(
        "INSERT INTO language_observations (checkout_id, run_id, observed_at, status, types_version) SELECT checkout_id, last_run_id, ?, 'complete', 2 FROM checkouts",
        (T0.isoformat(),),
    )
    old.close()
    new = open_index(tmp_path / "i.sqlite3")
    assert new.execute("PRAGMA user_version").fetchone()[0] == LATEST >= 7
    assert [tuple(r) for r in new.execute("SELECT code_files, documentation_files, other_files FROM language_observations")] == [(None, None, None)]


def test_counts_are_stored_with_the_observation(db):
    store(db, make_run([counted("a", 3, 2, 1)]))
    assert columns(db, "a") == [(3, 2, 1, "complete")]


def test_partial_walk_stores_lower_bounds(db):
    store(db, make_run([counted("a", 1, 2, stopped_by="entries")]))
    assert columns(db, "a") == [(1, 2, 0, "partial")]


def test_failed_observation_has_no_counts(db):
    store(db, make_run([replace(repo("a"), languages=LanguageOutcome(failed="detection_error"))]))
    assert columns(db, "a") == [(None, None, None, "failed")]


def test_report_without_counts_stores_null(db):
    store(db, make_run([replace(repo("a"), languages=LanguageOutcome(report()))]))
    assert columns(db, "a") == [(None, None, None, "complete")]


def test_retention_keeps_two_observations_with_their_counts(db):
    for i, (code, doc) in enumerate([(1, 1), (2, 2), (3, 3)]):
        store(db, make_run([counted("a", code, doc)]), at=T0 + timedelta(minutes=i))
    assert columns(db, "a") == [(2, 2, 0, "complete"), (3, 3, 0, "complete")]


# --- search ---

@pytest.fixture
def reader(db):
    def run(with_gone):
        runs = [
            counted("docs", 0, 4), counted("codey", 3, 1), counted("cut", 0, 2, stopped_by="entries"),
            replace(repo("old"), languages=LanguageOutcome(report())), repo("plain"),
            replace(repo("broken"), languages=LanguageOutcome(failed="detection_error")),
            counted("both1", 0, 5, identity="github.com/acme/both"), counted("both2", 2, 0, identity="github.com/acme/both"),
        ]
        return runs + ([counted("gone", 0, 7)] if with_gone else [])

    store(db, make_run(run(True)))
    store(db, make_run(run(False)), at=T0 + timedelta(minutes=5))  # "gone" is now missing
    return db


def search(db, **kw):
    return query.search_projects(db, now=NOW, **kw)


def names(result):
    return sorted(p["display_name"] for p in result["data"]["projects"])


def details(db, name):
    pid = next(p["project_id"] for p in search(db)["data"]["projects"] if p["display_name"] == name)
    return query.get_project(db, pid, now=NOW)["data"]


def test_documentation_only_true(reader):
    assert names(search(reader, documentation_only=True)) == ["both1", "docs"]


def test_documentation_only_false(reader):
    assert names(search(reader, documentation_only=False)) == ["both1", "codey"]


def test_any_active_checkout_matches_both_values(reader):
    assert "both1" in names(search(reader, documentation_only=True)) and "both1" in names(search(reader, documentation_only=False))


def test_partial_not_counted_and_failed_match_neither(reader):
    for value in (True, False):
        found = names(search(reader, documentation_only=value))
        assert not {"cut", "old", "plain", "broken"} & set(found)


def test_missing_checkout_does_not_match(reader):
    assert "gone" not in names(search(reader, documentation_only=True))


def test_combined_with_a_language_filter(reader):
    assert names(search(reader, documentation_only=False, language="Python")) == ["both1", "codey"]
    assert names(search(reader, documentation_only=True, language="Python")) == ["both1"]


@pytest.mark.parametrize("value", ["yes", 1, 0, [True], ""])
def test_non_boolean_is_rejected(reader, value):
    with pytest.raises(IndexStoreError) as error:
        search(reader, documentation_only=value)
    assert error.value.code == INVALID_INPUT and "documentation_only" in str(error.value)


# --- details ---

def composition(db, name):
    return [c["composition"] for c in details(db, name)["checkouts"]]


def test_counts_per_checkout_without_a_total(reader):
    data = details(reader, "both1")
    assert sorted((c["composition"]["code"], c["composition"]["documentation"]) for c in data["checkouts"]) == [(0, 5), (2, 0)]
    assert "composition" not in data


def test_counts_agree_and_indicator_follows(reader):
    (c,) = composition(reader, "docs")
    assert (c["status"], c["code"], c["documentation"], c["other"], c["total"], c["documentation_only"]) == ("complete", 0, 4, 0, 4, True)
    (c,) = composition(reader, "codey")
    assert c["total"] == c["code"] + c["documentation"] + c["other"] == 4 and c["documentation_only"] is False


def test_partial_shows_bound_and_unknown_indicator(reader):
    (c,) = composition(reader, "cut")
    assert (c["status"], c["stopped_by"], c["documentation"], c["documentation_only"]) == ("partial", "entries", 2, None)


def test_not_counted_is_not_zero(reader):
    empty = {"status": "not_counted", "stopped_by": None, "observed_at": None, "code": None, "documentation": None,
             "other": None, "total": None, "documentation_only": None}
    for name in ("old", "plain"):
        assert composition(reader, name)[0] == empty
    failed = composition(reader, "broken")[0]
    assert failed["status"] == "not_counted" and failed["code"] is None and failed["documentation_only"] is None


def test_missing_checkout_keeps_its_counts(reader):
    (checkout,) = details(reader, "gone")["checkouts"]
    assert checkout["state"] == "missing" and checkout["composition"]["documentation"] == 7


def test_no_path_in_composition(reader):
    assert "/ws" not in str(composition(reader, "docs"))


def test_queries_do_not_touch_the_filesystem(reader, monkeypatch):
    import os

    def boom(*a, **k):
        raise AssertionError("filesystem walked by a query")

    monkeypatch.setattr(os, "walk", boom)
    search(reader, documentation_only=True)
    details(reader, "docs")
