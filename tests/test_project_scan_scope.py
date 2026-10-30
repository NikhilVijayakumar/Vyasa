"""Project-scoped scan persistence; each test uses an isolated SQLite file."""
import shutil
import sqlite3
from datetime import datetime, timezone

import pytest

from vyasa.adapters.sqlite.database import MIGRATIONS, open_index
from vyasa.application.indexing.store import freshness
from vyasa.application.query import get_index_status


def test_project_scan_scope_migrates_existing_run_and_preserves_foreign_keys(tmp_path):
    old_steps = tmp_path / "old-migrations"
    old_steps.mkdir()
    for file in MIGRATIONS.glob("*.sql"):
        if int(file.name.split("_", 1)[0]) <= 11:
            shutil.copy(file, old_steps / file.name)
    path = tmp_path / "index.sqlite3"
    old = open_index(path, migrations=old_steps)
    old.execute("INSERT INTO scan_runs (run_id, root, status, tool_version, started_at, finished_at) VALUES ('old', '/root', 'completed', 'test', '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00')")
    old.execute("INSERT INTO projects (project_id, display_name, state, created_at, updated_at, last_seen_at) VALUES ('p', 'P', 'active', 't', 't', 't')")
    old.execute("INSERT INTO checkouts (project_id,path,path_key,root,state,first_seen_at,last_seen_at,last_run_id) VALUES ('p','/root/p','/root/p','/root','active','t','t','old')")
    old.close()
    db = open_index(path)
    assert tuple(db.execute("SELECT root, scope_kind, scope_project_id FROM scan_runs WHERE run_id='old'").fetchone()) == ('/root', 'workspace', None)
    assert db.execute("SELECT last_run_id FROM checkouts").fetchone()[0] == 'old'
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert path.with_name('index.sqlite3.bak-v11').exists()
    db.close()


def test_project_run_does_not_change_workspace_freshness_or_latest_status(tmp_path):
    db = open_index(tmp_path / 'index.sqlite3')
    db.execute("INSERT INTO projects (project_id, display_name, state, created_at, updated_at, last_seen_at) VALUES ('p','P','active','t','t','t')")
    db.execute("INSERT INTO scan_runs (run_id,root,status,tool_version,started_at,finished_at) VALUES ('w','/root','completed','test','2026-01-01T00:00:00+00:00','2026-01-01T00:00:00+00:00')")
    db.execute("INSERT INTO scan_runs (run_id,root,status,tool_version,started_at,finished_at,scope_kind,scope_project_id) VALUES ('p',NULL,'failed','test','2026-01-02T00:00:00+00:00','2026-01-02T00:00:00+00:00','project','p')")
    now = datetime(2026, 1, 1, 1, tzinfo=timezone.utc)
    assert freshness(db, now) == 'current'
    assert get_index_status(db, now=lambda: now)['data']['latest_run']['status'] == 'completed'
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO scan_runs (run_id,root,status,tool_version,started_at,scope_kind,scope_project_id) VALUES ('bad',NULL,'running','test','t','workspace',NULL)")
    db.close()


def test_failed_rebuild_rolls_back_version_and_restores_enforcement(tmp_path):
    from vyasa.adapters.sqlite.database import _apply
    from vyasa.domain.index import IndexStoreError

    db = open_index(tmp_path / 'index.sqlite3')
    before = db.execute('PRAGMA user_version').fetchone()[0]
    migration = tmp_path / '0012_project_scan_scope.sql'
    migration.write_text('CREATE TABLE doomed (id INTEGER); INSERT INTO missing_table VALUES (1);', encoding='utf-8')
    with pytest.raises(IndexStoreError):
        _apply(db, before + 1, migration)
    assert db.execute('PRAGMA foreign_keys').fetchone()[0] == 1
    assert db.execute('PRAGMA user_version').fetchone()[0] == before
    assert db.execute("SELECT name FROM sqlite_master WHERE name = 'doomed'").fetchone() is None
    db.close()


def test_foreign_key_check_aborts_rebuild_and_restores_enforcement(tmp_path):
    from vyasa.adapters.sqlite.database import _apply
    from vyasa.domain.index import IndexStoreError

    db = open_index(tmp_path / 'index.sqlite3')
    before = db.execute('PRAGMA user_version').fetchone()[0]
    migration = tmp_path / '0012_project_scan_scope.sql'
    migration.write_text("INSERT INTO checkouts (project_id,path,path_key,root,state,first_seen_at,last_seen_at) VALUES ('missing','/x','/x','/','active','t','t');", encoding='utf-8')
    with pytest.raises(IndexStoreError):
        _apply(db, before + 1, migration)
    assert db.execute('PRAGMA foreign_keys').fetchone()[0] == 1
    assert db.execute('PRAGMA user_version').fetchone()[0] == before
    assert db.execute('SELECT COUNT(*) FROM checkouts').fetchone()[0] == 0
    db.close()


def test_checkout_outcomes_are_unique_and_require_real_references(tmp_path):
    db = open_index(tmp_path / 'index.sqlite3')
    db.execute("INSERT INTO projects (project_id, display_name, state, created_at, updated_at, last_seen_at) VALUES ('p','P','active','t','t','t')")
    db.execute("INSERT INTO checkouts (project_id,path,path_key,root,state,first_seen_at,last_seen_at) VALUES ('p','/x','/x','/','active','t','t')")
    checkout = db.execute('SELECT checkout_id FROM checkouts').fetchone()[0]
    db.execute("INSERT INTO scan_runs (run_id,root,status,tool_version,started_at,scope_kind,scope_project_id) VALUES ('p',NULL,'running','test','t','project','p')")
    db.execute("INSERT INTO scan_checkout_results (run_id,checkout_id,status,reason) VALUES ('p',?,'completed',NULL)", (checkout,))
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO scan_checkout_results (run_id,checkout_id,status,reason) VALUES ('p',?,'failed','SCAN_FAILED')", (checkout,))
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO scan_checkout_results (run_id,checkout_id,status,reason) VALUES ('p',9999,'failed','SCAN_FAILED')")
    db.close()
