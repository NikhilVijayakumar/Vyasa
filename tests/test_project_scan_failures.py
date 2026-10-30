import io
import json
import os
import shutil

from vyasa.adapters.cli.main import main
from vyasa.adapters.sqlite.database import open_index


def call(args, env):
    out = io.StringIO()
    code = main(args, env, out, io.StringIO())
    return code, json.loads(out.getvalue())


def setup(tmp_path, *, same_remote=False):
    root, home = tmp_path / 'root', tmp_path / 'data'
    home.mkdir()
    for name in ('one', 'two'):
        repo = root / name
        (repo / '.git').mkdir(parents=True)
        (repo / '.git' / 'HEAD').write_text('ref: refs/heads/main\n')
        if same_remote:
            (repo / '.git' / 'config').write_text('[remote "origin"]\nurl = https://github.com/example/same.git\n')
        (repo / 'README.md').write_text(name)
    (home / 'config.toml').write_text(f'[workspace]\nroots = ["{root.as_posix()}"]\n')
    env = {'VYASA_HOME': str(home), 'HOME': str(tmp_path / 'home')}
    assert main(['scan'], env, io.StringIO(), io.StringIO()) == 0
    db = open_index(home / 'index.sqlite3')
    project = db.execute("SELECT project_id FROM projects WHERE display_name='one'").fetchone()[0]
    db.close()
    return root, home, env, project


def test_mixed_missing_checkout_is_partial_and_does_not_reconcile_other_projects(tmp_path):
    root, home, env, project = setup(tmp_path, same_remote=True)
    shutil.rmtree(root / 'two')
    code, body = call(['scan', '--project', project, '--json'], env)
    assert code == 1 and body['data']['status'] == 'partial'
    assert {x['reason'] for x in body['data']['checkouts']} == {None, 'MISSING'}


def test_unknown_project_and_missing_json_are_structured(tmp_path):
    root, home, env, project = setup(tmp_path)
    code, body = call(['scan', '--project', 'unknown', '--json'], env)
    assert code == 2 and body['error']['code'] == 'PROJECT_NOT_FOUND'
    code, body = call(['scan', '--project', project], env)
    assert code == 2 and body['error']['code'] == 'INVALID_INPUT'


def test_project_with_no_checkouts_is_failed(tmp_path):
    root, home, env, project = setup(tmp_path)
    db = open_index(home / 'index.sqlite3')
    db.execute("INSERT INTO projects (project_id,display_name,state,created_at,updated_at,last_seen_at) VALUES ('empty','Empty','active','t','t','t')")
    db.close()
    code, body = call(['scan', '--project', 'empty', '--json'], env)
    assert code == 1 and body['data']['status'] == 'failed' and body['data']['checkouts'] == []


def test_checkout_outside_current_roots_is_not_read(tmp_path):
    root, home, env, project = setup(tmp_path)
    alternate = tmp_path / 'alternate'
    alternate.mkdir()
    (home / 'config.toml').write_text(f'[workspace]\nroots = ["{alternate.as_posix()}"]\n')
    code, body = call(['scan', '--project', project, '--json'], env)
    assert code == 1 and body['data']['status'] == 'failed'
    assert body['data']['checkouts'][0]['reason'] == 'OUTSIDE_CONFIGURED_ROOTS'


def test_incomplete_detector_walk_is_not_success(tmp_path, monkeypatch):
    from dataclasses import replace
    from vyasa.application.indexing import project_scan

    root, home, env, project = setup(tmp_path)
    original = project_scan.enrich_run

    def incomplete(run):
        result = original(run)
        candidate = result.repositories[0]
        language = replace(candidate.languages.report, stopped_by='limit')
        outcome = replace(candidate.languages, report=language)
        return replace(result, repositories=(replace(candidate, languages=outcome),))

    monkeypatch.setattr(project_scan, 'enrich_run', incomplete)
    code, body = call(['scan', '--project', project, '--json'], env)
    assert code == 1 and body['data']['status'] == 'failed'
    assert body['data']['checkouts'][0]['reason'] == 'SCAN_FAILED'


def test_identity_conflict_is_failure_without_merging_projects(tmp_path):
    root, home, env, project = setup(tmp_path)
    remote = '[remote "origin"]\nurl = https://github.com/example/two.git\n'
    (root / 'two' / '.git' / 'config').write_text(remote)
    assert main(['scan'], env, io.StringIO(), io.StringIO()) == 0
    (root / 'one' / '.git' / 'config').write_text(remote)
    code, body = call(['scan', '--project', project, '--json'], env)
    assert code == 1 and body['data']['status'] == 'failed'
    assert body['data']['checkouts'][0]['reason'] == 'IDENTITY_CONFLICT'
    db = open_index(home / 'index.sqlite3', read_only=True)
    assert db.execute('SELECT COUNT(*) FROM projects').fetchone()[0] == 2
    db.close()


def test_parser_failure_with_real_argv_is_json(tmp_path, monkeypatch):
    import sys
    _, _, env, _ = setup(tmp_path)
    monkeypatch.setattr(sys, 'argv', ['vyasa', 'scan', '--project'])
    out = io.StringIO()
    assert main(None, env, out, io.StringIO()) == 2
    assert json.loads(out.getvalue())['error']['code'] == 'INVALID_INPUT'
