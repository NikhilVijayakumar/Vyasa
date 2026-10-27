import json
from pathlib import Path

from test_local_index import MIGRATIONS, ROOT, T0, db, make_run, repo, states, store  # noqa: F401

from vyasa.adapters.sqlite import projects
from vyasa.adapters.sqlite.database import open_index
from vyasa.domain.git_remote import GitRemote


def remote(identity):
    return GitRemote("origin", "github", "github.com", identity)


def pid(db, name):
    return next(r["project_id"] for r in projects.list_projects(db) if Path(r["path"]).name == name)


def flags(db, state="open"):
    return [(f["kind"], json.loads(f["evidence"])) for f in projects.list_flags(db, state)]


def kinds(db, project):
    return [e["kind"] for e in projects.list_events(db, project)]


def two_clones(extra=()):
    return make_run([repo("a", remote("h/o/r")), repo("b", remote("h/o/r")), *extra])


# -- duplicate checkouts ------------------------------------------------------------------------------


def test_two_clones_are_flagged_with_rule_and_evidence(db):
    store(db, two_clones())
    assert db.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 1
    assert flags(db) == [("duplicate_checkout", {"rule": "same_remote_identity", "aliases": ["h/o/r"], "active_checkouts": 2})]
    assert kinds(db, pid(db, "a")) == ["created", "flagged"]


def test_moved_clone_is_not_flagged(db):
    store(db, make_run([repo("old", remote("h/o/r"))]))
    store(db, make_run([repo("new", remote("h/o/r"))]))
    assert flags(db, None) == []


def test_removed_clone_clears_the_flag(db):
    store(db, two_clones())
    store(db, make_run([repo("a", remote("h/o/r"))]))
    assert flags(db) == [] and [f[0] for f in flags(db, "cleared")] == ["duplicate_checkout"]
    assert kinds(db, pid(db, "a")) == ["created", "flagged", "resolved"]
    assert db.execute("SELECT COUNT(*) FROM checkouts").fetchone()[0] == 2  # nothing deleted


def test_same_name_different_remotes_is_not_flagged(db):
    store(db, make_run([repo("x", remote("h/o/one")), repo("y", remote("h/o/two"))]))
    assert flags(db, None) == []


# -- conflict ------------------------------------------------------------------------------------------


def conflict(db):
    store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/b"))]))
    return store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/a"))]))


def test_conflict_makes_the_project_ambiguous_and_flagged(db):
    conflict(db)
    a, b = pid(db, "a"), pid(db, "b")
    assert flags(db) == [("identity_unresolved", {"alias": "h/o/a", "alias_owner": a, "path_project": b})]
    assert kinds(db, b)[-1] == "flagged"
    status = {Path(r["path"]).name: r["identity_status"] for r in projects.list_projects(db)}
    assert status == {"a": "resolved", "b": "ambiguous"}
    assert db.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 2


def test_repaired_evidence_restores_status_and_clears(db):
    conflict(db)
    b = pid(db, "b")
    store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/b2"))]))
    row = next(r for r in projects.list_projects(db) if r["project_id"] == b)
    assert row["identity_status"] == "resolved"
    assert flags(db) == [] and kinds(db, b)[-1] == "resolved"


def test_repaired_project_without_alias_becomes_provisional(db):
    store(db, make_run([repo("a", remote("h/o/a")), repo("b")]))
    store(db, make_run([repo("a", remote("h/o/a")), repo("b", remote("h/o/a"))]))
    assert flags(db)[0][0] == "identity_unresolved"
    store(db, make_run([repo("a", remote("h/o/a")), repo("b")]))
    row = next(r for r in projects.list_projects(db) if Path(r["path"]).name == "b")
    assert row["identity_status"] == "provisional" and flags(db) == []


