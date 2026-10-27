import asyncio
import json
import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pytest
from test_local_index import ROOT, T0, make_run, repo, store

pytest.importorskip("mcp", reason="the optional 'mcp' extra is not installed")

from mcp.client import Client  # noqa: E402
from mcp.client.stdio import StdioServerParameters, stdio_client  # noqa: E402
from mcp.client import ClientSession  # noqa: E402

from vyasa.adapters.mcp.server import build_server  # noqa: E402
from vyasa.adapters.sqlite.database import open_index  # noqa: E402
from vyasa.domain.git_remote import GitRemote  # noqa: E402

SNAPSHOT = Path(__file__).parent / "snapshots" / "mcp_tools.json"
SRC = Path(__file__).resolve().parents[1] / "src"
TOOLS = ["get_index_status", "get_profile_guide", "get_project", "search_projects"]


def remote(identity):
    return GitRemote("origin", "github", "github.com", identity)


@pytest.fixture
def index(tmp_path):
    path = tmp_path / "index.sqlite3"
    w = open_index(path)
    store(w, make_run([repo("alpha", remote("github.com/acme/alpha")), repo("beta")]))
    w.close()
    return path


def call(index_file, name, arguments=None):
    async def go():
        async with Client(build_server(index_file)) as client:
            return await client.call_tool(name, arguments or {})
    return asyncio.run(go())


def tools(index_file):
    async def go():
        async with Client(build_server(index_file)) as client:
            return (await client.list_tools()).tools
    return asyncio.run(go())


# -- listing and pinning --------------------------------------------------------------------------------


def test_exactly_four_read_tools(index):
    listed = tools(index)
    assert sorted(t.name for t in listed) == TOOLS
    assert all(t.description and t.input_schema for t in listed)


def test_read_only_annotations(index):
    for t in tools(index):
        a = t.annotations
        assert (a.read_only_hint, a.destructive_hint, a.idempotent_hint, a.open_world_hint) == (True, False, True, False)


def snapshot_of(listed):
    return [t.model_dump(exclude_none=True, mode="json") for t in sorted(listed, key=lambda t: t.name)]


def test_tool_list_matches_the_committed_snapshot(index):
    live = snapshot_of(tools(index))
    if os.environ.get("VYASA_UPDATE_SNAPSHOT"):
        SNAPSHOT.write_text(json.dumps(live, indent=2, sort_keys=True) + "\n")
    assert live == json.loads(SNAPSHOT.read_text()), "tool contract changed: regenerate with VYASA_UPDATE_SNAPSHOT=1 and note it"


def test_no_tool_takes_a_path(index):
    for t in tools(index):
        for name, spec in t.input_schema.get("properties", {}).items():
            text = (name + " " + str(spec.get("description", ""))).lower()
            assert "path" not in text and name != "include_paths"


def test_unregistered_tool_is_not_served(index):
    result = call(index, "get_project_context", {"project_id": "x"})
    assert result.is_error and not result.structured_content


# -- results ---------------------------------------------------------------------------------------------------


def test_search_returns_an_envelope(index):
    result = call(index, "search_projects", {"query": "alp"})
    assert not result.is_error
    body = result.structured_content
    assert body["schema_version"] == "1" and set(body["meta"]) == {"generated_at", "index_version", "freshness"}
    assert [p["display_name"] for p in body["data"]["projects"]] == ["alpha"]
    assert json.loads(result.content[0].text) == body


def test_project_and_status(index):
    pid = call(index, "search_projects", {"query": "alpha"}).structured_content["data"]["projects"][0]["project_id"]
    project = call(index, "get_project", {"project_id": pid}).structured_content
    assert project["data"]["identity"]["aliases"] == ["github.com/acme/alpha"]
    status = call(index, "get_index_status").structured_content
    assert status["data"]["projects"]["total"] == 2


def test_tools_leave_the_index_untouched(index):
    before = index.read_bytes()
    pid = call(index, "search_projects").structured_content["data"]["projects"][0]["project_id"]
    call(index, "get_project", {"project_id": pid})
    call(index, "get_index_status")
    assert index.read_bytes() == before


