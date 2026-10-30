import io
import json
from unittest.mock import patch

from vyasa.adapters.cli.main import main
from vyasa.adapters.sqlite.database import open_index
from vyasa.domain.index import IndexStoreError, UNAVAILABLE

def test_selected_path_does_not_inspect_nested_project(tmp_path):
    from vyasa.adapters.filesystem import repository_walk
    root, home = tmp_path / 'root', tmp_path / 'data'
    repo = root / 'one'
    (repo / '.git').mkdir(parents=True)
    (repo / '.git' / 'HEAD').write_text('ref: refs/heads/main\n')
    home.mkdir()
    (home / 'config.toml').write_text(f'[workspace]\nroots = ["{root.as_posix()}"]\n')
    env = {'VYASA_HOME': str(home), 'HOME': str(tmp_path / 'home')}
    assert main(['scan'], env, io.StringIO(), io.StringIO()) == 0
    db = open_index(home / 'index.sqlite3')
    project = db.execute('SELECT project_id FROM projects').fetchone()[0]
    db.close()
    (repo / '.git' / 'HEAD').unlink()
    (repo / '.git').rmdir()
    nested = repo / 'nested'
    (nested / '.git').mkdir(parents=True)
    (nested / '.git' / 'HEAD').write_text('ref: refs/heads/main\n')
    out = io.StringIO()
    original = repository_walk.read_profile
    def guarded(path):
        assert str(path) != str(nested), 'nested project was inspected'
        return original(path)
    with patch.object(repository_walk, 'read_profile', guarded):
        code = main(['scan', '--project', project, '--json'], env, out, io.StringIO())
    body = json.loads(out.getvalue())
    assert code == 1 and body['data']['status'] == 'failed'

def test_equals_form_parse_failure_returns_json():
    out = io.StringIO()
    code = main(['scan', '--project=x', '--unknown'], {}, out, io.StringIO())
    assert code == 2 and json.loads(out.getvalue())['error']['code'] == 'INVALID_INPUT'

def test_index_error_does_not_expose_local_details(tmp_path):
    home, root = tmp_path / 'data', tmp_path / 'root'
    home.mkdir(); root.mkdir()
    (home / 'config.toml').write_text(f'[workspace]\nroots = ["{root.as_posix()}"]\n')
    (home / 'index.sqlite3').touch()
    env = {'VYASA_HOME': str(home), 'HOME': str(tmp_path / 'home')}
    out = io.StringIO()
    with patch('vyasa.adapters.cli.main.open_index', side_effect=IndexStoreError(UNAVAILABLE, 'secret-local-path')):
        code = main(['scan', '--project', 'x', '--json'], env, out, io.StringIO())
    assert code == 4 and 'secret-local-path' not in out.getvalue()

def test_invalid_profile_is_failed_and_prior_profile_is_preserved(tmp_path):
    root, home = tmp_path / 'root', tmp_path / 'data'
    repo = root / 'one'
    (repo / '.git').mkdir(parents=True)
    (repo / '.git' / 'HEAD').write_text('ref: refs/heads/main\n')
    (repo / '.vyasa').mkdir()
    profile = repo / '.vyasa' / 'project-profile.toml'
    profile.write_text('schema_version = 1\nname = "Original"\n')
    home.mkdir()
    (home / 'config.toml').write_text(f'[workspace]\nroots = ["{root.as_posix()}"]\n')
    env = {'VYASA_HOME': str(home), 'HOME': str(tmp_path / 'home')}
    assert main(['scan'], env, io.StringIO(), io.StringIO()) == 0
    db = open_index(home / 'index.sqlite3')
    project = db.execute('SELECT project_id FROM projects').fetchone()[0]
    prior = tuple(db.execute('SELECT status, fields FROM checkout_profiles').fetchone())
    db.close()
    profile.write_text('schema_version = [broken')
    out = io.StringIO()
    assert main(['scan','--project',project,'--json'], env, out, io.StringIO()) == 1
    assert json.loads(out.getvalue())['data']['status'] == 'failed'
    db = open_index(home / 'index.sqlite3', read_only=True)
    assert tuple(db.execute('SELECT status, fields FROM checkout_profiles').fetchone()) == prior
    db.close()

def test_project_parser_does_not_echo_untrusted_token(capsys):
    out = io.StringIO()
    code = main(['scan', '--project=x', '--secret-path-token'], {}, out, io.StringIO())
    assert code == 2 and json.loads(out.getvalue())['error']['code'] == 'INVALID_INPUT'
    assert 'secret-path-token' not in capsys.readouterr().err

def test_unavailable_git_remote_is_failed_and_previous_identity_preserved(tmp_path):
    root, home = tmp_path / 'root', tmp_path / 'data'
    repo = root / 'one'
    (repo / '.git').mkdir(parents=True)
    (repo / '.git' / 'HEAD').write_text('ref: refs/heads/main\n')
    config = repo / '.git' / 'config'
    config.write_text('[remote "origin"]\nurl = https://github.com/example/one.git\n')
    home.mkdir()
    (home / 'config.toml').write_text(f'[workspace]\nroots = ["{root.as_posix()}"]\n')
    env = {'VYASA_HOME': str(home), 'HOME': str(tmp_path / 'home')}
    assert main(['scan'], env, io.StringIO(), io.StringIO()) == 0
    db = open_index(home / 'index.sqlite3')
    project = db.execute('SELECT project_id FROM projects').fetchone()[0]
    before = tuple(db.execute('SELECT remote_identity,remote_status FROM checkouts').fetchone())
    db.close()
    config.write_bytes(b'x' * 70000)
    out = io.StringIO()
    assert main(['scan','--project',project,'--json'], env, out, io.StringIO()) == 1
    assert json.loads(out.getvalue())['data']['status'] == 'failed'
    db = open_index(home / 'index.sqlite3', read_only=True)
    assert tuple(db.execute('SELECT remote_identity,remote_status FROM checkouts').fetchone()) == before
    db.close()


def test_malformed_manifest_fails_without_replacing_previous_observation(tmp_path):
    root, home = tmp_path / 'root', tmp_path / 'data'
    repo = root / 'one'
    (repo / '.git').mkdir(parents=True)
    (repo / '.git' / 'HEAD').write_text('ref: refs/heads/main\n')
    manifest = repo / 'pyproject.toml'
    manifest.write_text('[project]\nname = "example"\n')
    home.mkdir()
    (home / 'config.toml').write_text(f'[workspace]\nroots = ["{root.as_posix()}"]\n')
    env = {'VYASA_HOME': str(home), 'HOME': str(tmp_path / 'home')}
    assert main(['scan'], env, io.StringIO(), io.StringIO()) == 0
    db = open_index(home / 'index.sqlite3')
    project = db.execute('SELECT project_id FROM projects').fetchone()[0]
    before = db.execute('SELECT COUNT(*) FROM language_observations').fetchone()[0]
    db.close()
    manifest.write_text('[project\n')
    out = io.StringIO()
    assert main(['scan','--project',project,'--json'], env, out, io.StringIO()) == 1
    assert json.loads(out.getvalue())['data']['status'] == 'failed'
    db = open_index(home / 'index.sqlite3', read_only=True)
    assert db.execute('SELECT COUNT(*) FROM language_observations').fetchone()[0] == before
    db.close()
