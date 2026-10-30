import io
import json

from test_local_index import make_run, repo, store
from vyasa.adapters.cli.main import main
from vyasa.adapters.sqlite.database import open_index
from importlib.metadata import version


def run(args, home):
    out, err = io.StringIO(), io.StringIO()
    code = main(args, {"VYASA_HOME": str(home)}, out, err)
    return code, json.loads(out.getvalue()), err.getvalue()


def test_queries_an_existing_index_read_only(tmp_path):
    path = tmp_path / "index.sqlite3"
    conn = open_index(path)
    conn.close()
    before = path.read_bytes()
    for args in (["query", "status"], ["query", "search"]):
        code, result, err = run(args, tmp_path)
        assert code == 0 and not err
        assert result["schema_version"] == "1"
        assert "data" in result and "meta" in result
    assert path.read_bytes() == before


def test_missing_index_returns_error_without_creating_it(tmp_path):
    code, result, _ = run(["query", "status"], tmp_path)
    assert code != 0 and result["error"]["code"] == "INDEX_UNAVAILABLE"
    assert not (tmp_path / "index.sqlite3").exists()


def test_version_does_not_require_or_create_an_index(tmp_path):
    code, result, _ = run(["query", "version"], tmp_path)
    assert code == 0 and result["data"]["version"] == version("vyasa")
    assert not (tmp_path / "index.sqlite3").exists()


def test_invalid_search_and_missing_project_are_structured(tmp_path):
    conn = open_index(tmp_path / "index.sqlite3")
    conn.close()
    for args in (["query", "search", "--limit", "0"], ["query", "project", "absent"]):
        code, result, _ = run(args, tmp_path)
        assert code != 0 and result["error"]["code"]


def test_project_queries_share_the_indexed_identity_and_do_not_write(tmp_path):
    path = tmp_path / "index.sqlite3"
    conn = open_index(path)
    store(conn, make_run([repo("example")]))
    conn.close()
    before = path.read_bytes()
    code, result, _ = run(["query", "search", "--query", "example"], tmp_path)
    assert code == 0
    project_id = result["data"]["projects"][0]["project_id"]
    for operation in ("project", "dependencies", "context", "report"):
        code, result, err = run(["query", operation, project_id], tmp_path)
        assert code == 0 and not err
        assert result["schema_version"] == "1"
        assert "data" in result and "meta" in result
    assert path.read_bytes() == before
