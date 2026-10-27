import json

import pytest

from vyasa.application.scanning.file_composition import default_file_types, load_file_types
from vyasa.domain.file_composition import CODE, DOCUMENTATION, OTHER, FileTypeDataError, FileTypes, extension


def write(tmp_path, data):
    path = tmp_path / "types.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def valid():
    return {"version": 2, "code_extensions": [".PY", ".go"], "documentation_extensions": [".md"]}


def test_valid_data_is_loaded_and_lower_cased(tmp_path):
    types = load_file_types(write(tmp_path, valid()))
    assert types.version == 2
    assert types.code_extensions == {".py", ".go"}
    assert types.documentation_extensions == {".md"}


def test_overlapping_lists_are_rejected_naming_the_extension(tmp_path):
    data = valid()
    data["documentation_extensions"] = [".md", ".py"]
    with pytest.raises(FileTypeDataError, match=r"\.py"):
        load_file_types(write(tmp_path, data))


@pytest.mark.parametrize("version", [None, "1", 0, True, 1.5])
def test_missing_or_bad_version_is_rejected(tmp_path, version):
    data = valid()
    data["version"] = version
    with pytest.raises(FileTypeDataError, match="version"):
        load_file_types(write(tmp_path, data))


def test_missing_version_key_is_rejected(tmp_path):
    data = valid()
    del data["version"]
    with pytest.raises(FileTypeDataError, match="version"):
        load_file_types(write(tmp_path, data))


@pytest.mark.parametrize("bad", ["py", ".", 3, None])
def test_extension_without_a_leading_dot_is_rejected(tmp_path, bad):
    data = valid()
    data["code_extensions"] = [".py", bad]
    with pytest.raises(FileTypeDataError, match="code_extensions"):
        load_file_types(write(tmp_path, data))


def test_missing_list_is_rejected(tmp_path):
    data = valid()
    del data["documentation_extensions"]
    with pytest.raises(FileTypeDataError, match="documentation_extensions"):
        load_file_types(write(tmp_path, data))


def test_unreadable_or_non_json_file_is_rejected(tmp_path):
    with pytest.raises(FileTypeDataError):
        load_file_types(tmp_path / "missing.json")
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(FileTypeDataError):
        load_file_types(bad)
    with pytest.raises(FileTypeDataError, match="object"):
        load_file_types(write(tmp_path, [1, 2]))


def test_shipped_data_loads_and_its_lists_are_disjoint():
    types = default_file_types()
    assert types.version >= 1
    assert types.code_extensions and types.documentation_extensions
    assert not types.code_extensions & types.documentation_extensions
    assert {".md", ".rst"} <= types.documentation_extensions


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("a.py", CODE),
        ("A.PY", CODE),
        ("notes.MD", DOCUMENTATION),
        ("data.csv", OTHER),
        ("Makefile", OTHER),
        (".gitignore", OTHER),
        (".md", OTHER),
        ("trailing.", OTHER),
        ("archive.tar.gz", OTHER),
    ],
)
def test_classify_by_extension_only(name, expected):
    types = FileTypes(1, frozenset({".py"}), frozenset({".md"}))
    assert types.classify(name) == expected


def test_extension_helper():
    assert extension("a.b.C") == ".c"
    assert extension(".hidden") == ""
