import json
import multiprocessing
import os
import socket
import sqlite3
import stat
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from vyasa.adapters.sqlite import lock, projects
from vyasa.adapters.sqlite.database import MIGRATIONS, open_index
from vyasa.application.configuration.workspace import data_directory
from vyasa.application.indexing import store as store_module
from vyasa.application.indexing.store import freshness, index_path, store_run
from vyasa.domain.discovery import (
    COMPLETE,
    FAILED,
    INACCESSIBLE,
    PARTIAL,
    Candidate,
    DiscoveryOptions,
    DiscoveryRun,
    ScanWarning,
)
from vyasa.domain.git_remote import GitRemote
from vyasa.domain.index import (
    IN_PROGRESS,
    MIGRATION_FAILED,
    SCHEMA_TOO_NEW,
    IndexStoreError,
    freshness as domain_freshness,
)

LATEST = len(list(MIGRATIONS.glob("[0-9]*_*.sql")))
T0 = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
ROOT = Path("/ws")


def repo(name, remote=None, root=ROOT):
    return Candidate(root / name, "eligible", kind="repository", markers=("pyproject.toml",), git=".", remote=remote, remote_status="origin" if remote else "none")


_ids = iter(range(10_000))


def make_run(repos=(), status=COMPLETE, issues=(), warnings=(), root=ROOT):
    return DiscoveryRun(
        run_id=f"run{next(_ids)}", root=root, started_at=T0, finished_at=T0, status=status, tool_version="t",
        options=DiscoveryOptions(), counts={}, repositories=tuple(repos), issues=tuple(issues), warnings=tuple(warnings),
    )


@pytest.fixture
def db(tmp_path):
    connection = open_index(tmp_path / "data" / "index.sqlite3")
    yield connection
    connection.close()


def store(db, run, owner="a", at=T0):
    return store_run(db, run, owner=owner, now=lambda: at)


def states(db):
    return {Path(r["path"]).name: r["state"] for r in projects.list_projects(db)}


# -- open and migrate ---------------------------------------------------------------------------


def test_first_open_creates_directory_file_and_schema(tmp_path):
    path = tmp_path / "new" / "index.sqlite3"
    connection = open_index(path)
    assert path.is_file()
    assert connection.execute("PRAGMA user_version").fetchone()[0] == LATEST
    connection.close()


@pytest.mark.skipif(os.name != "posix", reason="POSIX permissions")
def test_posix_modes(tmp_path):
    path = tmp_path / "new" / "index.sqlite3"
    open_index(path).close()
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_pragmas(db):
    assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert db.execute("PRAGMA busy_timeout").fetchone()[0] == 5000


def test_index_path_follows_the_data_directory():
    env = {"VYASA_HOME": "/somewhere"}
    assert index_path(env) == data_directory(env) / "index.sqlite3"


def _migrations(tmp_path, *extra):
    folder = tmp_path / "migrations"
    folder.mkdir()
    (folder / "0001_initial.sql").write_text((MIGRATIONS / "0001_initial.sql").read_text())
    for name, sql in extra:
        (folder / name).write_text(sql)
    return folder


def test_pending_migration_makes_a_backup_and_keeps_data(tmp_path):
    path = tmp_path / "index.sqlite3"
    connection = open_index(path, migrations=_migrations(tmp_path))
    connection.execute(
        "INSERT INTO projects (project_id, display_name, state, created_at, updated_at, last_seen_at)"
        " VALUES ('p', 'a', 'active', 't', 't', 't')"
    )
    connection.close()
    connection = open_index(path, migrations=_migrations_with_second(tmp_path))
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
    assert (tmp_path / "index.sqlite3.bak-v1").is_file()
    assert connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 1
    connection.close()


@pytest.mark.parametrize("old", range(1, len(sorted(MIGRATIONS.glob("0*.sql")))))
def test_every_earlier_schema_version_upgrades_to_current(tmp_path, old):
    steps = sorted(MIGRATIONS.glob("0*.sql"))
    folder = tmp_path / "old"
    folder.mkdir()
    for file in steps[:old]:
        (folder / file.name).write_text(file.read_text(encoding="utf-8"), encoding="utf-8")
    path = tmp_path / "index.sqlite3"
    connection = open_index(path, migrations=folder)
    connection.execute(
        "INSERT INTO projects (project_id, display_name, state, created_at, updated_at, last_seen_at)"
        " VALUES ('p', 'a', 'active', 't', 't', 't')"
    )
    connection.close()
    connection = open_index(path)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == len(steps)
    assert connection.execute("SELECT display_name FROM projects WHERE project_id = 'p'").fetchone()[0] == "a"
    assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    assert (tmp_path / f"index.sqlite3.bak-v{old}").is_file()
    connection.close()


def _migrations_with_second(tmp_path):
    folder = tmp_path / "migrations2"
    folder.mkdir()
    (folder / "0001_initial.sql").write_text((MIGRATIONS / "0001_initial.sql").read_text())
    (folder / "0002_extra.sql").write_text("CREATE TABLE extra (x INTEGER);")
    return folder


