import builtins
import os

import pytest

from vyasa.adapters.filesystem.ignore_file import read_ignore_file
from vyasa.domain.ignore import MAX_IGNORE_BYTES, MAX_IGNORE_PATTERNS, parse_ignore


def rules(*lines):
    parsed, problems = parse_ignore("\n".join(lines))
    assert problems == ()
    return parsed


@pytest.mark.parametrize("path", ["fixtures", "a/fixtures", "a/b/fixtures"])
def test_bare_name_matches_at_any_depth(path):
    assert rules("fixtures").matches(path)


def test_bare_name_does_not_match_a_longer_name_or_a_parent_segment():
    r = rules("fixtures")
    assert not r.matches("fixtures2")
    assert not r.matches("my-fixtures")
    assert not r.matches("fixtures/inner")


@pytest.mark.parametrize(
    ("path", "expected"),
    [("data/novel/output", True), ("other/data/novel/output", False), ("data/novel", False)],
)
def test_path_from_the_root_is_anchored(path, expected):
    assert rules("data/novel/output").matches(path) is expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("data/x/cache", True),
        ("data/x/y/cache", False),
        ("data/cache", False),
        ("build-1", True),
        ("build-12", False),
        ("build-", False),
    ],
)
def test_star_stays_inside_a_segment_and_question_mark_is_one_character(path, expected):
    r = rules("data/*/cache", "build-?")
    assert r.matches(path) is expected


def test_double_star_crosses_segments():
    r = rules("data/**/cache")
    assert r.matches("data/x/y/cache")
    assert r.matches("data/x/cache")
    assert not r.matches("other/x/cache")


def test_case_is_ignored_in_pattern_and_path():
    assert rules("Fixtures").matches("fixtures")
    assert rules("fixtures").matches("A/FIXTURES")
    assert rules("Data/Novel").matches("data/NOVEL")


def test_comments_blank_lines_and_slashes_are_normalized():
    parsed, problems = parse_ignore("# comment\n\n  \n/data/\ndocs\\old\n./cache\n  spaced  \n")
    assert problems == ()
    assert parsed.patterns == ("/data", "/docs/old", "/cache", "spaced")


def test_a_leading_slash_anchors_a_single_name_at_the_root():
    r = rules("/data")
    assert r.matches("data")
    assert not r.matches("sub/data")


def test_special_characters_are_literal():
    r = rules("a.b", "x+y", "[abc]")
    assert r.matches("a.b") and not r.matches("axb")
    assert r.matches("x+y")
    assert r.matches("[abc]") and not r.matches("a")


def test_double_star_alone_matches_everything():
    assert rules("**").matches("any/path/at/all")


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ("!keep", "negation"),
        ("../outside", "'..'"),
        ("/etc/x/../y", "'..'"),
        ("a/../b", "'..'"),
        ("C:/Windows", "drive"),
        ("d:\\data", "drive"),
        ("/", "empty"),
        (".", "empty"),
    ],
)
def test_invalid_lines_are_reported_with_their_number_and_skipped(line, message):
    parsed, problems = parse_ignore(f"ok\n{line}\nalso-ok\n")
    assert len(problems) == 1
    assert problems[0].startswith("line 2:") and message in problems[0]
    assert parsed.patterns == ("ok", "also-ok")


def test_all_invalid_lines_are_reported_and_the_valid_one_applies():
    parsed, problems = parse_ignore("!keep\n/etc/x/../y\nC:/Windows\n../outside\nok\n")
    assert len(problems) == 4
    assert [p.split(":")[0] for p in problems] == ["line 1", "line 2", "line 3", "line 4"]
    assert parsed.matches("ok") and not parsed.matches("keep")


def test_too_many_patterns_keep_the_first_thousand_and_report_the_rest():
    text = "\n".join(f"dir{i}" for i in range(MAX_IGNORE_PATTERNS + 5))
    parsed, problems = parse_ignore(text)
    assert len(parsed.patterns) == MAX_IGNORE_PATTERNS
    assert parsed.matches("dir0") and not parsed.matches(f"dir{MAX_IGNORE_PATTERNS}")
    assert len(problems) == 1 and "too many" in problems[0]