def test_no_result_contains_the_root(index):
    pid = call(index, "search_projects").structured_content["data"]["projects"][0]["project_id"]
    for result in (call(index, "search_projects"), call(index, "get_project", {"project_id": pid}), call(index, "get_index_status")):
        assert str(ROOT) not in json.dumps(result.structured_content)


# -- failures --------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("name,args,code", [
    ("search_projects", {"state": "retired"}, "INVALID_INPUT"),
    ("search_projects", {"limit": 0}, "INVALID_INPUT"),
    ("search_projects", {"cursor": "junk"}, "INVALID_CURSOR"),
    ("get_project", {"project_id": "nope"}, "PROJECT_NOT_FOUND"),
])
def test_domain_failures_are_structured(index, name, args, code):
    result = call(index, name, args)
    assert result.is_error and result.structured_content["error"]["code"] == code
    assert result.structured_content["error"]["message"]


def test_missing_index_is_reported_and_not_created(tmp_path):
    missing = tmp_path / "none" / "index.sqlite3"
    result = call(missing, "get_index_status")
    assert result.is_error and result.structured_content["error"]["code"] == "INDEX_UNAVAILABLE"
    assert str(tmp_path) not in json.dumps(result.structured_content)
    assert not missing.parent.exists()


def test_unexpected_errors_are_generic(index, monkeypatch, capsys):
    from vyasa.application import query

    def boom(*a, **k):
        raise RuntimeError("secret detail /home/x")

    monkeypatch.setattr(query, "get_index_status", boom)
    result = call(index, "get_index_status")
    assert result.structured_content["error"]["code"] == "INTERNAL_ERROR"
    assert "secret" not in json.dumps(result.structured_content)


# -- stdio ------------------------------------------------------------------------------------------------------


def test_stdio_subprocess_lists_tools_and_answers(index, tmp_path):
    env = {**os.environ, "VYASA_HOME": str(index.parent), "PYTHONPATH": str(SRC)}
    # The server reads <VYASA_HOME>/index.sqlite3, which is exactly where the fixture put it.
    params = StdioServerParameters(command=sys.executable, args=["-m", "vyasa.adapters.mcp"], env=env)

    async def go():
        async with stdio_client(params) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                listed = await session.list_tools()
                status = await session.call_tool("get_index_status", {})
                return [t.name for t in listed.tools], status

    names, status = asyncio.run(asyncio.wait_for(go(), 30))
    assert sorted(names) == TOOLS
    assert status.structured_content["data"]["projects"]["total"] == 2


# -- the SDK is optional ----------------------------------------------------------------------------------------


def run_blocked(code):
    blocker = "import sys; sys.modules['mcp'] = None; "
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    return subprocess.run([sys.executable, "-c", blocker + code], capture_output=True, text=True, env=env, timeout=60)


def test_core_works_without_the_sdk(tmp_path):
    code = (
        "from vyasa.adapters.sqlite.database import open_index\n"
        "from vyasa.application import query\n"
        f"c = open_index(r'{tmp_path / 'i.sqlite3'}')\n"
        "print(query.get_index_status(c)['data']['projects']['total'])"
    )
    done = run_blocked(code)
    assert done.returncode == 0 and done.stdout.strip() == "0", done.stderr


def test_entry_point_hints_when_the_sdk_is_missing():
    done = run_blocked("from vyasa.adapters.mcp.launch import main; main()")
    assert done.returncode == 2 and "vyasa[mcp]" in done.stderr and done.stdout == ""


# -- the profile guide ---------------------------------------------------------------------------------------


def test_guide_needs_no_index_and_creates_nothing(tmp_path):
    missing = tmp_path / "none" / "index.sqlite3"
    result = call(missing, "get_profile_guide")
    assert not result.is_error and result.structured_content["schema_version"] == "1"
    assert set(result.structured_content["meta"]) == {"generated_at"}
    assert not missing.parent.exists()


def test_guide_tool_returns_the_domain_guide(index):
    from vyasa.domain.profile import profile_guide

    result = call(index, "get_profile_guide")
    assert result.structured_content["data"] == profile_guide()
    assert json.loads(result.content[0].text) == result.structured_content


def test_guide_tool_takes_no_input(index):
    [tool] = [t for t in tools(index) if t.name == "get_profile_guide"]
    assert tool.input_schema.get("properties", {}) == {}
