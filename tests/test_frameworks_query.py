import shutil
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest
from test_language_query import report, scanned  # noqa: F401
from test_local_index import LATEST, ROOT, T0, db, make_run, repo, store  # noqa: F401

from vyasa.adapters.sqlite.database import open_index
from vyasa.application import query
from vyasa.application.indexing.scan import scan_workspace
from vyasa.application.scanning.frameworks import default_registry, technologies_of
from vyasa.domain.discovery import PARTIAL
from vyasa.domain.frameworks import Dependency, FrameworkReport, ManifestResult
from vyasa.domain.git_remote import GitRemote
from vyasa.domain.index import INVALID_INPUT, IndexStoreError
from vyasa.domain.languages import CheckoutScan, LanguageOutcome
from vyasa.domain.workspace_config import WorkspaceConfig

NOW = lambda: T0 + timedelta(hours=1)  # noqa: E731
REGISTRY = default_registry()


def mf(path, ecosystem, *deps, status="parsed", reason=None, skipped=0, workspace=False, total=None):
    dependencies = tuple(Dependency(n, c, s) for n, c, s in deps)
    return ManifestResult(path, ecosystem, status, reason, dependencies, total if total is not None else len(dependencies), skipped, workspace)


def fw(*manifests, nested=(), stopped_by=None):
    return FrameworkReport(tuple(manifests), tuple(nested), technologies_of(tuple(manifests), REGISTRY), REGISTRY.version, stopped_by)


def framed(name, framework=None, identity=None, languages=(), stopped_by=None):
    outcome = LanguageOutcome(report(languages, stopped_by=stopped_by), frameworks=framework)
    remote = GitRemote("origin", "github", "github.com", identity) if identity else None
    return replace(repo(name, remote), languages=outcome)


def rows(db, table, name):
    return [tuple(r) for r in db.execute(
        f"SELECT t.* FROM {table} t JOIN language_observations o USING (observation_id) JOIN checkouts c USING (checkout_id)"
        " WHERE c.path LIKE ? ORDER BY o.observation_id, 2, 3", (f"%{name}",))]


def version(db, name):
    return [r[0] for r in db.execute(
        "SELECT o.frameworks_version FROM language_observations o JOIN checkouts c USING (checkout_id)"
        " WHERE c.path LIKE ? ORDER BY o.observation_id", (f"%{name}",))]


PY = mf("pyproject.toml", "python", ("fastapi", ">=0.1", "runtime"), ("pytest", None, "dev"), ("leftover", "1", "runtime"), skipped=2)
JS = mf("package.json", "javascript", ("react", "^18", "runtime"), workspace=True)


# --- store ---

def test_version_8_index_upgrades_with_null_versions(tmp_path):
    steps = tmp_path / "old"
    steps.mkdir()
    for file in sorted(Path(__file__).parents[1].joinpath("src/vyasa/adapters/sqlite/migrations").glob("000[1-8]_*.sql")):
        shutil.copy(file, steps / file.name)
    old = open_index(tmp_path / "i.sqlite3", migrations=steps)
    store(old, make_run([repo("a")]))
    old.execute("INSERT INTO language_observations (checkout_id, run_id, observed_at, status, types_version)"
                " SELECT checkout_id, last_run_id, ?, 'complete', 2 FROM checkouts", (T0.isoformat(),))
    old.close()
    new = open_index(tmp_path / "i.sqlite3")
    assert new.execute("PRAGMA user_version").fetchone()[0] == LATEST >= 9
    assert [tuple(r) for r in new.execute("SELECT frameworks_version FROM language_observations")] == [(None,)]


