import io
import json
import pytest
from vyasa.adapters.cli.main import main
from vyasa.adapters.sqlite.database import open_index

@pytest.mark.parametrize('pointer,child', [
    ('gitdir: /some/repo/.git/worktrees/name\n', False),
    ('gitdir: /some/repo/.git/modules/name\n', False),
    ('gitdir: /some/other/path\n', False),
    ('gitdir: /some/repo/.git/worktrees/name\n', True),
])
def test_pointer_checkout_can_be_scanned_without_following_target(tmp_path, pointer, child):
    root, home = tmp_path / 'root', tmp_path / 'data'
    repo = root / 'one'
    git_root = repo / 'Source' if child else repo
    git_root.mkdir(parents=True)
    (git_root / '.git').write_text(pointer)
    if child:
        (repo / 'game.uproject').write_text('{}')
    home.mkdir()
    (home / 'config.toml').write_text(f'[workspace]\nroots = ["{root.as_posix()}"]\n')
    env = {'VYASA_HOME': str(home), 'HOME': str(tmp_path / 'home')}
    assert main(['scan'], env, io.StringIO(), io.StringIO()) == 0
    db = open_index(home / 'index.sqlite3')
    project = db.execute('SELECT project_id FROM projects').fetchone()[0]
    db.close()
    out = io.StringIO()
    assert main(['scan','--project',project,'--json'], env, out, io.StringIO()) == 0
    assert json.loads(out.getvalue())['data']['status'] == 'completed'
