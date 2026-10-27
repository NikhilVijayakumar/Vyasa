import json
import sqlite3
from pathlib import Path

import pytest
from test_local_index import MIGRATIONS, ROOT, T0, db, make_run, repo, states, store  # noqa: F401

from vyasa.adapters.sqlite import projects
from vyasa.adapters.sqlite.database import open_index
from vyasa.domain.discovery import Candidate
from vyasa.domain.git_remote import GitRemote


def remote(identity, host="github.com"):
    return GitRemote("origin", "github", host, identity)


def rows(db):
    return projects.list_projects(db)


def project(db, name):
    return next(r for r in rows(db) if Path(r["path"]).name == name)


# -- creation -----------------------------------------------------------------------------------


def test_repository_with_a_remote_is_resolved_with_an_alias(db):
    store(db, make_run([repo("a", remote("github.com/o/r"))]))
    row = project(db, "a")
    assert (row["identity_status"], row["identity_source"]) == ("resolved", "remote")
    assert projects.list_aliases(db, row["project_id"]) == ["github.com/o/r"]
    assert [e["kind"] for e in projects.list_events(db, row["project_id"])] == ["created"]


@pytest.mark.parametrize("remote_value", [None, GitRemote("origin", "local", None, None)])
def test_repository_without_a_usable_remote_is_provisional(db, remote_value):
    store(db, make_run([repo("a", remote_value)]))
    row = project(db, "a")
    assert (row["identity_status"], row["identity_source"]) == ("provisional", "path")
    assert projects.list_aliases(db, row["project_id"]) == []
    assert len(projects.list_events(db, row["project_id"])) == 1


# -- rediscovery ----------------------------------------------------------------------------------


def test_rescan_adds_no_event_and_no_project(db):
    run = lambda: make_run([repo("a", remote("github.com/o/r"))])
    store(db, run())
    pid = project(db, "a")["project_id"]
    store(db, run())
    assert len(rows(db)) == 1 and len(projects.list_events(db, pid)) == 1


def test_moved_repository_keeps_its_project(db):
    store(db, make_run([repo("old", remote("github.com/o/r"))]))
    pid = project(db, "old")["project_id"]
    result = store(db, make_run([repo("new", remote("github.com/o/r"))]))
    assert result.counts["attached"] == 1 and result.counts["missing"] == 1
    got = {Path(r["path"]).name: (r["project_id"], r["state"]) for r in rows(db)}
    assert got == {"old": (pid, "active"), "new": (pid, "active")}
    assert db.execute("SELECT state FROM checkouts WHERE path LIKE '%old'").fetchone()[0] == "missing"
    assert db.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 1
    assert len(projects.list_events(db, pid)) == 1


def test_project_is_missing_only_when_no_checkout_is_active(db):
    store(db, make_run([repo("old", remote("github.com/o/r"))]))
    store(db, make_run([repo("new", remote("github.com/o/r"))]))
    assert {r["state"] for r in rows(db)} == {"active"}
    store(db, make_run())
    assert {r["state"] for r in rows(db)} == {"missing"}


def test_moved_provisional_repository_is_a_new_project(db):
    store(db, make_run([repo("old")]))
    store(db, make_run([repo("new")]))
    assert states(db) == {"old": "missing", "new": "active"}
    assert db.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 2


# -- later evidence ---------------------------------------------------------------------------------


def test_remote_added_resolves_the_project(db):
    store(db, make_run([repo("a")]))
    pid = project(db, "a")["project_id"]
    store(db, make_run([repo("a", remote("github.com/o/r"))]))
    row = project(db, "a")
    assert row["project_id"] == pid and row["identity_status"] == "resolved"
    assert projects.list_aliases(db, pid) == ["github.com/o/r"]
    assert [e["kind"] for e in projects.list_events(db, pid)] == ["created", "alias_added"]


def test_renamed_remote_keeps_both_aliases(db):
    store(db, make_run([repo("a", remote("github.com/o/old"))]))
    pid = project(db, "a")["project_id"]
    store(db, make_run([repo("a", remote("github.com/o/new"))]))
    assert db.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 1
    assert sorted(projects.list_aliases(db, pid)) == ["github.com/o/new", "github.com/o/old"]


