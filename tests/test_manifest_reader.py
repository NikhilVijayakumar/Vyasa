import os

import pytest

from vyasa.adapters.filesystem.manifest_reader import read_manifest


def write(root, name, data):
    path = root / name
    path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def test_regular_root_file_is_read(tmp_path):
    write(tmp_path, "package.json", '{"a": 1}')
    read = read_manifest(tmp_path, "package.json", 1024)
    assert (read.status, read.reason, read.text) == ("read", None, '{"a": 1}')


def test_missing_file_is_unreadable(tmp_path):
    read = read_manifest(tmp_path, "package.json", 1024)
    assert (read.status, read.reason, read.text) == ("unreadable", "io", None)


def test_directory_named_like_a_manifest_is_not_a_file(tmp_path):
    (tmp_path / "package.json").mkdir()
    read = read_manifest(tmp_path, "package.json", 1024)
    assert (read.status, read.reason, read.text) == ("unreadable", "not_file", None)


def test_symbolic_link_is_never_read(tmp_path):
    target = write(tmp_path, "real.json", '{"dependencies": {"react": "1"}}')
    try:
        os.symlink(target, tmp_path / "package.json")
    except (OSError, NotImplementedError):
        pytest.skip("cannot create a file symlink on this platform")
    read = read_manifest(tmp_path, "package.json", 1024)
    assert (read.status, read.reason, read.text) == ("unreadable", "link", None)


def test_link_to_a_file_outside_the_root_is_never_read(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = write(outside, "secret.txt", "TOP SECRET")
    root = tmp_path / "root"
    root.mkdir()
    try:
        os.symlink(secret, root / "go.mod")
    except (OSError, NotImplementedError):
        pytest.skip("cannot create a file symlink on this platform")
    read = read_manifest(root, "go.mod", 1024)
    assert read.text is None and "SECRET" not in repr(read)


def test_file_over_the_limit_is_too_large_and_not_read(tmp_path):
    write(tmp_path, "package.json", b"x" * 1025)
    read = read_manifest(tmp_path, "package.json", 1024)
    assert (read.status, read.reason, read.text) == ("too_large", None, None)


def test_file_exactly_at_the_limit_is_read(tmp_path):
    write(tmp_path, "package.json", b"x" * 1024)
    assert read_manifest(tmp_path, "package.json", 1024).status == "read"


def test_default_limit_is_one_mebibyte(tmp_path):
    write(tmp_path, "package.json", b"x" * (1024 * 1024 + 1))
    assert read_manifest(tmp_path, "package.json").status == "too_large"


def test_bom_is_accepted(tmp_path):
    write(tmp_path, "Cargo.toml", b"\xef\xbb\xbf[package]\n")
    assert read_manifest(tmp_path, "Cargo.toml", 1024).text == "[package]\n"


@pytest.mark.parametrize("data", [b"\xff\xfe\x00\x00", b"[package]\n\xc3\x28", bytes(range(256))])
def test_invalid_utf8_is_malformed_with_reason_encoding(tmp_path, data):
    write(tmp_path, "Cargo.toml", data)
    read = read_manifest(tmp_path, "Cargo.toml", 1024)
    assert (read.status, read.reason, read.text) == ("malformed", "encoding", None)


def test_name_with_a_separator_is_refused(tmp_path):
    (tmp_path / "sub").mkdir()
    write(tmp_path / "sub", "package.json", "{}")
    read = read_manifest(tmp_path, "sub/package.json", 1024)
    assert (read.status, read.reason, read.text) == ("unreadable", "not_file", None)


def test_file_swapped_for_another_between_check_and_open_is_refused(tmp_path, monkeypatch):
    write(tmp_path, "package.json", "{}")
    real = os.fstat

    class Other:
        def __init__(self, st):
            self.st_mode, self.st_ino, self.st_dev, self.st_size = st.st_mode, st.st_ino + 1, st.st_dev, st.st_size

    monkeypatch.setattr(os, "fstat", lambda fd: Other(real(fd)))
    read = read_manifest(tmp_path, "package.json", 1024)
    assert (read.status, read.text) == ("unreadable", None)
