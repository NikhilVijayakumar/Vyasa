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