def test_removed_remote_keeps_status_and_aliases(db):
    store(db, make_run([repo("a", remote("github.com/o/r"))]))
    pid = project(db, "a")["project_id"]
    store(db, make_run([repo("a")]))
    row = project(db, "a")
    assert row["identity_status"] == "resolved" and projects.list_aliases(db, pid) == ["github.com/o/r"]


# -- conflict ------------------------------------------------------------------------------------------


def test_conflicting_alias_and_path_change_nothing_but_an_event(db):
    store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/b"))]))
    a, b = project(db, "a")["project_id"], project(db, "b")["project_id"]
    result = store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/a"))]))
    assert result.counts["conflicts"] == 1
    assert project(db, "b")["project_id"] == b and project(db, "a")["project_id"] == a
    assert projects.list_aliases(db, b) == ["h/o/b"]
    assert db.execute("SELECT remote_identity FROM checkouts WHERE path LIKE '%b'").fetchone()[0] == "h/o/b"
    kinds = [e["kind"] for e in projects.list_events(db, b)]
    assert kinds == ["created", "identity_conflict", "flagged"]
    store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/a"))]))
    assert len(projects.list_events(db, b)) == 3


def test_conflicting_checkout_is_not_marked_missing(db):
    store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/b"))]))
    store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/a"))]))
    assert states(db) == {"a": "active", "b": "active"}


def test_events_hold_no_path_or_url(db):
    store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/b"))]))
    store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/a"))]))
    for event in db.execute("SELECT * FROM identity_events"):
        assert event["project_id"] and event["run_id"] and event["at"]
        text = event["detail"]
        assert "/ws" not in text and "://" not in text and "@" not in text
        assert isinstance(json.loads(text), dict)


# -- migration -----------------------------------------------------------------------------------------


def _schema1(tmp_path):
    folder = tmp_path / "v1"
    folder.mkdir()
    (folder / "0001_initial.sql").write_text((MIGRATIONS / "0001_initial.sql").read_text())
    path = tmp_path / "index.sqlite3"
    connection = open_index(path, migrations=folder)
    for pid, name, identity, cid in (("p1", "a", "h/o/a", 1), ("p2", "b", None, 2), ("p3", "c", "h/o/a", 3)):
        connection.execute(
            "INSERT INTO projects VALUES (?, ?, 'active', 't', 't', 't')", (pid, name)
        )
        connection.execute(
            "INSERT INTO checkouts (checkout_id, project_id, path, path_key, root, remote_identity, state,"
            " first_seen_at, last_seen_at) VALUES (?, ?, ?, ?, '/ws', ?, 'active', ?, 't')",
            (cid, pid, f"/ws/{name}", f"/ws/{name}", identity, f"2026-01-0{cid}"),
        )
    connection.close()
    return path


def test_migration_backfills_aliases_and_keeps_projects(tmp_path):
    path = _schema1(tmp_path)
    connection = open_index(path)
    got = {r["display_name"]: (r["identity_status"], r["identity_source"]) for r in rows(connection)}
    assert got == {"a": ("resolved", "remote"), "b": ("provisional", "path"), "c": ("provisional", "path")}
    assert projects.list_aliases(connection, "p1") == ["h/o/a"]
    assert projects.list_aliases(connection, "p3") == []
    assert connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 3
    assert (tmp_path / "index.sqlite3.bak-v1").is_file()
    connection.close()


@pytest.mark.parametrize("status", ["ambiguous", "unavailable", "none"])
def test_unusable_remote_is_a_local_project_without_a_flag(db, status):
    candidate = Candidate(ROOT / "a", "eligible", kind="repository", git=".", remote=None, remote_status=status)
    store(db, make_run([candidate]))
    row = project(db, "a")
    assert (row["identity_status"], row["identity_source"], row["remote_status"]) == ("provisional", "path", status)
    assert db.execute("SELECT COUNT(*) FROM review_flags").fetchone()[0] == 0
    store(db, make_run([Candidate(ROOT / "moved", "eligible", kind="repository", git=".", remote_status=status)]))
    assert db.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 2  # a move is a new project; nothing is linked
