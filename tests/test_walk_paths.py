import os

import pytest

from vyasa.adapters.filesystem.checkout_walk import walk_checkout
from vyasa.domain.file_composition import DEFAULT_EXCLUSIONS, WalkLimits
from vyasa.domain.ignore import parse_ignore


def tree(root, *names):
    for name in names:
        path = root / name
        if name.endswith("/"):
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")
    return root


def walk(root, **kw):
    return walk_checkout(root, kw.pop("limits", WalkLimits()), kw.pop("exclusions", DEFAULT_EXCLUSIONS), **kw)


def test_relative_posix_paths_and_directories(tmp_path):
    root = tree(tmp_path, "b.txt", "a/x.py", "a/sub/y.py", "z/", "README.md")
    result = walk(root)
    assert sorted(result.files) == ["README.md", "a/sub/y.py", "a/x.py", "b.txt"]
    assert sorted(result.directories) == ["a", "a/sub", "z"]
    assert all("\\" not in p and not os.path.isabs(p) for p in (*result.files, *result.directories))


def test_order_is_stable(tmp_path):
    one = walk(tree(tmp_path / "one", "b/y.py", "a/x.py", "c.txt"))
    two = walk(tree(tmp_path / "two", "c.txt", "a/x.py", "b/y.py"))
    assert (one.files, one.directories) == (two.files, two.directories)


def test_names_are_unchanged(tmp_path):
    result = walk(tree(tmp_path, "a/x.py", "b.txt"))
    assert sorted(result.names) == ["b.txt", "x.py"]
    assert [p.rpartition("/")[2] for p in result.files] == list(result.names)


def test_excluded_directories_are_not_reported(tmp_path):
    result = walk(tree(tmp_path, "node_modules/p/test_a.py", "src/a.py"))
    assert result.directories == ("src",) and result.files == ("src/a.py",)


def test_ignored_directories_are_not_reported(tmp_path):
    ignore, _problems = parse_ignore("vendor/\n")
    result = walk(tree(tmp_path, "vendor/x.py", "src/a.py"), ignore=ignore)
    assert result.directories == ("src",)


def test_directory_at_the_depth_limit_is_reported_but_not_entered(tmp_path):
    result = walk(tree(tmp_path, "a/b/c/x.py"), limits=WalkLimits(max_depth=1))
    assert result.directories == ("a", "a/b")
    assert result.stopped_by == "depth" and result.files == ()


def test_symlinked_directory_is_not_reported_or_entered(tmp_path):
    outside = tree(tmp_path / "outside", "secret/test_x.py")
    root = tmp_path / "root"
    root.mkdir()
    try:
        os.symlink(outside, root / "link", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("cannot create a directory symlink on this platform")
    result = walk(root)
    assert result.files == () and result.directories == ()


def test_entry_cap_stops_and_lists_only_what_was_counted(tmp_path):
    result = walk(tree(tmp_path, *[f"f{i}.txt" for i in range(5)]), limits=WalkLimits(max_entries=3))
    assert result.stopped_by == "entries" and len(result.files) == 3 == len(result.names)
