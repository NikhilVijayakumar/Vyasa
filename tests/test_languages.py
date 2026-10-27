import json

import pytest

from vyasa.application.scanning.file_composition import compose, default_file_types, load_file_types
from vyasa.application.scanning.languages import detect_languages
from vyasa.domain.file_composition import FileTypeDataError, WalkLimits


def write(tmp_path, data):
    path = tmp_path / "types.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def valid():
    return {
        "version": 2,
        "code_extensions": [".py", ".h"],
        "documentation_extensions": [".md"],
        "languages": {".py": "Python", ".h": "C/C++ header"},
        "manifests": {"Cargo.toml": "Rust"},
    }


def tree(root, *names):
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    return root


def detect(root, **kw):
    return detect_languages(root, default_file_types(), **kw)


# --- validated language data ---

def test_valid_data_carries_both_maps_lower_cased(tmp_path):
    types = load_file_types(write(tmp_path, valid()))
    assert types.languages == {".py": "Python", ".h": "C/C++ header"}
    assert types.manifests == {"cargo.toml": "Rust"}


def test_version_1_data_has_no_languages(tmp_path):
    data = {"version": 1, "code_extensions": [".py"], "documentation_extensions": []}
    types = load_file_types(write(tmp_path, data))
    assert types.languages == {} and types.manifests == {}


def test_languages_disagreeing_with_code_extensions_are_rejected(tmp_path):
    data = valid()
    data["languages"][".rs"] = "Rust"
    with pytest.raises(FileTypeDataError, match=r"\.rs"):
        load_file_types(write(tmp_path, data))


@pytest.mark.parametrize("label", ["", 3, None])
def test_bad_label_is_rejected(tmp_path, label):
    data = valid()
    data["manifests"]["Cargo.toml"] = label
    with pytest.raises(FileTypeDataError, match="manifests"):
        load_file_types(write(tmp_path, data))


def test_shipped_data_is_valid_and_sums_to_code_extensions():
    types = default_file_types()
    assert set(types.languages) == set(types.code_extensions)


# --- files detected ---

def test_extensions_give_counts(tmp_path):
    report = detect(tree(tmp_path, "a.py", "b.py", "c.py", "d.rs", "e.rs"))
    assert report.files_detected == (("Python", 3), ("Rust", 2))


def test_extension_case_is_ignored(tmp_path):
    assert detect(tree(tmp_path, "a.PY", "b.py")).files_detected == (("Python", 2),)


def test_shared_extension_maps_to_one_label(tmp_path):
    assert detect(tree(tmp_path, "a.h", "b.h")).files_detected == (("C/C++ header", 2),)


def test_unknown_and_extensionless_are_ignored(tmp_path):
    report = detect(tree(tmp_path, "data.xyz", "Makefile", "notes.md"))
    assert report.files_detected == () and report.declared == ()


# --- declared ---

def test_manifest_declares_without_sources(tmp_path):
    report = detect(tree(tmp_path, "Cargo.toml"))
    assert report.declared == ("Rust",) and report.files_detected == ()


def test_nested_manifest_declares_and_case_is_ignored(tmp_path):
    assert detect(tree(tmp_path, "svc/GO.MOD")).declared == ("Go",)


def test_unrecognized_manifest_declares_nothing(tmp_path):
    assert detect(tree(tmp_path, "project.manifest")).declared == ()


def test_found_both_ways_keeps_two_results(tmp_path):
    report = detect(tree(tmp_path, "pyproject.toml", "a.py", "b.py"))
    assert report.declared == ("Python",)
    assert report.files_detected == (("Python", 2),)


# --- agreement, partial, evidence ---

def mixed(tmp_path):
    return tree(tmp_path, "a.py", "b.rs", "c.h", "d.md", "e.txt", "x/f.go", "x/g.png")


def test_sum_equals_code_count(tmp_path):
    root = mixed(tmp_path)
    types = default_file_types()
    total = sum(n for _, n in detect_languages(root, types).files_detected)
    assert total == compose(root, types).code == 4


def test_sum_equals_code_count_when_capped(tmp_path):
    root = mixed(tmp_path)
    types = default_file_types()
    limits = WalkLimits(max_entries=3)
    report = detect_languages(root, types, limits)
    assert not report.complete
    assert sum(n for _, n in report.files_detected) == compose(root, types, limits).code


def test_partial_makes_absence_unknown(tmp_path):
    report = detect(mixed(tmp_path), limits=WalkLimits(max_entries=3))
    assert report.stopped_by == "entries"
    assert report.is_absent("Ruby") is None
    assert all(report.is_absent(label) is False for label, _ in report.files_detected)


def test_complete_makes_absence_true(tmp_path):
    report = detect(tree(tmp_path, "a.py"))
    assert report.complete and report.is_absent("Rust") is True
    assert report.is_absent("Python") is False


def test_evidence_is_present(tmp_path):
    report = detect(tree(tmp_path, "a.py"), exclusions=["zeta", "alpha"])
    assert report.evidence.types_version == 2
    assert report.evidence.exclusions == ("alpha", "zeta")


def test_result_is_independent_of_creation_order(tmp_path):
    names = ["a.py", "b.rs", "x/c.go", "pyproject.toml"]
    one = detect(tree(tmp_path / "one", *names))
    two = detect(tree(tmp_path / "two", *reversed(names)))
    assert one == two


def test_missing_root_raises(tmp_path):
    with pytest.raises(ValueError):
        detect(tmp_path / "nope")
