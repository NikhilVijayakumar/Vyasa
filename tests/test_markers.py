import json

import pytest

from vyasa.application.scanning.markers import default_marker_rules, load_marker_rules
from vyasa.domain.markers import MARKERS, MAX_PATHS, MarkerRulesError, markers_of

RULES = default_marker_rules()


def detect(files=(), directories=(), stopped_by=None):
    report = markers_of(files, directories, RULES, stopped_by)
    return {f.marker: f for f in report.found}


def paths(found):
    return [p for p, _ in found.paths]


# --- rules data ---

def write(tmp_path, data):
    path = tmp_path / "markers.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def valid():
    return {
        "version": 1,
        "readme": {"names": ["README.md"]},
        "docs": {"directories": ["Docs"]},
        "agent_instructions": {"files": ["AGENTS.md"]},
        "openspec": {"directory": "openspec", "config": ["config.yaml"], "specs": "specs", "changes": "changes"},
        "tests": {"directories": ["tests"], "file_patterns": ["test_*.py"]},
    }


def test_valid_rules_carry_the_version_and_lower_case_names(tmp_path):
    rules = load_marker_rules(write(tmp_path, valid()))
    assert rules.version == 1 and rules.readme_names == {"readme.md"} and rules.docs_directories == {"docs"}
    assert rules.test_patterns == ("test_*.py",)


def test_shipped_rules_are_valid():
    assert RULES.version >= 1 and "readme.md" in RULES.readme_names


@pytest.mark.parametrize("mutate,match", [
    (lambda d: d.pop("version"), "version"),
    (lambda d: d.update(version="1"), "version"),
    (lambda d: d.update(version=True), "version"),
    (lambda d: d.pop("readme"), "readme"),
    (lambda d: d["readme"].update(names="README.md"), "readme.names"),
    (lambda d: d["readme"].update(names=[""]), "readme.names"),
    (lambda d: d["docs"].update(directories=["a/b"]), "docs.directories"),
    (lambda d: d["tests"].update(file_patterns=["x\\y"]), "tests.file_patterns"),
    (lambda d: d["openspec"].update(directory=3), "openspec.directory"),
])
def test_malformed_rules_are_rejected_naming_the_field(tmp_path, mutate, match):
    data = valid()
    mutate(data)
    with pytest.raises(MarkerRulesError, match=match):
        load_marker_rules(write(tmp_path, data))


def test_unreadable_rules_are_rejected(tmp_path):
    with pytest.raises(MarkerRulesError):
        load_marker_rules(tmp_path / "missing.json")


# --- detection ---

def test_readme_at_the_root_with_any_case():
    assert paths(detect(files=["readme.RST"])["readme"]) == ["readme.RST"]
    assert paths(detect(files=["README.md"])["readme"]) == ["README.md"]


def test_readme_below_the_root_is_not_a_root_readme():
    assert "readme" not in detect(files=["pkg/README.md"])


def test_docs_directory_at_the_root_only():
    assert paths(detect(directories=["docs"])["docs"]) == ["docs"]
    assert "docs" not in detect(directories=["pkg/docs"])


def test_name_alone_is_not_content():
    assert "readme" not in detect(files=["notes.txt"])


def test_agent_files_anywhere_with_scope():
    found = detect(files=["AGENTS.md", "packages/app/CLAUDE.md"])["agent_instructions"]
    assert found.total == 2 and found.paths == (("AGENTS.md", "root"), ("packages/app/CLAUDE.md", "packages/app"))


def test_openspec_indicators_are_separate():
    found = detect(files=[], directories=["openspec", "openspec/specs"])
    assert set(found) == {"openspec_directory", "openspec_specs"}


def test_openspec_config_and_changes():
    found = detect(files=["openspec/config.yaml"], directories=["openspec", "openspec/changes"])
    assert set(found) == {"openspec_directory", "openspec_config", "openspec_changes"}


def test_openspec_only_at_the_root():
    assert not detect(directories=["pkg/openspec", "pkg/openspec/specs"])


def test_tests_by_directory_and_name_record_both_rules():
    found = detect(files=["svc/service_test.go"], directories=["tests"])["tests"]
    assert found.total == 2 and set(found.rules) == {"test_directory", "file_pattern:*_test.go"}


def test_nested_test_directory():
    assert paths(detect(directories=["packages/app/tests"])["tests"]) == ["packages/app/tests"]


@pytest.mark.parametrize("name", ["test_a.py", "a_test.py", "a_test.go", "a.test.ts", "a.test.jsx", "a.spec.js", "ServiceTest.java"])
def test_test_file_names(name):
    assert "tests" in detect(files=[name])


@pytest.mark.parametrize("name", ["latest.java", "contest.py", "a.testing.ts", "tests.txt"])
def test_not_test_names(name):
    assert "tests" not in detect(files=[name])


def test_cap_keeps_twenty_and_reports_the_total():
    found = detect(files=[f"t/test_{i:02d}.py" for i in range(30)])["tests"]
    assert found.total == 30 and len(found.paths) == MAX_PATHS == 20
    assert paths(found) == sorted(paths(found))


def test_order_of_input_does_not_matter():
    files = ["b/test_b.py", "a/test_a.py", "AGENTS.md", "README.md"]
    one = markers_of(files, ["docs"], RULES)
    two = markers_of(list(reversed(files)), ["docs"], RULES)
    assert one == two


def test_paths_are_relative_and_clean():
    for found in detect(files=["a/test_x.py", "AGENTS.md"], directories=["tests", "docs"]).values():
        for p, _ in found.paths:
            assert not p.startswith("/") and ":" not in p and ".." not in p.split("/")


def test_report_carries_version_and_bound():
    report = markers_of([], [], RULES, "entries")
    assert (report.rules_version, report.stopped_by, report.complete) == (RULES.version, "entries", False)
    assert markers_of([], [], RULES).complete


def test_marker_names_are_the_eight():
    assert len(MARKERS) == 8 and set(MARKERS) >= {"readme", "docs", "tests", "agent_instructions", "openspec_config"}
