"""A legacy index must remain queryable without migration."""
import shutil
from datetime import datetime, timezone

from vyasa.adapters.sqlite.database import MIGRATIONS, open_index
from vyasa.application.indexing.store import freshness
from vyasa.application.query import get_index_status


def test_legacy_index_freshness_and_status_are_readable_without_migration(tmp_path):
    migrations = tmp_path / 'old'
    migrations.mkdir()
    for file in MIGRATIONS.glob('*.sql'):
        if int(file.name.split('_', 1)[0]) <= 11:
            shutil.copy(file, migrations / file.name)
    path = tmp_path / 'index.sqlite3'
    db = open_index(path, migrations=migrations)
    db.execute("INSERT INTO scan_runs (run_id,root,status,tool_version,started_at,finished_at) VALUES ('w','/root','completed','test','2026-01-01T00:00:00+00:00','2026-01-01T00:00:00+00:00')")
    db.close()
    db = open_index(path, read_only=True)
    now = datetime(2026, 1, 1, 1, tzinfo=timezone.utc)
    assert freshness(db, now) == 'current'
    assert get_index_status(db, now=lambda: now)['data']['latest_run']['status'] == 'completed'
    assert db.execute('PRAGMA user_version').fetchone()[0] == 11
    db.close()
