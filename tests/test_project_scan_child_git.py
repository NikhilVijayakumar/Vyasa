import io
import json
from vyasa.adapters.cli.main import main
from vyasa.adapters.sqlite.database import open_index

def test_selected_project_preserves_indexed_child_git(tmp_path):
    root, home = tmp_path / 'root', tmp_path / 'data'
    repo = root / 'game'
    (repo / 'Source' / '.git').mkdir(parents=True)
    (repo / 'Source' / '.git' / 'HEAD').write_text('ref: refs/heads/main\n')
    (repo / 'Source' / '.git' / 'config').write_text('[remote "origin"]\nurl = https://github.com/example/game.git\n')
    (repo / 'game.uproject').write_text('{}')
    home.mkdir()
    (home / 'config.toml').write_text(f'[workspace]\nroots = ["{root.as_posix()}"]\n')
    env = {'VYASA_HOME': str(home), 'HOME': str(tmp_path / 'home')}
    assert main(['scan'], env, io.StringIO(), io.StringIO()) == 0
    db = open_index(home / 'index.sqlite3')
    project = db.execute('SELECT project_id FROM projects').fetchone()[0]
    before = tuple(db.execute('SELECT git,remote_identity FROM checkouts').fetchone())
    db.close()
    out = io.StringIO()
    assert main(['scan','--project',project,'--json'], env, out, io.StringIO()) == 0
    assert json.loads(out.getvalue())['data']['status'] == 'completed'
    db = open_index(home / 'index.sqlite3', read_only=True)
    assert tuple(db.execute('SELECT git,remote_identity FROM checkouts').fetchone()) == before
    db.close()
