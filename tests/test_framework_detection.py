import json

import pytest

from vyasa.adapters.filesystem.manifest_reader import ManifestRead, read_manifest
from vyasa.application.scanning.checkout_scan import scan_checkout
from vyasa.application.scanning.file_composition import default_file_types
from vyasa.application.scanning.frameworks import default_registry, detect_frameworks
from vyasa.application.scanning.markers import default_marker_rules
from vyasa.domain.file_composition import WalkLimits
from vyasa.domain.frameworks import MAX_DEPENDENCIES

REGISTRY = default_registry()


def tree(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))
    return root


def detect(root, files, stopped_by=None, **kw):
    return detect_frameworks(root, files, stopped_by, REGISTRY, **kw)


def by_path(report):
    return {m.path: m for m in report.manifests}


PACKAGE = json.dumps({"dependencies": {"react": "^18"}, "devDependencies": {"jest": "^29", "left-pad": "1"}})


def test_root_manifests_are_read_and_mapped(tmp_path):
    root = tree(tmp_path, {"package.json": PACKAGE, "pyproject.toml": '[project]\ndependencies = ["fastapi>=0.1"]\n'})
    report = detect(root, ["package.json", "pyproject.toml", "README.md", "src/a.py"])
    assert sorted(by_path(report)) == ["package.json", "pyproject.toml"]
    assert [(t.key, t.scopes) for t in report.technologies] == [("fastapi", ("runtime",)), ("jest", ("dev",)), ("react", ("runtime",))]
    assert report.registry_version == REGISTRY.version


def test_unknown_dependency_is_kept_without_a_technology(tmp_path):
    report = detect(tree(tmp_path, {"package.json": PACKAGE}), ["package.json"])
    assert "left-pad" in {d.name for d in by_path(report)["package.json"].dependencies}
    assert "left-pad" not in {t.key for t in report.technologies}


def test_file_names_match_case_insensitively_and_by_pattern(tmp_path):
    root = tree(tmp_path, {"Cargo.TOML": '[dependencies]\ntokio = "1"\n', "requirements-dev.txt": "pytest\n"})
    report = detect(root, ["Cargo.TOML", "requirements-dev.txt"])
    assert sorted(by_path(report)) == ["Cargo.TOML", "requirements-dev.txt"]
    assert {t.key for t in report.technologies} == {"tokio", "pytest"}


def test_setup_py_and_unsupported_files_are_never_opened(tmp_path):
    opened = []

    def reader(root, name, limit):
        opened.append(name)
        return ManifestRead("{}", "read")

    detect(tmp_path, ["setup.py", "Dockerfile", "docker-compose.yml", "tsconfig.json", "package-lock.json", "package.json"], reader=reader)
    assert opened == ["package.json"]


def test_nested_manifests_are_counted_and_not_read(tmp_path):
    opened = []

    def reader(root, name, limit):
        opened.append(name)
        return ManifestRead("{}", "read")

    report = detect(tmp_path, ["a/package.json", "b/package.json", "c/d/package.json", "svc/go.mod", "x/requirements-dev.txt"], reader=reader)
    assert opened == [] and report.manifests == () and report.technologies == ()
    assert dict(report.nested) == {"javascript": 3, "go": 1, "python": 1}


def test_workspace_flag_without_expanding_members(tmp_path):
    root = tree(tmp_path, {"package.json": '{"workspaces": ["packages/*"], "dependencies": {"react": "1"}}', "packages/a/package.json": '{"dependencies": {"vue": "1"}}'})
    report = detect(root, ["package.json", "packages/a/package.json"])
    assert by_path(report)["package.json"].workspace is True
    assert {t.key for t in report.technologies} == {"react"}
    assert dict(report.nested) == {"javascript": 1}


def test_status_and_reason_per_manifest(tmp_path):
    root = tree(tmp_path, {
        "package.json": b"\xff\xfe",
        "Cargo.toml": "= = =",
        "go.mod": "module x\nrequire github.com/gin-gonic/gin v1.9.1\n",
        "pyproject.toml": "x" * 100,
    })
    report = detect(root, ["package.json", "Cargo.toml", "go.mod", "pyproject.toml"], limit=40)
    assert {p: (m.status, m.reason) for p, m in by_path(report).items()} == {
        "package.json": ("malformed", "encoding"), "Cargo.toml": ("malformed", "syntax"),
        "go.mod": ("too_large", None), "pyproject.toml": ("too_large", None),
    }


