import io
import json
import subprocess

from vyasa.adapters.cli.main import main


def call(home, *args):
    out, err = io.StringIO(), io.StringIO()
    code = main(args, {"VYASA_HOME": str(home)}, out, err)
    return code, out.getvalue(), err.getvalue()


def setup(tmp_path):
    home = tmp_path / "data"
    home.mkdir()
    roots = [tmp_path / "one", tmp_path / "two"]
    for root, name in zip(roots, ("alpha", "beta")):
        project = root / name
        project.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        (project / "package.json").write_text('{"name":"' + name + '"}', encoding="utf-8")
    (home / "config.toml").write_text("[workspace]\nroots = " + json.dumps([str(r) for r in roots]), encoding="utf-8")
    return home, roots


def test_list_roots_does_not_create_index(tmp_path):
    home, roots = setup(tmp_path)
    code, out, _ = call(home, "query", "workspaces")
    assert code == 0
    assert [x["root"] for x in json.loads(out)["data"]["workspaces"]] == [str(x) for x in roots]
    assert not (home / "index.sqlite3").exists()


def test_selected_root_search_and_scan_are_isolated(tmp_path):
    home, roots = setup(tmp_path)
    assert call(home, "scan")[0] == 0
    for root, name in zip(roots, ("alpha", "beta")):
        code, out, _ = call(home, "query", "search", "--workspace", str(root), "--limit", "1")
        assert code == 0
        assert [x["display_name"] for x in json.loads(out)["data"]["projects"]] == [name]
    (roots[1] / "beta").rename(roots[1] / "moved")
    assert call(home, "scan", "--workspace", str(roots[0]))[0] == 0
    code, out, _ = call(home, "query", "search", "--workspace", str(roots[1]))
    assert code == 0
    assert json.loads(out)["data"]["projects"][0]["state"] == "active"


def test_unconfigured_root_rejected_without_creating_index(tmp_path):
    home, _ = setup(tmp_path)
    code, _, _ = call(home, "scan", "--workspace", str(tmp_path / "other"))
    assert code != 0
    assert not (home / "index.sqlite3").exists()
    code, out, _ = call(home, "query", "search", "--workspace", str(tmp_path / "other"))
    assert code != 0 and json.loads(out)["error"]


def test_workspace_filter_applies_before_pagination(tmp_path):
    home, roots = setup(tmp_path)
    project = roots[0] / "zeta"
    project.mkdir()
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    (project / "package.json").write_text('{"name":"zeta"}', encoding="utf-8")
    assert call(home, "scan")[0] == 0
    code, out, _ = call(home, "query", "search", "--workspace", str(roots[0]), "--limit", "1")
    first = json.loads(out)["data"]
    assert code == 0 and first["page"]["next_cursor"]
    code, out, _ = call(home, "query", "search", "--workspace", str(roots[0]), "--limit", "1", "--cursor", first["page"]["next_cursor"])
    second = json.loads(out)["data"]
    assert code == 0
    assert {first["projects"][0]["display_name"], second["projects"][0]["display_name"]} == {"alpha", "zeta"}
    assert not second["page"]["has_more"]