def test_absence_does_not_clear_ambiguity(db):
    conflict(db)
    store(db, make_run([repo("a", remote("h/o/a"))]))
    status = {Path(r["path"]).name: r["identity_status"] for r in projects.list_projects(db)}
    assert status["b"] == "ambiguous" and [f[0] for f in flags(db)] == ["identity_unresolved"]


# -- idempotence and audit ---------------------------------------------------------------------------------


def test_repeated_scan_adds_nothing(db):
    store(db, two_clones())
    before = (db.execute("SELECT COUNT(*) FROM review_flags").fetchone()[0], db.execute("SELECT COUNT(*) FROM identity_events").fetchone()[0])
    store(db, two_clones())
    after = (db.execute("SELECT COUNT(*) FROM review_flags").fetchone()[0], db.execute("SELECT COUNT(*) FROM identity_events").fetchone()[0])
    assert before == after


def test_reopened_flag_reuses_the_row(db):
    store(db, two_clones())
    store(db, make_run([repo("a", remote("h/o/r"))]))
    store(db, two_clones())
    assert db.execute("SELECT COUNT(*) FROM review_flags").fetchone()[0] == 1
    assert kinds(db, pid(db, "a")) == ["created", "flagged", "resolved", "flagged"]
    assert len(projects.list_flags(db)) == 1


def test_listing_filters_and_orders(db):
    conflict(db)  # one open identity_unresolved flag
    store(db, make_run([repo("c", remote("h/o/r")), repo("d", remote("h/o/r"))]))  # one open duplicate flag
    store(db, make_run([repo("c", remote("h/o/r"))]))  # clears it
    assert [f["kind"] for f in projects.list_flags(db)] == ["identity_unresolved"]
    assert [f["kind"] for f in projects.list_flags(db, "cleared")] == ["duplicate_checkout"]
    everything = projects.list_flags(db, None)
    assert [(f["project_id"], f["kind"]) for f in everything] == sorted((f["project_id"], f["kind"]) for f in everything)
    assert len(everything) == 2


def test_flag_evidence_and_events_hold_no_path_or_url(db):
    conflict(db)
    store(db, two_clones())
    texts = [f["evidence"] for f in projects.list_flags(db, None)] + [e["detail"] for e in db.execute("SELECT detail FROM identity_events")]
    assert texts
    for text in texts:
        assert "/ws" not in text and "://" not in text and "@" not in text


# -- migration ---------------------------------------------------------------------------------------------


def test_migration_keeps_events_and_derives_duplicates(tmp_path):
    folder = tmp_path / "v2"
    folder.mkdir()
    for name in ("0001_initial.sql", "0002_identity.sql"):
        (folder / name).write_text((MIGRATIONS / name).read_text())
    path = tmp_path / "index.sqlite3"
    c = open_index(path, migrations=folder)
    c.execute(
        "INSERT INTO projects (project_id, display_name, state, created_at, updated_at, last_seen_at, identity_status,"
        " identity_source) VALUES ('p', 'a', 'active', 't', 't', 't', 'resolved', 'remote')"
    )
    c.execute("INSERT INTO project_aliases VALUES ('remote', 'h/o/r', 'p', 't')")
    for i, name in enumerate(("a", "b"), 1):
        c.execute(
            "INSERT INTO checkouts (checkout_id, project_id, path, path_key, root, state, first_seen_at, last_seen_at)"
            " VALUES (?, 'p', ?, ?, '/ws', 'active', 't', 't')", (i, f"/ws/{name}", f"/ws/{name}"),
        )
    c.execute("INSERT INTO identity_events (project_id, kind, detail, at) VALUES ('p', 'created', '{}', 't')")
    c.close()
    c = open_index(path)
    assert [e["kind"] for e in projects.list_events(c, "p")] == ["created"]
    assert flags(c) == [("duplicate_checkout", {"rule": "same_remote_identity", "aliases": ["h/o/r"], "active_checkouts": 2})]
    assert (tmp_path / "index.sqlite3.bak-v2").is_file()
    c.close()
