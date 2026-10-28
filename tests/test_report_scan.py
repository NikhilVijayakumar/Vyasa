import hashlib
import os
import sqlite3
import sys
from datetime import timedelta
from pathlib import Path

import pytest
from test_local_index import T0, make_run, repo, store

from vyasa.adapters.filesystem.report_file import read_report_file
from vyasa.adapters.sqlite import reports
from vyasa.adapters.sqlite.database import open_index
from vyasa.application.scanning.discovery import discover_repositories
from vyasa.domain.discovery import DiscoveryOptions
from vyasa.domain.report import EXAMPLE, INVALID, NOT_PRESENT, PRESENT, UNREADABLE, ReportLimits, ReportResult

GOOD = "## Overview\nHello\n\n## Architecture\nParts\n"


def write(directory, text, *, raw=None):
    folder = Path(directory, ".vyasa")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "project-report.md"
    if raw is not None:
        path.write_bytes(raw)
    else:
        path.write_bytes(text.encode("utf-8"))
    return path


# -- reading the file ---------------------------------------------------------------------------------


def test_no_vyasa_folder_is_not_present(tmp_path):
    assert read_report_file(str(tmp_path), ReportLimits()).status == NOT_PRESENT


def test_no_report_file_is_not_present(tmp_path):
    (tmp_path / ".vyasa").mkdir()
    assert read_report_file(str(tmp_path), ReportLimits()).status == NOT_PRESENT


def test_a_valid_report_is_read_with_its_hash_and_limits(tmp_path):
    write(tmp_path, GOOD)
    result = read_report_file(str(tmp_path), ReportLimits(512, 32))
    assert result.status == PRESENT
    assert [s.name for s in result.sections] == ["Overview", "Architecture"]
    assert result.content_hash == hashlib.sha256(GOOD.encode()).hexdigest()
    assert result.limits == ReportLimits(512, 32)


def test_an_oversize_file_is_invalid_and_names_the_limit(tmp_path):
    write(tmp_path, "## Overview\n" + "x" * (17 * 1024))
    result = read_report_file(str(tmp_path), ReportLimits(16, 1))
    assert result.status == INVALID and result.reason == "is larger than 16 KiB" and result.sections == ()


def test_a_file_exactly_at_the_limit_is_read(tmp_path):
    body = "## Overview\n" + "x" * (16 * 1024 - len("## Overview\n"))
    write(tmp_path, body)
    assert read_report_file(str(tmp_path), ReportLimits(16, 16)).status == PRESENT


def test_invalid_utf8_is_invalid(tmp_path):
    write(tmp_path, "", raw=b"## Overview\n\xff\xfe\n")
    result = read_report_file(str(tmp_path), ReportLimits())
    assert result.status == INVALID and result.reason == "is not valid UTF-8"


def test_a_directory_in_place_of_the_file_is_unreadable(tmp_path):
    (tmp_path / ".vyasa" / "project-report.md").mkdir(parents=True)
    result = read_report_file(str(tmp_path), ReportLimits())
    assert result.status == UNREADABLE and result.reason == "must be a regular file, not a link"


@pytest.mark.skipif(sys.platform == "win32", reason="symbolic links need privileges on Windows; junction case below")
def test_a_symbolic_link_is_not_followed(tmp_path):
    target = tmp_path / "secret.md"
    target.write_text(GOOD, encoding="utf-8")
    (tmp_path / ".vyasa").mkdir()
    os.symlink(target, tmp_path / ".vyasa" / "project-report.md")
    result = read_report_file(str(tmp_path), ReportLimits())
    assert result.status == UNREADABLE and result.sections == ()


@pytest.mark.skipif(sys.platform == "win32", reason="symbolic links need privileges on Windows")
def test_a_linked_vyasa_folder_is_not_followed(tmp_path):
    real = tmp_path / "elsewhere"
    write(real.parent / "elsewhere", GOOD)
    os.symlink(real / ".vyasa", tmp_path / ".vyasa")
    assert read_report_file(str(tmp_path), ReportLimits()).status == UNREADABLE


def test_reading_changes_nothing(tmp_path):
    path = write(tmp_path, GOOD)
    before = (path.read_bytes(), sorted(p.name for p in tmp_path.rglob("*")))
    read_report_file(str(tmp_path), ReportLimits())
    assert (path.read_bytes(), sorted(p.name for p in tmp_path.rglob("*"))) == before


# -- discovery carries the report ------------------------------------------------------------------------


