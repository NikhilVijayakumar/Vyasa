"""Project scan contract on isolated repositories and index data."""
import io
import json

from vyasa.adapters.cli.main import main
from vyasa.adapters.sqlite.database import open_index


def run(args, environ):
    out, err = io.StringIO(), io.StringIO()
    code = main(args, environ, out, err)
    return code, out.getvalue()


def test_selected_project_scan_preserves_other_checkout_and_reports_result(tmp_path):
    root = tmp_path / 'workspace'
    home = tmp_path / 'data'
    home.mkdir()
    for name in ('selected', 'other'):
        repo = root / name
        (repo / '.git').mkdir(parents=True)
        (repo / '.git' / 'HEAD').write_text('ref: refs/heads/main\n')
        (repo / 'README.md').write_text(name)
    (home / 'config.toml').write_text(f'[workspace]\nroots = ["{root.as_posix()}"]\n')
    environ = {'VYASA_HOME': str(home), 'HOME': str(tmp_path / 'home')}
    assert run(['scan'], environ)[0] == 0
    db = open_index(home / 'index.sqlite3')
    project = db.execute("SELECT project_id FROM projects WHERE display_name='selected'").fetchone()[0]
    other = tuple(db.execute("SELECT state, last_run_id FROM checkouts WHERE path LIKE '%other'").fetchone())
    db.close()
    before = (root / 'selected' / 'README.md').read_bytes()
    code, out = run(['scan', '--project', project, '--json'], environ)
    data = json.loads(out)['data']
    assert code == 0 and data['status'] == 'completed'
    assert len(data['checkouts']) == 1 and data['checkouts'][0]['status'] == 'completed'
    db = open_index(home / 'index.sqlite3', read_only=True)
    assert tuple(db.execute("SELECT state, last_run_id FROM checkouts WHERE path LIKE '%other'").fetchone()) == other
    db.close()
    assert (root / 'selected' / 'README.md').read_bytes() == before


def test_capability_probe_does_not_need_config_or_index(tmp_path):
    code, out = run(['query', 'capabilities'], {'VYASA_HOME': str(tmp_path / 'absent')})
    assert code == 0
    assert json.loads(out) == {'schema_version': '1', 'data': {'capabilities': {'project_scan': 1}}}
    assert not (tmp_path / 'absent').exists()
