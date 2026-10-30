import io
import json
import os
from datetime import datetime, timezone
import pytest
from vyasa.adapters.cli.main import main
from vyasa.adapters.sqlite import lock
from vyasa.adapters.sqlite.database import open_index

def call(args, env):
    out = io.StringIO()
    code = main(args, env, out, io.StringIO())
    return code, json.loads(out.getvalue())

def setup(tmp_path):
    roots = [tmp_path / 'a', tmp_path / 'b']
    home = tmp_path / 'data'
    home.mkdir()
    for root in roots:
        repo = root / 'repo'
        (repo / '.git').mkdir(parents=True)
        (repo / '.git' / 'HEAD').write_text('ref: refs/heads/main\n')
        (repo / '.git' / 'config').write_text('[remote "origin"]\nurl = https://github.com/example/shared.git\n')
    (home / 'config.toml').write_text('[workspace]\nroots = [' + ','.join('"' + r.as_posix() + '"' for r in roots) + ']\n')
    env = {'VYASA_HOME': str(home), 'HOME': str(tmp_path / 'home')}
    assert main(['scan'], env, io.StringIO(), io.StringIO()) == 0
    db = open_index(home / 'index.sqlite3')
    project = db.execute('SELECT project_id FROM projects').fetchone()[0]
    db.close()
    return roots, home, env, project

def test_multiple_roots_are_scanned_and_reported(tmp_path):
    roots, home, env, project = setup(tmp_path)
    code, body = call(['scan','--project',project,'--json'], env)
    assert code == 0 and body['data']['status'] == 'completed'
    assert len(body['data']['checkouts']) == 2
    assert all(item['status'] == 'completed' for item in body['data']['checkouts'])

def test_inaccessible_checkout_does_not_stop_other(tmp_path, monkeypatch):
    from vyasa.application.indexing import project_scan
    roots, home, env, project = setup(tmp_path)
    original = project_scan._inspect_selected
    def inspect(path, *args):
        if path == roots[0] / 'repo':
            raise PermissionError('private path')
        return original(path, *args)
    monkeypatch.setattr(project_scan, '_inspect_selected', inspect)
    code, body = call(['scan','--project',project,'--json'], env)
    assert code == 1 and body['data']['status'] == 'partial'
    assert {item['reason'] for item in body['data']['checkouts']} == {None, 'INACCESSIBLE'}

def test_linked_checkout_is_not_followed(tmp_path):
    roots, home, env, project = setup(tmp_path)
    checkout = roots[0] / 'repo'
    moved = tmp_path / 'moved'
    checkout.rename(moved)
    try:
        os.symlink(moved, checkout, target_is_directory=True)
    except OSError:
        pytest.skip('directory symlink unavailable')
    code, body = call(['scan','--project',project,'--json'], env)
    assert code == 1 and body['data']['status'] == 'partial'
    assert 'OUTSIDE_CONFIGURED_ROOTS' in [item['reason'] for item in body['data']['checkouts']]

def test_busy_lock_is_reported_and_successful_run_releases_lock(tmp_path):
    roots, home, env, project = setup(tmp_path)
    db = open_index(home / 'index.sqlite3')
    lock.acquire(db, 'test', 'held', datetime.now(timezone.utc))
    code, body = call(['scan','--project',project,'--json'], env)
    assert code == 3 and body['error']['code'] == 'OPERATION_IN_PROGRESS'
    lock.release(db, 'held')
    db.close()
    assert call(['scan','--project',project,'--json'], env)[0] == 0
    db = open_index(home / 'index.sqlite3')
    assert db.execute('SELECT COUNT(*) FROM index_lock').fetchone()[0] == 0
    db.close()

def test_configuration_index_and_option_errors_are_structured(tmp_path):
    home = tmp_path / 'data'
    env = {'VYASA_HOME': str(home), 'HOME': str(tmp_path / 'home')}
    code, body = call(['scan','--project','x','--json'], env)
    assert code == 2 and body['error']['code'] == 'CONFIG_NOT_FOUND'
    home.mkdir()
    config = home / 'config.toml'
    config.write_text('invalid = [')
    code, body = call(['scan','--project','x','--json'], env)
    assert code == 2 and body['error']['code'] == 'CONFIG_INVALID'
    root = tmp_path / 'root'
    root.mkdir()
    config.write_text(f'[workspace]\nroots = ["{root.as_posix()}"]\n')
    code, body = call(['scan','--project','x','--json'], env)
    assert code == 4 and body['error']['code'] == 'INDEX_UNAVAILABLE'
    code, body = call(['scan','--project','x','--workspace',str(root),'--json'], env)
    assert code == 2 and body['error']['code'] == 'INVALID_INPUT'

def test_json_without_project_is_rejected_without_scanning(tmp_path):
    roots, home, env, project = setup(tmp_path)
    db = open_index(home / 'index.sqlite3')
    before = db.execute('SELECT COUNT(*) FROM scan_runs').fetchone()[0]
    db.close()
    code, body = call(['scan','--json'], env)
    assert code == 2 and body['error']['code'] == 'INVALID_INPUT'
    db = open_index(home / 'index.sqlite3', read_only=True)
    assert db.execute('SELECT COUNT(*) FROM scan_runs').fetchone()[0] == before
    db.close()
