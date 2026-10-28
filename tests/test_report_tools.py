import asyncio
import json

import pytest

pytest.importorskip("mcp")
from mcp import Client  # noqa: E402

from vyasa.adapters.mcp.server import build_server  # noqa: E402
from vyasa.domain.report import report_template  # noqa: E402


def call(index_file, name, arguments=None):
    async def go():
        async with Client(build_server(index_file)) as client:
            return await client.call_tool(name, arguments or {})
    return asyncio.run(go())


def test_template_needs_no_index_and_creates_nothing(tmp_path):
    missing = tmp_path / "none" / "index.sqlite3"
    result = call(missing, "get_report_template")
    assert not result.is_error
    assert result.structured_content["schema_version"] == "1"
    assert set(result.structured_content["meta"]) == {"generated_at"}
    assert result.structured_content["data"] == report_template()
    assert result.structured_content["data"]["limits"]["source"] == "default"
    assert json.loads(result.content[0].text) == result.structured_content
    assert not missing.parent.exists()


# -- stored reports through the tools ----------------------------------------------------------------------

from dataclasses import replace  # noqa: E402
from datetime import timedelta  # noqa: E402

from test_local_index import T0, make_run, repo, store  # noqa: E402

from vyasa.adapters.sqlite.database import open_index  # noqa: E402
from vyasa.domain.report import INVALID, NOT_PRESENT, SECTIONS, UNREADABLE, ReportLimits, ReportResult, read_report  # noqa: E402

TEXT = "## Overview\nHello world\n\n## Architecture\nParts and wiring\n"


@pytest.fixture
def index(tmp_path):
    path = tmp_path / "index.sqlite3"
    db = open_index(path)
    store(db, make_run([replace(repo("alpha"), report=read_report(TEXT, ReportLimits(512, 32), "h1")), repo("beta")]))
    db.close()
    return path


def project_id(index_file, name):
    db = open_index(index_file, read_only=True)
    try:
        return db.execute("SELECT project_id FROM projects WHERE display_name = ?", (name,)).fetchone()[0]
    finally:
        db.close()


def report_of(index_file, name, **arguments):
    return call(index_file, "get_project_report", {"project_id": project_id(index_file, name), **arguments})


def test_whole_report_is_served_as_declared_data(index):
    result = report_of(index, "alpha")
    assert not result.is_error
    [checkout] = result.structured_content["data"]["checkouts"]
    assert checkout["status"] == "present" and checkout["origin"] == "declared"
    assert checkout["content_hash"] == "h1" and checkout["scanned_at"] == T0.isoformat()
    assert [s["name"] for s in checkout["sections"]] == ["Overview", "Architecture"]
    assert checkout["sections"][0] == {"name": "Overview", "text": "Hello world", "size": 11}
    assert "untrusted" in result.structured_content["data"]["warning"]
    assert json.loads(result.content[0].text) == result.structured_content


def test_one_section_is_served_alone(index):
    [checkout] = report_of(index, "alpha", section="architecture").structured_content["data"]["checkouts"]
    assert [s["name"] for s in checkout["sections"]] == ["Architecture"]


def test_an_unknown_section_is_refused_with_the_allowed_names(index):
    result = report_of(index, "alpha", section="Gossip")
    assert result.is_error and result.structured_content["error"]["code"] == "INVALID_INPUT"
    assert "Overview" in result.structured_content["error"]["message"] and "Hello" not in json.dumps(result.structured_content)


def test_a_project_without_a_stored_observation_is_not_assessed(index):
    [checkout] = report_of(index, "beta").structured_content["data"]["checkouts"]
    assert checkout["status"] == "not_assessed" and checkout["sections"] == []


def test_a_project_whose_report_is_missing_says_not_present(tmp_path):
    path = tmp_path / "i.sqlite3"
    db = open_index(path)
    store(db, make_run([replace(repo("gamma"), report=ReportResult(NOT_PRESENT))]))
    db.close()
    [checkout] = report_of(path, "gamma").structured_content["data"]["checkouts"]
    assert checkout["status"] == "not_present" and checkout["sections"] == []


def test_unknown_project_is_refused(index):
    result = call(index, "get_project_report", {"project_id": "nope"})
    assert result.is_error and result.structured_content["error"]["code"] == "PROJECT_NOT_FOUND"


def test_earlier_sections_stay_servable_after_a_failed_read_and_say_where_they_came_from(tmp_path):
    path = tmp_path / "i.sqlite3"
    db = open_index(path)
    store(db, make_run([replace(repo("alpha"), report=read_report(TEXT, ReportLimits(), "h1"))]))
    failed = ReportResult(UNREADABLE, reason="could not be read")
    store(db, make_run([replace(repo("alpha"), report=failed)]), at=T0 + timedelta(hours=1))
    db.close()
    [checkout] = report_of(path, "alpha").structured_content["data"]["checkouts"]
    assert (checkout["status"], checkout["reason"]) == ("unreadable", "could not be read")
    assert [s["name"] for s in checkout["sections"]] == ["Overview", "Architecture"]
    assert checkout["kept_from"] == {"content_hash": "h1", "scanned_at": T0.isoformat()}


def test_project_details_show_status_only(index):
    result = call(index, "get_project", {"project_id": project_id(index, "alpha")})
    [checkout] = result.structured_content["data"]["checkouts"]
    report = checkout["report"]
    assert report["status"] == "present" and report["sections"] == [{"name": "Overview", "size": 11}, {"name": "Architecture", "size": 16}]
    assert "Hello" not in json.dumps(report) and report["dropped"] == []


def test_project_details_for_an_unassessed_checkout(index):
    [checkout] = call(index, "get_project", {"project_id": project_id(index, "beta")}).structured_content["data"]["checkouts"]
    assert checkout["report"]["status"] == "not_assessed"


def test_no_local_path_crosses_the_boundary(index):
    assert "/ws" not in json.dumps(report_of(index, "alpha").structured_content)


def test_the_template_shows_the_limits_of_the_latest_scan(index):
    data = call(index, "get_report_template").structured_content["data"]
    assert data["limits"] == {"max_file_bytes": 512 * 1024, "max_section_bytes": 32 * 1024, "source": "index"}


def test_the_template_falls_back_to_defaults_on_an_index_without_report_data(tmp_path):
    path = tmp_path / "i.sqlite3"
    db = open_index(path)
    store(db, make_run([repo("alpha")]))
    db.close()
    assert call(path, "get_report_template").structured_content["data"]["limits"]["source"] == "default"


def test_an_index_from_before_reports_answers_not_assessed(tmp_path):
    path = tmp_path / "i.sqlite3"
    db = open_index(path)
    store(db, make_run([repo("alpha")]))
    db.execute("DROP TABLE report_sections")
    db.execute("DROP TABLE report_observations")
    db.close()
    [checkout] = report_of(path, "alpha").structured_content["data"]["checkouts"]
    assert checkout["status"] == "not_assessed"
    assert call(path, "get_report_template").structured_content["data"]["limits"]["source"] == "default"


def test_the_tools_are_read_only_and_the_index_is_unchanged(index):
    before = index.read_bytes()
    report_of(index, "alpha")
    call(index, "get_report_template")
    assert index.read_bytes() == before


def test_report_tool_inputs_are_not_paths(index):
    from test_mcp_server import tools

    [tool] = [t for t in tools(index) if t.name == "get_project_report"]
    assert set(tool.input_schema["properties"]) == {"project_id", "section"}
    assert {name for name, _ in SECTIONS} >= {"Overview"} and INVALID == "invalid"