def test_frameworks_are_stored_with_the_observation(db):
    store(db, make_run([framed("a", fw(PY, JS, nested=[("javascript", 2)]))]))
    assert version(db, "a") == [REGISTRY.version]
    assert rows(db, "checkout_manifests", "a") == [
        (rows(db, "checkout_manifests", "a")[0][0], "package.json", "javascript", "parsed", None, 1, 0, 1, None),
        (rows(db, "checkout_manifests", "a")[1][0], "pyproject.toml", "python", "parsed", None, 3, 2, 0, None),
    ]
    deps = [r[1:] for r in rows(db, "checkout_dependencies", "a")]
    assert ("pyproject.toml", "fastapi", ">=0.1", "runtime") in [(p, n, c, s) for p, n, c, s in deps]
    assert len(deps) == 4
    assert [(r[1], r[2], r[3]) for r in rows(db, "checkout_technologies", "a")] == [
        ("fastapi", '["runtime"]', '["pyproject.toml"]'), ("pytest", '["dev"]', '["pyproject.toml"]'), ("react", '["runtime"]', '["package.json"]')]
    assert [r[1:] for r in rows(db, "checkout_nested_manifests", "a")] == [("javascript", 2)]


def test_non_parsed_manifests_store_status_and_reason_only(db):
    bad = mf("package.json", "javascript", status="malformed", reason="syntax")
    store(db, make_run([framed("a", fw(bad))]))
    (row,) = rows(db, "checkout_manifests", "a")
    assert row[1:6] == ("package.json", "javascript", "malformed", "syntax", 0)
    assert rows(db, "checkout_dependencies", "a") == [] and rows(db, "checkout_technologies", "a") == []


def test_complete_scan_without_manifests_still_has_a_version(db):
    store(db, make_run([framed("a", fw())]))
    assert version(db, "a") == [REGISTRY.version] and rows(db, "checkout_manifests", "a") == []


def test_partial_walk_stores_what_was_found(db):
    store(db, make_run([framed("a", fw(JS, stopped_by="entries"), stopped_by="entries")]))
    assert version(db, "a") == [REGISTRY.version] and len(rows(db, "checkout_manifests", "a")) == 1


def test_failed_and_unframed_outcomes_store_no_version(db):
    store(db, make_run([replace(repo("f"), languages=LanguageOutcome(failed="detection_error")),
                        replace(repo("u"), languages=LanguageOutcome(report()))]))
    assert version(db, "f") == [None] and version(db, "u") == [None]


def test_retention_keeps_two_observations_with_their_frameworks(db):
    for i, manifest in enumerate([JS, PY, mf("Cargo.toml", "rust", ("tokio", "1", "runtime"))]):
        store(db, make_run([framed("a", fw(manifest))]), at=T0 + timedelta(minutes=i))
    assert [r[1] for r in rows(db, "checkout_manifests", "a")] == ["pyproject.toml", "Cargo.toml"]
    assert db.execute("SELECT count(*) FROM checkout_technologies").fetchone()[0] == 3  # fastapi, pytest, tokio
    assert db.execute("SELECT count(*) FROM checkout_dependencies").fetchone()[0] == 4


# --- scan ---

def config(tmp_path):
    return WorkspaceConfig(roots=(ROOT,), source=tmp_path / "c.toml")


def test_scan_stores_frameworks_from_the_scan_result(db, tmp_path):
    def detect(path):
        scan = scanned(report())
        return CheckoutScan(scan.composition, scan.languages, None, fw(JS))

    scan_workspace(config(tmp_path), db, owner="o", discover=lambda r: make_run([repo("a")]), detect=detect)
    assert [r[1] for r in rows(db, "checkout_technologies", "a")] == ["react"]


def test_failing_detection_is_isolated_and_marks_the_run_partial(db, tmp_path):
    def detect(path):
        if path.name == "bad":
            raise RuntimeError("secret")
        scan = scanned(report())
        return CheckoutScan(scan.composition, scan.languages, None, fw(JS))

    (result,) = scan_workspace(config(tmp_path), db, owner="o", discover=lambda r: make_run([repo("good"), repo("bad")]), detect=detect)
    assert result.stored.status == "partial" and result.run.status == PARTIAL
    assert version(db, "bad") == [None] and version(db, "good") == [REGISTRY.version]


