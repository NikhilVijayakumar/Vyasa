import json
import sqlite3
from datetime import timedelta
from pathlib import Path

import pytest
from test_local_index import ROOT, T0, db, make_run, repo, store  # noqa: F401

from vyasa.adapters.sqlite import projects
from vyasa.adapters.sqlite.database import open_index
from vyasa.application import query
from vyasa.domain.discovery import Candidate
from vyasa.domain.git_remote import GitRemote
from vyasa.domain.index import INVALID_CURSOR, INVALID_INPUT, PROJECT_NOT_FOUND, IndexStoreError

NOW = lambda: T0 + timedelta(hours=1)  # noqa: E731


def remote(identity, provider="github"):
    return GitRemote("origin", provider, "h", identity)


def names(result):
    return [p["display_name"] for p in result["data"]["projects"]]


def search(db, **kw):
    return query.search_projects(db, now=NOW, **kw)


def error(fn, *a, **kw):
    with pytest.raises(IndexStoreError) as e:
        fn(*a, **kw)
    return e.value.code


@pytest.fixture
def reader(tmp_path):
    """An index with a spread of projects, opened read-only."""
    path = tmp_path / "index.sqlite3"
    writer = open_index(path)
    store(writer, make_run([
        repo("billing-api", remote("github.com/acme/billing")),
        repo("Web", remote("bitbucket.org/acme/web", "bitbucket")),
        repo("tool", remote("github.com/acme/tool")),
        repo("local-only"),
        repo("gone", remote("github.com/acme/gone")),
    ]))
    store(writer, make_run([
        repo("billing-api", remote("github.com/acme/billing")),
        repo("Web", remote("bitbucket.org/acme/web", "bitbucket")),
        repo("tool", remote("github.com/acme/tool")),
        repo("local-only"),
    ]), at=T0 + timedelta(minutes=1))
    writer.close()
    connection = open_index(path, read_only=True)
    yield connection
    connection.close()


# -- envelope ------------------------------------------------------------------------------------------


def test_envelope(reader):
    result = search(reader)
    assert result["schema_version"] == "1"
    assert set(result["meta"]) == {"generated_at", "index_version", "freshness"}
    assert result["meta"]["index_version"] >= 4 and result["meta"]["freshness"] == "current"


# -- search --------------------------------------------------------------------------------------------


def test_order_is_by_lowercase_name(reader):
    assert names(search(reader)) == ["billing-api", "gone", "local-only", "tool", "Web"]


def test_repeat_is_identical(reader):
    assert search(reader, query="a") == search(reader, query="a")


def test_paging_covers_everything_once(tmp_path):
    path = tmp_path / "i.sqlite3"
    w = open_index(path)
    store(w, make_run([repo(f"p{i:02d}") for i in range(45)]))
    w.close()
    r = open_index(path, read_only=True)
    seen, cursor, pages = [], None, 0
    while True:
        result = query.search_projects(r, limit=20, cursor=cursor, now=NOW)
        seen += names(result)
        pages += 1
        cursor = result["data"]["page"]["next_cursor"]
        if not cursor:
            assert result["data"]["page"]["has_more"] is False
            break
    assert pages == 3 and seen == [f"p{i:02d}" for i in range(45)]


@pytest.mark.parametrize("limit", [0, 101, -1, "5", 2.5, True])
def test_bad_limit(reader, limit):
    assert error(search, reader, limit=limit) == INVALID_INPUT


def test_default_and_max_limit(reader):
    assert search(reader)["data"]["page"]["limit"] == 20
    assert search(reader, limit=100)["data"]["page"]["limit"] == 100


@pytest.mark.parametrize("cursor", ["nonsense", "e30=", "WyJhIl0="])
def test_bad_cursor(reader, cursor):
    assert error(search, reader, cursor=cursor) == INVALID_CURSOR


def test_name_match_is_case_insensitive_and_says_why(reader):
    result = search(reader, query="BILL")
    assert names(result) == ["billing-api"]
    assert result["data"]["projects"][0]["matched"] == ["display_name", "remote_identity"]  # its remote also contains "billing"
    [web] = search(reader, query="WEB")["data"]["projects"]
    assert web["matched"] == ["display_name", "remote_identity"]
    assert search(reader, query="api")["data"]["projects"][0]["matched"] == ["display_name"]


def test_remote_match(reader):
    [item] = search(reader, query="acme/tool")["data"]["projects"]
    assert item["display_name"] == "tool" and item["matched"] == ["remote_identity"]


@pytest.mark.parametrize("text", ["%", "_", "\\"])
def test_wildcards_are_literal(reader, text):
    assert names(search(reader, query=text)) == []


