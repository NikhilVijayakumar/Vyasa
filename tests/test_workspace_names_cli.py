import hashlib
import io
import json
import os

from vyasa.adapters.cli.main import main
from test_workspace_desktop_cli import setup


def invoke(home, *args):
    out, err = io.StringIO(), io.StringIO()
    code = main(args, {"VYASA_HOME": str(home)}, out, err)
    return code, json.loads(out.getvalue())


def test_names_persist_without_changing_config_or_creating_index(tmp_path):
    home, roots = setup(tmp_path)
    config = home / "config.toml"
    before = config.read_bytes()
    code, result = invoke(home, "workspace", "set-name", "--root", str(roots[0]), "--name", "  Work  ")
    assert code == 0 and result["data"]["name"] == "Work"
    code, result = invoke(home, "query", "workspaces")
    assert code == 0 and [x["name"] for x in result["data"]["workspaces"]] == ["Work", None]
    assert config.read_bytes() == before
    assert not (home / "index.sqlite3").exists()
    assert invoke(home, "workspace", "set-name", "--root", str(roots[0]), "--name", "Personal")[0] == 0
    assert invoke(home, "query", "workspaces")[1]["data"]["workspaces"][0]["name"] == "Personal"


def test_invalid_root_and_names_do_not_create_metadata(tmp_path):
    home, roots = setup(tmp_path)
    for root, name in [(tmp_path / "other", "Name"), (roots[0], "  "), (roots[0], "x" * 101), (roots[0], "bad\nname")]:
        code, result = invoke(home, "workspace", "set-name", "--root", str(root), "--name", name)
        assert code != 0 and result["error"]
    assert not (home / "workspace-names").exists()


def test_corrupt_metadata_is_not_overwritten(tmp_path):
    home, roots = setup(tmp_path)
    directory = home / "workspace-names"
    directory.mkdir()
    key = hashlib.sha256(os.path.normcase(str(roots[0])).encode("utf-8")).hexdigest()
    record = directory / (key + ".json")
    record.write_text("{broken", encoding="utf-8")
    code, result = invoke(home, "workspace", "set-name", "--root", str(roots[0]), "--name", "Name")
    assert code != 0 and result["error"]
    assert record.read_text(encoding="utf-8") == "{broken"


def test_independent_roots_can_share_names_and_scan_preserves_them(tmp_path):
    home, roots = setup(tmp_path)
    for root in roots:
        assert invoke(home, "workspace", "set-name", "--root", str(root), "--name", "Work")[0] == 0
    out, err = io.StringIO(), io.StringIO()
    assert main(["scan"], {"VYASA_HOME": str(home)}, out, err) == 0
    code, result = invoke(home, "query", "workspaces")
    assert code == 0 and [item["name"] for item in result["data"]["workspaces"]] == ["Work", "Work"]