def test_real_scan_reads_a_real_manifest(db, tmp_path):
    from vyasa.domain.discovery import Candidate

    root = tmp_path / "ws" / "proj"
    root.mkdir(parents=True)
    (root / "package.json").write_text('{"dependencies": {"react": "^18"}, "devDependencies": {"jest": "^29"}}', encoding="utf-8")
    (root / "setup.py").write_text("raise SystemExit('executed!')", encoding="utf-8")
    cand = Candidate(root, "eligible", kind="repository", markers=("package.json",), git=".", remote=None, remote_status="none")
    scan_workspace(WorkspaceConfig(roots=(tmp_path / "ws",), source=tmp_path / "c"), db, owner="o",
                   discover=lambda r: replace(make_run([]), repositories=(cand,), root=tmp_path / "ws"))
    assert [r[1] for r in rows(db, "checkout_technologies", "proj")] == ["jest", "react"]


# --- search ---

@pytest.fixture
def reader(db):
    def run(with_gone):
        runs = [
            framed("api", fw(PY)),
            framed("web", fw(JS)),
            framed("bare", fw()),
            framed("broken", fw(mf("package.json", "javascript", status="malformed", reason="syntax"))),
            framed("cut", fw(stopped_by="entries"), stopped_by="entries"),
            replace(repo("old"), languages=LanguageOutcome(report())), repo("plain"),
            replace(repo("failed"), languages=LanguageOutcome(failed="detection_error")),
            framed("both1", fw(mf("pyproject.toml", "python", ("django", "4", "runtime"))), identity="github.com/acme/both"),
            framed("both2", fw(JS), identity="github.com/acme/both", languages=(("Python", 1),)),
        ]
        return runs + ([framed("gone", fw(mf("Cargo.toml", "rust", ("tokio", "1", "runtime"))))] if with_gone else [])

    store(db, make_run(run(True)))
    store(db, make_run(run(False)), at=T0 + timedelta(minutes=5))
    return db


def search(db, **kw):
    return query.search_projects(db, now=NOW, **kw)


def names(result):
    return sorted(p["display_name"] for p in result["data"]["projects"])


def details(db, name):
    pid = next(p["project_id"] for p in search(db)["data"]["projects"] if p["display_name"] == name)
    return query.get_project(db, pid, now=NOW)["data"]


def code(db, **kw):
    with pytest.raises(IndexStoreError) as caught:
        search(db, **kw)
    return caught.value


def test_search_by_technology(reader):
    assert names(search(reader, technology="fastapi")) == ["api"]


def test_search_several_keys_is_or(reader):
    assert names(search(reader, technology=["react", "django"])) == ["both1", "web"]


def test_key_case_is_ignored(reader):
    assert names(search(reader, technology="FastAPI")) == ["api"]


def test_dev_declaration_counts(reader):
    assert names(search(reader, technology="pytest")) == ["api"]
    (pytest_row,) = [t for t in details(reader, "api")["checkouts"][0]["frameworks"]["technologies"] if t["key"] == "pytest"]
    assert pytest_row["scopes"] == ["dev"]


def test_any_active_checkout_matches(reader):
    assert "both1" in names(search(reader, technology="django")) and "both1" in names(search(reader, technology="react"))


def test_missing_checkout_does_not_match(reader):
    assert "gone" not in names(search(reader, technology="tokio"))


def test_malformed_partial_and_unassessed_match_nothing(reader):
    everything = names(search(reader, technology=list(REGISTRY.keys())))
    assert not {"broken", "cut", "old", "plain", "failed", "bare"} & set(everything)


def test_combined_with_a_language_filter(reader):
    assert names(search(reader, technology="react", language="Python")) == ["both1"]


def test_unknown_key_lists_the_allowed(reader):
    error = code(reader, technology="fastapii")
    assert error.code == INVALID_INPUT and "fastapii" in str(error) and "fastapi" in str(error) and "react" in str(error)


@pytest.mark.parametrize("value", [3, "", [], [1], ["react", 2]])
def test_wrong_types_are_rejected(reader, value):
    assert code(reader, technology=value).code == INVALID_INPUT


def test_filter_value_is_bound_not_executed(reader):
    assert code(reader, technology="x'; DROP TABLE projects; --").code == INVALID_INPUT
    assert reader.execute("SELECT count(*) FROM projects").fetchone()[0] > 0