def test_failed_migration_rolls_back(tmp_path):
    path = tmp_path / "index.sqlite3"
    open_index(path).close()
    folder = tmp_path / "bad"
    folder.mkdir()
    for file in MIGRATIONS.glob("[0-9]*_*.sql"):
        (folder / file.name).write_text(file.read_text())
    (folder / f"{LATEST + 1:04d}_bad.sql").write_text("CREATE TABLE half (x INTEGER); SELECT nonsense FROM nowhere;")
    with pytest.raises(IndexStoreError) as error:
        open_index(path, migrations=folder)
    assert error.value.code == MIGRATION_FAILED
    check = sqlite3.connect(path)
    assert check.execute("PRAGMA user_version").fetchone()[0] == LATEST
    assert check.execute("SELECT name FROM sqlite_master WHERE name = 'half'").fetchone() is None
    check.close()


def test_newer_schema_is_refused_and_untouched(tmp_path):
    path = tmp_path / "index.sqlite3"
    raw = sqlite3.connect(path)
    raw.execute("PRAGMA user_version = 99")
    raw.close()
    before = path.read_bytes()
    with pytest.raises(IndexStoreError) as error:
        open_index(path)
    assert error.value.code == SCHEMA_TOO_NEW
    assert path.read_bytes() == before


def test_up_to_date_makes_no_backup(tmp_path):
    path = tmp_path / "index.sqlite3"
    open_index(path).close()
    open_index(path).close()
    assert not list(tmp_path.glob("*.bak-*"))


# -- storing --------------------------------------------------------------------------------------


def test_new_project_is_stored_and_survives_restart(tmp_path):
    path = tmp_path / "index.sqlite3"
    connection = open_index(path)
    result = store(connection, make_run([repo("a")]))
    assert result.status == "completed" and result.counts == {"added": 1}
    connection.close()
    again = open_index(path, read_only=True)
    rows = projects.list_projects(again)
    assert [(r["display_name"], r["state"]) for r in rows] == [("a", "active")]
    again.close()


def test_changed_project_keeps_its_identifier(db):
    store(db, make_run([repo("a")]))
    before = projects.list_projects(db)[0]["project_id"]
    result = store(db, make_run([repo("a", GitRemote("origin", "github", "github.com", "github.com/o/a"))]))
    row = projects.list_projects(db)[0]
    assert result.counts["updated"] == 1
    assert row["project_id"] == before and row["remote_identity"] == "github.com/o/a"


def test_only_the_normalized_remote_is_stored(db):
    store(db, make_run([repo("a", GitRemote("origin", "github", "github.com", "github.com/o/a"))]))
    dump = "\n".join(db.iterdump())
    assert "github.com/o/a" in dump and "https://" not in dump and "@" not in dump


def test_same_tree_twice_does_not_duplicate(db):
    store(db, make_run([repo("a"), repo("b")]))
    ids = {r["display_name"]: r["project_id"] for r in projects.list_projects(db)}
    result = store(db, make_run([repo("a"), repo("b")]))
    assert result.counts == {"unchanged": 2}
    assert {r["display_name"]: r["project_id"] for r in projects.list_projects(db)} == ids


def test_order_does_not_matter(tmp_path):
    first = open_index(tmp_path / "1.sqlite3")
    second = open_index(tmp_path / "2.sqlite3")
    store(first, make_run([repo("a"), repo("b")]))
    store(second, make_run([repo("b"), repo("a")]))
    names = lambda c: [r["display_name"] for r in projects.list_projects(c)]
    assert names(first) == names(second) == ["a", "b"]


# -- vanished projects ------------------------------------------------------------------------------


def test_removed_project_is_missing_not_erased(db):
    store(db, make_run([repo("a"), repo("b")]))
    store(db, make_run([repo("a")]))
    assert states(db) == {"a": "active", "b": "missing"}


def test_unreadable_project_is_inaccessible(db):
    store(db, make_run([repo("a")]))
    store(db, make_run(issues=[Candidate(ROOT / "a", INACCESSIBLE, reason="unreadable")], status=PARTIAL))
    assert states(db) == {"a": "inaccessible"}


@pytest.mark.parametrize("status", [PARTIAL, FAILED])
def test_incomplete_run_changes_nothing(db, status):
    store(db, make_run([repo("a")]))
    store(db, make_run(status=status))
    assert states(db) == {"a": "active"}


def test_hidden_directories_prevent_marking_absent(db):
    store(db, make_run([repo("a")]))
    warning = ScanWarning("max_depth", 1, (ROOT / "deep",), "")
    store(db, make_run(warnings=[warning]))
    assert states(db) == {"a": "active"}


def test_ignore_file_warning_does_not_prevent_marking_absent(db):
    store(db, make_run([repo("a")]))
    store(db, make_run(warnings=[ScanWarning("ignore_file", 1, (), "")]))
    assert states(db) == {"a": "missing"}


def test_reappearing_project_is_active_with_the_same_id(db):
    store(db, make_run([repo("a")]))
    before = projects.list_projects(db)[0]["project_id"]
    store(db, make_run())
    result = store(db, make_run([repo("a")]))
    row = projects.list_projects(db)[0]
    assert result.counts == {"restored": 1}
    assert (row["state"], row["project_id"]) == ("active", before)


