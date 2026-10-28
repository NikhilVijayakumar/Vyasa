import json
from dataclasses import replace

import pytest
from test_frameworks_query import JS, PY, framed, fw, rows
from test_local_index import db, make_run, store  # noqa: F401

from vyasa.application.scanning.frameworks import default_registry, detect_frameworks
from vyasa.domain.manifests import MAX_NAME, parse_manifest

REGISTRY = default_registry()


def declared(name, text):
    return parse_manifest(name, text).declared_name


# --- the name each ecosystem declares ---

def test_python_project_name_is_normalized():
    assert declared("pyproject.toml", '[project]\nname = "Billing_API"\n') == "billing-api"


def test_poetry_name_is_read_and_project_name_wins():
    assert declared("pyproject.toml", '[tool.poetry]\nname = "My.Tool"\n') == "my-tool"
    both = '[project]\nname = "first"\n[tool.poetry]\nname = "second"\n'
    assert declared("pyproject.toml", both) == "first"


def test_package_json_name():
    assert declared("package.json", json.dumps({"name": "@acme/ui"})) == "@acme/ui"


def test_cargo_package_name():
    assert declared("Cargo.toml", '[package]\nname = "ledger-core"\nversion = "1"\n') == "ledger-core"


def test_go_module_path():
    assert declared("go.mod", "module example.com/acme/tool\n\ngo 1.22\n") == "example.com/acme/tool"


@pytest.mark.parametrize("name,text", [
    ("pyproject.toml", '[tool.black]\nline-length = 100\n'),
    ("package.json", json.dumps({"dependencies": {"react": "1"}})),
    ("Cargo.toml", '[workspace]\nmembers = ["a"]\n'),
    ("go.mod", "go 1.22\n"),
    ("requirements.txt", "requests\n"),
])
def test_no_name_declared(name, text):
    assert declared(name, text) is None


@pytest.mark.parametrize("name,text", [
    ("package.json", json.dumps({"name": 5})),
    ("pyproject.toml", "[project]\nname = 7\n"),
    ("Cargo.toml", "[package]\nname = []\n"),
    ("package.json", json.dumps({"name": "x" * (MAX_NAME + 1)})),
    ("package.json", json.dumps({"name": ""})),
])
def test_name_that_is_not_text_or_too_long_is_dropped(name, text):
    assert declared(name, text) is None


def test_name_does_not_change_the_dependencies():
    plain = parse_manifest("package.json", json.dumps({"dependencies": {"react": "^18"}}))
    named = parse_manifest("package.json", json.dumps({"name": "app", "dependencies": {"react": "^18"}}))
    assert (plain.dependencies, plain.skipped, plain.workspace) == (named.dependencies, named.skipped, named.workspace)


# --- from files to the detector ---

def test_detector_keeps_the_name_of_parsed_manifests_only(tmp_path):
    (tmp_path / "package.json").write_text(json.dumps({"name": "app"}))
    (tmp_path / "Cargo.toml").write_text("[package\nname =")
    report = detect_frameworks(tmp_path, ["package.json", "Cargo.toml"], None, REGISTRY)
    names = {m.path: (m.status, m.declared_name) for m in report.manifests}
    assert names == {"package.json": ("parsed", "app"), "Cargo.toml": ("malformed", None)}


# --- stored with the observation ---

def test_name_is_stored_on_the_manifest_row(db):
    store(db, make_run([framed("a", fw(replace(JS, declared_name="app"), PY))]))
    got = {r[1]: r[-1] for r in rows(db, "checkout_manifests", "a")}
    assert got == {"package.json": "app", "pyproject.toml": None}