def test_one_bad_manifest_does_not_hide_another(tmp_path):
    root = tree(tmp_path, {"package.json": "{not json", "Cargo.toml": '[dependencies]\ntokio = "1"\n'})
    report = detect(root, ["package.json", "Cargo.toml"])
    results = {p: (m.status, m.reason) for p, m in by_path(report).items()}
    assert results == {"package.json": ("malformed", "syntax"), "Cargo.toml": ("parsed", None)}
    assert [t.key for t in report.technologies] == ["tokio"]


def test_bad_manifests_have_no_dependencies_and_no_text(tmp_path):
    root = tree(tmp_path, {"package.json": '{"dependencies": [1], "secret": "hunter2"}'})
    (manifest,) = detect(root, ["package.json"]).manifests
    assert (manifest.status, manifest.reason, manifest.dependencies, manifest.total_dependencies) == ("malformed", "structure", (), 0)
    assert "hunter2" not in repr(manifest)


def test_unexpected_exceptions_are_isolated(tmp_path):
    def reader(root, name, limit):
        if name == "package.json":
            raise RuntimeError("secret detail")
        return read_manifest(root, name, limit)

    root = tree(tmp_path, {"package.json": PACKAGE, "Cargo.toml": '[dependencies]\ntokio = "1"\n'})
    report = detect(root, ["package.json", "Cargo.toml"], reader=reader)
    results = {p: (m.status, m.reason) for p, m in by_path(report).items()}
    assert results == {"package.json": ("unreadable", "io"), "Cargo.toml": ("parsed", None)}
    assert "secret" not in repr(report)


def test_dependency_cap_keeps_the_total_and_all_technologies(tmp_path):
    deps = {f"pkg-{i:03d}": "1" for i in range(300)} | {"zzz-react-last": "1", "react": "1"}
    root = tree(tmp_path, {"package.json": json.dumps({"dependencies": deps})})
    (manifest,) = detect(root, ["package.json"]).manifests
    assert len(manifest.dependencies) == MAX_DEPENDENCIES == 200 and manifest.total_dependencies == 302
    assert [d.name for d in manifest.dependencies] == sorted(d.name for d in manifest.dependencies)
    assert "react" in {t.key for t in detect(root, ["package.json"]).technologies}


def test_order_is_deterministic(tmp_path):
    root = tree(tmp_path, {"package.json": PACKAGE, "Cargo.toml": '[dependencies]\ntokio = "1"\n', "go.mod": "module x\n"})
    one = detect(root, ["package.json", "Cargo.toml", "go.mod"])
    two = detect(root, ["go.mod", "Cargo.toml", "package.json"])
    assert one == two


def test_stopped_by_is_carried(tmp_path):
    assert detect(tmp_path, [], "entries").stopped_by == "entries"
    assert detect(tmp_path, []).complete


def test_no_report_without_a_registry(tmp_path):
    scan = scan_checkout(tree(tmp_path, {"package.json": PACKAGE}), default_file_types())
    assert scan.frameworks is None


def test_scan_checkout_detects_frameworks_from_one_walk(tmp_path):
    root = tree(tmp_path, {"package.json": PACKAGE, "src/a.js": "", "README.md": ""})
    scan = scan_checkout(root, default_file_types(), rules=default_marker_rules(), frameworks=REGISTRY)
    assert {t.key for t in scan.frameworks.technologies} == {"react", "jest"}
    assert scan.frameworks.stopped_by == scan.composition.stopped_by is None
    assert sum(n for _, n in scan.languages.files_detected) == scan.composition.code == 1


def test_scan_checkout_partial_walk_is_carried_to_frameworks(tmp_path):
    root = tree(tmp_path, {f"f{i}.txt": "" for i in range(10)} | {"package.json": PACKAGE})
    scan = scan_checkout(root, default_file_types(), WalkLimits(max_entries=3), frameworks=REGISTRY)
    assert scan.frameworks.stopped_by == "entries"


def test_scan_checkout_ignores_links_to_manifests(tmp_path):
    import os

    target = tree(tmp_path / "t", {"real.json": PACKAGE})
    root = tmp_path / "root"
    root.mkdir()
    try:
        os.symlink(target / "real.json", root / "package.json")
    except (OSError, NotImplementedError):
        pytest.skip("cannot create a file symlink on this platform")
    scan = scan_checkout(root, default_file_types(), frameworks=REGISTRY)
    (manifest,) = scan.frameworks.manifests
    assert (manifest.status, manifest.reason) == ("unreadable", "link") and scan.frameworks.technologies == ()