def test_other_roots_are_untouched(db):
    other = Path("/other")
    store(db, make_run([repo("a", root=other)], root=other))
    store(db, make_run([repo("b")]))
    assert states(db) == {"a": "active", "b": "active"}


# -- run lifecycle and the writer ----------------------------------------------------------------------


def test_completed_run_is_recorded(db):
    run = make_run([repo("a")])
    store(db, run)
    row = db.execute("SELECT * FROM scan_runs WHERE run_id = ?", (run.run_id,)).fetchone()
    assert (row["status"], row["root"], row["finished_at"] is not None) == ("completed", str(ROOT), True)
    assert json.loads(row["counts"]) == {"added": 1}
    assert db.execute("SELECT COUNT(*) FROM index_lock").fetchone()[0] == 0


def test_failure_part_way_keeps_earlier_projects_and_unrelated_data(db, monkeypatch):
    store(db, make_run([repo("old")]))
    real = projects.upsert
    calls = []

    def failing(*args):
        calls.append(1)
        if len(calls) == 2:
            raise RuntimeError("boom")
        return real(*args)

    monkeypatch.setattr(projects, "upsert", failing)
    run = make_run([repo("a"), repo("b"), repo("c")])
    with pytest.raises(RuntimeError):
        store(db, run)
    assert states(db) == {"a": "active", "old": "active"}
    assert db.execute("SELECT status FROM scan_runs WHERE run_id = ?", (run.run_id,)).fetchone()[0] == "interrupted"
    assert db.execute("SELECT COUNT(*) FROM index_lock").fetchone()[0] == 0


def test_second_writer_is_refused(tmp_path):
    path = tmp_path / "index.sqlite3"
    one, two = open_index(path), open_index(path)
    lock.acquire(one, "a", "r1", T0)
    with pytest.raises(IndexStoreError) as error:
        store(two, make_run([repo("a")]), owner="b", at=T0 + timedelta(seconds=5))
    assert error.value.code == IN_PROGRESS
    assert projects.list_projects(two) == []
    lock.release(one, "r1")
    store(two, make_run([repo("a")]), owner="b", at=T0 + timedelta(seconds=6))
    one.close(); two.close()


def test_dead_writer_is_recovered(db):
    db.execute("INSERT INTO scan_runs (run_id, root, status, tool_version, started_at) VALUES ('old', '/x', 'running', 't', ?)", (T0.isoformat(),))
    lock.acquire(db, "gone", "old", T0)
    store(db, make_run([repo("a")]), owner="new", at=T0 + timedelta(seconds=61))
    assert db.execute("SELECT status FROM scan_runs WHERE run_id = 'old'").fetchone()[0] == "interrupted"
    assert states(db) == {"a": "active"}


def _hold(path, started, release):
    connection = open_index(path)
    lock.acquire(connection, "child", "rc", datetime.now(timezone.utc))
    started.set()
    release.wait(10)
    connection.close()


def test_second_process_is_refused(tmp_path):
    path = tmp_path / "index.sqlite3"
    open_index(path).close()
    started, release = multiprocessing.Event(), multiprocessing.Event()
    child = multiprocessing.Process(target=_hold, args=(path, started, release))
    child.start()
    try:
        assert started.wait(10)
        connection = open_index(path)
        with pytest.raises(IndexStoreError) as error:
            store_run(connection, make_run([repo("a")]), owner="parent")
        assert error.value.code == IN_PROGRESS
        connection.close()
    finally:
        release.set()
        child.join(10)


# -- freshness and reading ------------------------------------------------------------------------------


def test_freshness_states(db):
    assert freshness(db, T0) == "unknown"
    store(db, make_run([repo("a")]), at=T0)
    assert freshness(db, T0 + timedelta(hours=1)) == "current"
    assert freshness(db, T0 + timedelta(hours=25)) == "stale"
    store(db, make_run(status=PARTIAL), at=T0 + timedelta(minutes=1))
    assert freshness(db, T0 + timedelta(hours=1)) == "partial"


def test_domain_freshness_boundary():
    assert domain_freshness("completed", T0, T0 + timedelta(hours=24)) == "current"
    assert domain_freshness("interrupted", T0, T0) == "partial"


def test_read_only_connection_reads_and_cannot_write(tmp_path):
    path = tmp_path / "index.sqlite3"
    writer = open_index(path)
    store(writer, make_run([repo("a")]))
    writer.close()
    reader = open_index(path, read_only=True)
    assert len(projects.list_projects(reader)) == 1
    assert freshness(reader, T0) == "current"
    with pytest.raises(sqlite3.OperationalError):
        reader.execute("DELETE FROM projects")
    reader.close()


def test_works_with_sockets_blocked(tmp_path, monkeypatch):
    def refuse(*a, **k):
        raise AssertionError("network used")

    monkeypatch.setattr(socket, "socket", refuse)
    connection = open_index(tmp_path / "index.sqlite3")
    store(connection, make_run([repo("a")]))
    assert len(projects.list_projects(connection)) == 1
    connection.close()