# --- details ---

def frameworks(db, name):
    return [c["frameworks"] for c in details(db, name)["checkouts"]]


def eco(f, name):
    return next(e for e in f["ecosystems"] if e["ecosystem"] == name)


def test_complete_observation_states_every_ecosystem(reader):
    (f,) = frameworks(reader, "api")
    assert (f["status"], f["registry_version"], f["stopped_by"]) == ("complete", REGISTRY.version, None)
    assert [e["ecosystem"] for e in f["ecosystems"]] == ["python", "javascript", "rust", "go"]
    assert eco(f, "python")["state"] == "detected" and eco(f, "javascript")["state"] == "not_detected"


def test_manifest_evidence(reader):
    (f,) = frameworks(reader, "api")
    (manifest,) = eco(f, "python")["manifests"]
    assert (manifest["path"], manifest["status"], manifest["reason"], manifest["total_dependencies"], manifest["skipped"], manifest["workspace"]) == (
        "pyproject.toml", "parsed", None, 3, 2, False)
    assert {"name": "fastapi", "constraint": ">=0.1", "scope": "runtime"} in manifest["dependencies"]
    (web,) = frameworks(reader, "web")
    assert eco(web, "javascript")["manifests"][0]["workspace"] is True


def test_technologies_carry_registry_names(reader):
    (f,) = frameworks(reader, "api")
    fastapi = next(t for t in f["technologies"] if t["key"] == "fastapi")
    assert fastapi == {"key": "fastapi", "name": "FastAPI", "category": "web-framework", "scopes": ["runtime"], "manifests": ["pyproject.toml"]}


def test_malformed_manifest_is_detected_and_claims_nothing(reader):
    (f,) = frameworks(reader, "broken")
    manifest = eco(f, "javascript")["manifests"][0]
    assert eco(f, "javascript")["state"] == "detected" and (manifest["status"], manifest["reason"]) == ("malformed", "syntax")
    assert manifest["dependencies"] == [] and f["technologies"] == []


def test_partial_walk_makes_absent_ecosystems_unknown(reader):
    (f,) = frameworks(reader, "cut")
    assert f["status"] == "partial" and f["stopped_by"] == "entries"
    assert {e["state"] for e in f["ecosystems"]} == {"unknown"}


def test_not_assessed_for_old_failed_and_unscanned(reader):
    for name in ("old", "failed", "plain"):
        (f,) = frameworks(reader, name)
        assert (f["status"], f["registry_version"], f["ecosystems"], f["technologies"]) == ("not_assessed", None, [], [])


def test_nested_manifests_are_reported(db):
    store(db, make_run([framed("a", fw(nested=[("javascript", 3)]))]))
    (f,) = frameworks(db, "a")
    assert eco(f, "javascript")["nested_not_parsed"] == 3 and eco(f, "javascript")["state"] == "not_detected"
    assert eco(f, "python")["nested_not_parsed"] == 0 and f["technologies"] == []


def test_checkouts_are_not_combined(reader):
    data = details(reader, "both1")
    assert sorted(len(c["frameworks"]["technologies"]) for c in data["checkouts"]) == [1, 1]
    assert "frameworks" not in data


def test_missing_checkout_keeps_its_frameworks(reader):
    (checkout,) = details(reader, "gone")["checkouts"]
    assert checkout["state"] == "missing" and [t["key"] for t in checkout["frameworks"]["technologies"]] == ["tokio"]


def test_no_text_and_no_absolute_path(reader):
    text = str(frameworks(reader, "api")) + str(frameworks(reader, "broken"))
    assert "/ws" not in text and ":\\" not in text


def test_queries_do_not_touch_the_filesystem(reader, monkeypatch):
    import os

    def boom(*a, **k):
        raise AssertionError("filesystem touched by a query")

    monkeypatch.setattr(os, "walk", boom)
    monkeypatch.setattr(os, "lstat", boom)
    search(reader, technology="react")
    details(reader, "api")