def git_repo(path):
    (path / ".git").mkdir(parents=True)
    (path / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    return path


def test_discovery_reads_the_report_with_the_configured_limits(tmp_path):
    write(git_repo(tmp_path / "ws" / "alpha"), "## Overview\n" + "y" * 2048)
    run = discover_repositories(tmp_path / "ws", DiscoveryOptions(report_limits=ReportLimits(16, 1)))
    [candidate] = run.repositories
    assert candidate.report.status == PRESENT
    assert candidate.report.sections == () and candidate.report.dropped == (("Overview", "is larger than 1 KiB"),)


def test_a_manifest_project_without_git_also_carries_its_report(tmp_path):
    project = tmp_path / "ws" / "beta"
    project.mkdir(parents=True)
    (project / "pyproject.toml").write_text("[project]\nname='b'\n", encoding="utf-8")
    write(project, GOOD)
    [candidate] = discover_repositories(tmp_path / "ws").repositories
    assert [s.name for s in candidate.report.sections] == ["Overview", "Architecture"]


# -- storing ---------------------------------------------------------------------------------------------


@pytest.fixture
def db(tmp_path):
    connection = open_index(tmp_path / "data" / "index.sqlite3")
    yield connection
    connection.close()


def with_report(name, report):
    from dataclasses import replace

    return replace(repo(name), report=report)


def result(text=GOOD, limits=ReportLimits(), digest="h1"):
    from vyasa.domain.report import read_report

    return read_report(text, limits, digest)


def checkout_id(db):
    return db.execute("SELECT checkout_id FROM checkouts").fetchone()[0]


def observation(db):
    return db.execute("SELECT * FROM report_observations").fetchone()


def section_names(db):
    return [r[0] for r in db.execute("SELECT name FROM report_sections ORDER BY position")]


def test_a_report_is_stored_by_section_with_hash_time_and_limits(db):
    store(db, make_run([with_report("alpha", result(limits=ReportLimits(512, 32)))]))
    row = observation(db)
    assert (row["status"], row["content_hash"], row["max_file_bytes"], row["max_section_bytes"]) == ("present", "h1", 512 * 1024, 32 * 1024)
    assert row["scanned_at"] == T0.isoformat() and row["kept_hash"] == "h1" and row["kept_at"] == T0.isoformat()
    assert section_names(db) == ["Overview", "Architecture"]


def test_dropped_headings_are_stored(db):
    store(db, make_run([with_report("alpha", result("## Overview\nx\n## Gossip\ny\n"))]))
    assert reports.load(db, checkout_id(db))["dropped"] == [{"heading": "Gossip", "reason": "is not a section of the template"}]


def test_a_candidate_without_a_read_leaves_the_checkout_not_assessed(db):
    store(db, make_run([repo("alpha")]))  # no report attribute: nothing was read
    assert observation(db) is None and section_names(db) == []


def test_a_new_present_read_replaces_the_sections(db):
    store(db, make_run([with_report("alpha", result())]))
    store(db, make_run([with_report("alpha", result("## Modules\nm\n", digest="h2"))]), at=T0 + timedelta(hours=1))
    assert section_names(db) == ["Modules"] and observation(db)["kept_hash"] == "h2"


def test_a_failed_read_keeps_the_earlier_sections_and_their_origin(db):
    store(db, make_run([with_report("alpha", result())]))
    failed = ReportResult(UNREADABLE, reason="could not be read", limits=ReportLimits())
    store(db, make_run([with_report("alpha", failed)]), at=T0 + timedelta(hours=1))
    row = observation(db)
    assert (row["status"], row["reason"]) == ("unreadable", "could not be read")
    assert section_names(db) == ["Overview", "Architecture"]
    assert (row["kept_hash"], row["kept_at"]) == ("h1", T0.isoformat())
    assert row["scanned_at"] == (T0 + timedelta(hours=1)).isoformat()


def test_an_invalid_read_keeps_the_earlier_sections(db):
    store(db, make_run([with_report("alpha", result())]))
    store(db, make_run([with_report("alpha", ReportResult(INVALID, reason="is larger than 16 KiB"))]), at=T0 + timedelta(hours=1))
    assert observation(db)["status"] == "invalid" and section_names(db) == ["Overview", "Architecture"]


def test_a_vanished_report_deletes_the_sections(db):
    store(db, make_run([with_report("alpha", result())]))
    store(db, make_run([with_report("alpha", ReportResult(NOT_PRESENT))]), at=T0 + timedelta(hours=1))
    row = observation(db)
    assert row["status"] == "not_present" and row["kept_hash"] is None and section_names(db) == []


def test_the_example_stores_every_section(db):
    from vyasa.domain.report import SECTIONS, read_report

    store(db, make_run([with_report("alpha", read_report(EXAMPLE, ReportLimits(), "e"))]))
    assert section_names(db) == [name for name, _ in SECTIONS]


def test_latest_limits_come_from_the_newest_observation(db):
    assert reports.latest_limits(db) is None
    store(db, make_run([with_report("alpha", result(limits=ReportLimits(512, 32)))]))
    assert reports.latest_limits(db) == ReportLimits(512, 32)


# -- end to end through the scan command -------------------------------------------------------------------


def tree_hash(root):
    digest = hashlib.sha256()
    for path in sorted(Path(root).rglob("*")):
        digest.update(path.relative_to(root).as_posix().encode())
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def test_scan_command_stores_the_report_applies_config_limits_and_changes_nothing(tmp_path):
    import io

    from vyasa.adapters.cli.main import main
    from vyasa.application.indexing.store import index_path

    project = git_repo(tmp_path / "ws" / "alpha")
    write(project, "## Overview\nfine\n## Architecture\n" + "z" * 3000 + "\n## Gossip\nno\n## Modules\nsee https://u:p@h/x\n")
    config = tmp_path / "config.toml"
    config.write_text(f'[workspace]\nroots = ["{(tmp_path / "ws").as_posix()}"]\n[report]\nmax_section_kib = 1\n', encoding="utf-8")
    environ = {"VYASA_HOME": str(tmp_path / "home")}
    before = tree_hash(project)
    out, err = io.StringIO(), io.StringIO()
    assert main(["scan", "--config", str(config)], environ, out, err) in (0, 2)
    assert tree_hash(project) == before
    db = open_index(index_path(environ))
    try:
        assert section_names(db) == ["Overview"]
        row = observation(db)
        assert (row["max_file_bytes"], row["max_section_bytes"]) == (256 * 1024, 1024)
        dropped = reports.load(db, checkout_id(db))["dropped"]
        assert {d["heading"] for d in dropped} == {"Architecture", "Gossip", "Modules"}
    finally:
        db.close()