def test_digest_depends_on_the_patterns_only():
    assert rules("a", "b").digest == rules("a", "b").digest
    assert rules("a", "b").digest != rules("a", "c").digest
    assert parse_ignore("# note\na\n\nb\n")[0].digest == rules("a", "b").digest


def test_empty_text_gives_no_patterns_and_matches_nothing():
    parsed, problems = parse_ignore("")
    assert parsed.patterns == () and problems == ()
    assert not parsed.matches("anything")


# -- reading ----------------------------------------------------------------------------------


def test_no_file_gives_no_rules_and_no_problem(tmp_path):
    assert read_ignore_file(os.fspath(tmp_path)) == (None, ())


def test_file_is_read_with_or_without_a_byte_order_mark(tmp_path):
    (tmp_path / ".vyasaignore").write_bytes(b"\xef\xbb\xbfdata\n")
    parsed, problems = read_ignore_file(os.fspath(tmp_path))
    assert problems == () and parsed.patterns == ("data",)


def test_undecodable_bytes_do_not_break_reading(tmp_path):
    (tmp_path / ".vyasaignore").write_bytes(b"ok\n\xff\xfe\n")
    parsed, _problems = read_ignore_file(os.fspath(tmp_path))
    assert parsed is not None and "ok" in parsed.patterns


def test_oversized_file_is_refused_as_a_whole(tmp_path):
    (tmp_path / ".vyasaignore").write_text("a\n" * (MAX_IGNORE_BYTES // 2 + 10), encoding="utf-8")
    parsed, problems = read_ignore_file(os.fspath(tmp_path))
    assert parsed is None
    assert len(problems) == 1 and "larger than 64 KiB" in problems[0]


def test_a_file_of_exactly_the_limit_is_accepted(tmp_path):
    (tmp_path / ".vyasaignore").write_bytes(b"a" * (MAX_IGNORE_BYTES - 1) + b"\n")
    assert (tmp_path / ".vyasaignore").stat().st_size == MAX_IGNORE_BYTES
    parsed, problems = read_ignore_file(os.fspath(tmp_path))
    assert parsed is not None and problems == ()


def test_at_most_the_limit_plus_one_byte_is_read(tmp_path, monkeypatch):
    (tmp_path / ".vyasaignore").write_text("a\n" * (MAX_IGNORE_BYTES), encoding="utf-8")
    sizes = []
    real = builtins.open

    class Watching:
        def __init__(self, handle):
            self.handle = handle

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            self.handle.close()

        def read(self, size=-1):
            sizes.append(size)
            return self.handle.read(size)

    def watching(file, *args, **kwargs):
        handle = real(file, *args, **kwargs)
        return Watching(handle) if os.path.basename(os.fspath(file)) == ".vyasaignore" else handle

    monkeypatch.setattr(builtins, "open", watching)
    read_ignore_file(os.fspath(tmp_path))
    assert sizes == [MAX_IGNORE_BYTES + 1]


def test_unreadable_file_is_reported(tmp_path, monkeypatch):
    (tmp_path / ".vyasaignore").write_text("a\n", encoding="utf-8")
    real = builtins.open

    def guarded(file, *args, **kwargs):
        if os.path.basename(os.fspath(file)) == ".vyasaignore":
            raise PermissionError(13, "denied", os.fspath(file))
        return real(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", guarded)
    parsed, problems = read_ignore_file(os.fspath(tmp_path))
    assert parsed is None and "cannot be read" in problems[0]


def test_a_linked_ignore_file_is_refused(tmp_path):
    target = tmp_path / "elsewhere.txt"
    target.write_text("secret-name\n", encoding="utf-8")
    repo = tmp_path / "repo"
    repo.mkdir()
    try:
        os.symlink(target, repo / ".vyasaignore")
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"this platform or account cannot create file symlinks: {error}")
    parsed, problems = read_ignore_file(os.fspath(repo))
    assert parsed is None and "link" in problems[0]
