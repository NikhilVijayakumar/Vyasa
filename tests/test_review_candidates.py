import json
from datetime import timedelta
from pathlib import Path

import pytest
from test_local_index import MIGRATIONS, ROOT, T0, db, make_run, repo, store  # noqa: F401

from vyasa.adapters.sqlite import projects, review
from vyasa.adapters.sqlite.database import open_index
from vyasa.domain.discovery import INACCESSIBLE, Candidate
from vyasa.domain.git_remote import GitRemote
from vyasa.domain.index import CANDIDATE_NOT_FOUND, INVALID_DECISION, IndexStoreError

DUP = "duplicate_checkout"


def remote(identity):
    return GitRemote("origin", "github", "github.com", identity)


def clones(*names):
    return make_run([repo(n, remote("h/o/r")) for n in names])


def pid(db, name):
    return next(r["project_id"] for r in projects.list_projects(db) if Path(r["path"]).name == name)


def decide(db, project, status, note=None, kind=DUP, at=T0):
    review.decide(db, project, kind, status, note, now=at)


# -- explainable ------------------------------------------------------------------------------------


def test_duplicate_candidate_is_explained(db):
    store(db, clones("a", "b"))
    [c] = review.list_candidates(db)
    assert (c["kind"], c["rule"], c["confidence"], c["review_status"]) == (DUP, "same_remote_identity", "high", "open")
    assert "checkout" in c["criteria"] and json.loads(c["evidence"])["active_checkouts"] == 2


def test_unresolved_candidate_is_explained(db):
    store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/b"))]))
    store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/a"))]))
    [c] = review.list_candidates(db)
    assert (c["kind"], c["rule"], c["confidence"]) == ("identity_unresolved", "path_remote_conflict", "low")
    assert set(json.loads(c["evidence"])) == {"alias", "alias_owner", "path_project"}


def test_cleared_flags_are_not_candidates(db):
    store(db, clones("a", "b"))
    store(db, clones("a"))
    assert review.list_candidates(db) == []


# -- decisions ----------------------------------------------------------------------------------------


def test_dismiss_with_a_note(db):
    store(db, clones("a", "b"))
    decide(db, pid(db, "a"), "dismissed", "two worktrees on purpose")
    [c] = review.list_candidates(db)
    assert (c["review_status"], c["note"], c["decided_at"]) == ("dismissed", "two worktrees on purpose", T0.isoformat())
    assert review.list_candidates(db, "open") == [] and len(review.list_candidates(db, "dismissed")) == 1


def test_change_of_mind(db):
    store(db, clones("a", "b"))
    decide(db, pid(db, "a"), "confirmed")
    decide(db, pid(db, "a"), "open")
    assert review.list_candidates(db)[0]["review_status"] == "open"
    assert db.execute("SELECT COUNT(*) FROM review_decisions").fetchone()[0] == 1


def test_unknown_candidate_writes_nothing(db):
    store(db, clones("a"))
    with pytest.raises(IndexStoreError) as error:
        decide(db, pid(db, "a"), "dismissed")
    assert error.value.code == CANDIDATE_NOT_FOUND
    assert db.execute("SELECT COUNT(*) FROM review_decisions").fetchone()[0] == 0


@pytest.mark.parametrize("status,note", [("later", None), ("dismissed", "x" * 501)])
def test_invalid_decision_writes_nothing(db, status, note):
    store(db, clones("a", "b"))
    with pytest.raises(IndexStoreError) as error:
        decide(db, pid(db, "a"), status, note)
    assert error.value.code == INVALID_DECISION
    assert db.execute("SELECT COUNT(*) FROM review_decisions").fetchone()[0] == 0


def test_a_note_of_the_maximum_length_is_accepted(db):
    store(db, clones("a", "b"))
    decide(db, pid(db, "a"), "dismissed", "x" * 500)
    assert len(review.list_candidates(db)[0]["note"]) == 500


# -- decisions follow the evidence ---------------------------------------------------------------------


def test_changed_evidence_reopens_the_candidate(db):
    store(db, clones("a", "b"))
    decide(db, pid(db, "a"), "dismissed")
    store(db, clones("a", "b", "c"))
    [c] = review.list_candidates(db)
    assert json.loads(c["evidence"])["active_checkouts"] == 3
    assert (c["review_status"], c["note"]) == ("open", None)


def test_same_condition_returning_keeps_the_decision(db):
    store(db, clones("a", "b"))
    decide(db, pid(db, "a"), "dismissed", "ok")
    store(db, clones("a"))
    assert review.list_candidates(db) == []
    store(db, clones("a", "b"))
    assert review.list_candidates(db)[0]["review_status"] == "dismissed"


# -- nothing is changed -----------------------------------------------------------------------------------


def snapshot(db):
    tables = ("projects", "checkouts", "project_aliases", "review_flags", "identity_events", "scan_runs", "index_lock")
    return {t: db.execute(f"SELECT * FROM {t} ORDER BY 1, 2").fetchall() for t in tables}


def test_a_decision_changes_only_its_own_table(db):
    store(db, clones("a", "b"))
    before = [[tuple(r) for r in rows] for rows in snapshot(db).values()]
    decide(db, pid(db, "a"), "confirmed", "same repo")
    after = [[tuple(r) for r in rows] for rows in snapshot(db).values()]
    assert before == after
    assert db.execute("SELECT COUNT(*) FROM review_decisions").fetchone()[0] == 1


def test_inaccessible_project_is_not_a_candidate(db):
    store(db, make_run([repo("a")]))
    store(db, make_run(issues=[Candidate(ROOT / "a", INACCESSIBLE, reason="unreadable")], status="partial"))
    assert db.execute("SELECT state FROM projects").fetchone()[0] == "inaccessible"
    assert review.list_candidates(db) == []


def test_long_unseen_project_is_not_a_candidate(db):
    store(db, make_run([repo("a")]), at=T0)
    store(db, make_run([repo("b")]), at=T0 + timedelta(days=400))
    assert review.list_candidates(db) == []


# -- migration ---------------------------------------------------------------------------------------------


def test_migration_adds_an_empty_decisions_table(tmp_path):
    folder = tmp_path / "v3"
    folder.mkdir()
    for file in MIGRATIONS.glob("000[123]_*.sql"):
        (folder / file.name).write_text(file.read_text())
    path = tmp_path / "index.sqlite3"
    open_index(path, migrations=folder).close()
    c = open_index(path)
    assert c.execute("SELECT COUNT(*) FROM review_decisions").fetchone()[0] == 0
    assert (tmp_path / "index.sqlite3.bak-v3").is_file()
    c.close()