def test_combined_filters(reader):
    assert names(search(reader, state="active", provider="github")) == ["billing-api", "tool"]
    assert names(search(reader, state="missing")) == ["gone"]


def test_values_within_a_filter_are_or(reader):
    assert names(search(reader, provider=["github", "bitbucket"], state="active")) == ["billing-api", "tool", "Web"]


def test_local_projects_have_provider_none(reader):
    assert names(search(reader, provider="none")) == ["local-only"]


def test_identity_status_filter(reader):
    assert names(search(reader, identity_status="provisional")) == ["local-only"]


@pytest.mark.parametrize("kw", [{"state": "retired"}, {"provider": "svn"}, {"identity_status": "maybe"}, {"state": 3}])
def test_unknown_filter_values(reader, kw):
    assert error(search, reader, **kw) == INVALID_INPUT


@pytest.mark.parametrize("text", ["", "x" * 201, 5])
def test_bad_query(reader, text):
    assert error(search, reader, query=text) == INVALID_INPUT


def test_no_match_is_empty_not_an_error(reader):
    result = search(reader, query="zzz")
    assert result["data"] == {"projects": [], "page": {"limit": 20, "next_cursor": None, "has_more": False}}


# -- one project ----------------------------------------------------------------------------------------------


def pid(db, name):
    return next(r["project_id"] for r in projects.list_projects(db) if r["display_name"] == name)


def test_resolved_project_with_two_checkouts(tmp_path):
    path = tmp_path / "i.sqlite3"
    w = open_index(path)
    store(w, make_run([repo("a", remote("h/o/r")), repo("b", remote("h/o/r"))]))
    w.close()
    r = open_index(path, read_only=True)
    data = query.get_project(r, pid(r, "a"), now=NOW)["data"]
    assert data["identity"] == {"status": "resolved", "source": "remote", "aliases": ["h/o/r"]}
    assert len(data["checkouts"]) == 2
    assert [c["kind"] for c in data["review_candidates"]] == ["duplicate_checkout"]
    assert data["review_candidates"][0]["review_status"] == "open"


def test_local_project_marks_an_absent_remote(reader):
    data = query.get_project(reader, pid(reader, "local-only"), now=NOW)["data"]
    assert data["identity"]["status"] == "provisional"
    assert data["checkouts"][0]["remote"] == {"provider": "none", "host": None, "identity": None, "status": "none"}
    assert data["review_candidates"] == []


def test_unknown_or_bad_project_id(reader):
    assert error(query.get_project, reader, "nope") == PROJECT_NOT_FOUND
    assert error(query.get_project, reader, "") == INVALID_INPUT


# -- status ---------------------------------------------------------------------------------------------------


def test_status_of_an_empty_index(tmp_path):
    w = open_index(tmp_path / "i.sqlite3")
    w.close()
    r = open_index(tmp_path / "i.sqlite3", read_only=True)
    result = query.get_index_status(r, now=NOW)
    assert result["meta"]["freshness"] == "unknown"
    assert result["data"] == {"latest_run": None, "projects": {"total": 0, "active": 0, "missing": 0, "inaccessible": 0}, "open_candidates": 0}


def test_status_after_a_run(reader):
    result = query.get_index_status(reader, now=NOW)
    assert result["meta"]["freshness"] == "current"
    assert result["data"]["latest_run"]["status"] == "completed"
    assert result["data"]["projects"] == {"total": 5, "active": 4, "missing": 1, "inaccessible": 0}


# -- read-only and paths ---------------------------------------------------------------------------------------


def strings(value):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from strings(k)
            yield from strings(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from strings(v)
    elif isinstance(value, str):
        yield value


def test_no_path_or_root_by_default(reader):
    results = [search(reader), query.get_project(reader, pid(reader, "tool"), now=NOW), query.get_index_status(reader, now=NOW)]
    for result in results:
        assert not [s for s in strings(result) if str(ROOT) in s or s.startswith("/ws")]


def test_paths_on_request(reader):
    data = query.get_project(reader, pid(reader, "tool"), include_paths=True, now=NOW)["data"]
    assert data["checkouts"][0]["path"] == str(ROOT / "tool")


def test_queries_cannot_write_and_leave_the_file_alone(reader, tmp_path):
    path = tmp_path / "index.sqlite3"
    before = path.read_bytes()
    search(reader, query="a")
    query.get_index_status(reader, now=NOW)
    with pytest.raises(sqlite3.OperationalError):
        reader.execute("DELETE FROM projects")
    assert path.read_bytes() == before
