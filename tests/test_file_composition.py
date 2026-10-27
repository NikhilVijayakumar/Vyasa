import builtins
import os

import pytest

from vyasa.application.scanning.file_composition import compose
from vyasa.domain.file_composition import DEFAULT_EXCLUSIONS, FileComposition, FileTypes, WalkLimits

TYPES = FileTypes(version=3, code_extensions=frozenset({".py", ".go"}), documentation_extensions=frozenset({".md"}))


def make(root, *relative_files):
    for relative in relative_files:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x", encoding="utf-8")
    return root


def run(root, **kwargs):
    return compose(root, TYPES, **kwargs)


def ticking_clock(step):
    state = {"now": 0.0}

    def clock():
        state["now"] += step
        return state["now"]

    return clock


# -- counts ------------------------------------------------------------------


def test_mixed_checkout_counts_agree(tmp_path):
    make(tmp_path, "a.py", "b.py", "src/c.go", "README.md", "docs/d.md", "x.csv", "y.png", "z.bin", "Makefile")
    result = run(tmp_path)
    assert (result.code, result.documentation, result.other, result.total) == (3, 2, 4, 9)
    assert result.total == result.code + result.documentation + result.other
    assert result.complete and result.stopped_by is None


def test_extension_case_is_ignored(tmp_path):
    make(tmp_path, "a.MD", "b.md", "C.PY")
    result = run(tmp_path)
    assert (result.documentation, result.code) == (2, 1)


def test_unknown_types_are_other_never_code(tmp_path):
    make(tmp_path, "a.zzz", "b.dat", "noext", ".dotfile")
    result = run(tmp_path)
    assert (result.code, result.documentation, result.other) == (0, 0, 4)


def test_content_is_never_read(tmp_path, monkeypatch):
    path = tmp_path / "notes.md"
    path.write_text("def f():\n    return 1\n", encoding="utf-8")

    def refuse(*_args, **_kwargs):
        raise AssertionError("a file was opened")

    monkeypatch.setattr(builtins, "open", refuse)
    result = run(tmp_path)
    assert (result.documentation, result.code) == (1, 0)


def test_empty_checkout_is_complete_and_not_documentation_only(tmp_path):
    result = run(tmp_path)
    assert (result.code, result.documentation, result.other, result.total) == (0, 0, 0, 0)
    assert result.complete and result.documentation_only is False


def test_missing_root_raises_value_error(tmp_path):
    with pytest.raises(ValueError):
        run(tmp_path / "missing")
    make(tmp_path, "a.py")
    with pytest.raises(ValueError):
        run(tmp_path / "a.py")


# -- documentation-only indicator ----------------------------------------------


def test_documentation_only_true(tmp_path):
    make(tmp_path, "a.md", "b.md", "config.yml")
    assert run(tmp_path).documentation_only is True


def test_documentation_and_code_is_false(tmp_path):
    make(tmp_path, "a.md", "b.py")
    assert run(tmp_path).documentation_only is False


def test_no_documentation_is_false(tmp_path):
    make(tmp_path, "data.csv")
    assert run(tmp_path).documentation_only is False


def test_partial_count_makes_the_indicator_unknown(tmp_path):
    make(tmp_path, "a.md", "b.md", "c.md")
    result = run(tmp_path, limits=WalkLimits(max_entries=2))
    assert not result.complete
    assert result.documentation_only is None


# -- bounds ------------------------------------------------------------------


def test_entry_cap_marks_partial_and_gives_lower_bounds(tmp_path):
    make(tmp_path, *[f"f{i}.py" for i in range(10)])
    result = run(tmp_path, limits=WalkLimits(max_entries=4))
    assert result.stopped_by == "entries"
    assert result.total == 4


def test_entries_count_directories_as_well_as_files(tmp_path):
    for i in range(5):
        (tmp_path / f"d{i}").mkdir()
    result = run(tmp_path, limits=WalkLimits(max_entries=3))
    assert result.stopped_by == "entries"


def test_depth_limit_marks_partial(tmp_path):
    make(tmp_path, "top.py", "a/one.py", "a/b/two.py", "a/b/c/three.py")
    result = run(tmp_path, limits=WalkLimits(max_depth=2))
    assert result.stopped_by == "depth"
    assert result.code == 3


def test_files_at_exactly_the_depth_limit_are_counted_and_complete(tmp_path):
    make(tmp_path, "top.py", "a/one.py", "a/b/two.py")
    result = run(tmp_path, limits=WalkLimits(max_depth=2))
    assert result.complete
    assert result.code == 3


def test_time_limit_marks_partial(tmp_path):
    make(tmp_path, "a.py", "sub/b.py", "sub/deeper/c.py")
    result = run(tmp_path, limits=WalkLimits(max_seconds=1.0), clock=ticking_clock(10.0))
    assert result.stopped_by == "time"
    assert result.documentation_only is None


def test_within_all_limits_is_complete(tmp_path):
    make(tmp_path, "a.py", "sub/b.md")
    result = run(tmp_path)
    assert result.complete and result.stopped_by is None


def test_unreadable_directory_marks_partial_but_other_files_count(tmp_path, monkeypatch):
    make(tmp_path, "ok.py", "blocked/hidden.py", "fine/also.md")
    blocked = os.fspath(tmp_path / "blocked")
    real = os.scandir

    def scandir(path="."):
        if os.fspath(path) == blocked:
            raise PermissionError(13, "denied", blocked)
        return real(path)

    monkeypatch.setattr(os, "scandir", scandir)
    result = run(tmp_path)
    assert result.stopped_by == "unreadable"
    assert (result.code, result.documentation) == (1, 1)


def test_first_cause_is_reported(tmp_path, monkeypatch):
    make(tmp_path, "a/x.py", "b/y.py", "c/z.py", "c/w.py")
    blocked = os.fspath(tmp_path / "a")
    real = os.scandir

    def scandir(path="."):
        if os.fspath(path) == blocked:
            raise PermissionError(13, "denied", blocked)
        return real(path)

    monkeypatch.setattr(os, "scandir", scandir)
    result = run(tmp_path, limits=WalkLimits(max_entries=3))
    assert result.stopped_by == "unreadable"


def test_partial_results_are_repeatable(tmp_path):
    make(tmp_path, *[f"d{i}/f{j}.py" for i in range(5) for j in range(5)])
    limits = WalkLimits(max_entries=9)
    first, second = run(tmp_path, limits=limits), run(tmp_path, limits=limits)
    assert first == second
    assert first.stopped_by == "entries"


# -- links and exclusions --------------------------------------------------------


def symlink_dir(link, target):
    try:
        os.symlink(target, link, target_is_directory=True)
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"this platform or account cannot create directory symlinks: {error}")


def test_directory_symlink_is_not_followed(tmp_path):
    outside = make(tmp_path / "outside", "secret.py", "more.md")
    checkout = make(tmp_path / "checkout", "own.py")
    symlink_dir(checkout / "link", outside)
    result = run(checkout)
    assert (result.code, result.documentation) == (1, 0)
    assert result.complete


def test_symlinked_file_is_counted_as_itself(tmp_path):
    outside = make(tmp_path / "outside", "target.dat")
    checkout = make(tmp_path / "checkout", "own.py")
    try:
        os.symlink(outside / "target.dat", checkout / "linked.md")
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"this platform or account cannot create file symlinks: {error}")
    result = run(checkout)
    assert (result.code, result.documentation, result.other) == (1, 1, 0)


def test_junction_is_not_followed(tmp_path):
    winapi = pytest.importorskip("_winapi", reason="directory junctions exist only on Windows")
    outside = make(tmp_path / "outside", "secret.py")
    checkout = make(tmp_path / "checkout", "own.py")
    winapi.CreateJunction(os.fspath(outside), os.fspath(checkout / "junction"))
    result = run(checkout)
    assert result.code == 1


def test_excluded_directory_is_not_counted_and_is_recorded(tmp_path):
    make(tmp_path, "a.py", "node_modules/dep/x.py", "node_modules/y.md")
    result = run(tmp_path)
    assert result.code == 1 and result.documentation == 0
    assert "node_modules" in result.evidence.exclusions


def test_exclusion_names_ignore_case(tmp_path):
    make(tmp_path, "a.py", "Node_Modules/x.py")
    result = run(tmp_path)
    assert result.code == 1


def test_custom_exclusions_replace_the_defaults(tmp_path):
    make(tmp_path, "a.py", "node_modules/x.py", "skipme/y.py")
    result = run(tmp_path, exclusions={"skipme"})
    assert result.code == 2
    assert result.evidence.exclusions == ("skipme",)


def test_checkout_named_like_an_exclusion_is_still_counted(tmp_path):
    root = make(tmp_path / "build", "a.py", "b.md")
    result = run(root)
    assert (result.code, result.documentation) == (1, 1)


# -- evidence and determinism ------------------------------------------------------------


def test_evidence_carries_version_exclusions_limits_and_marker(tmp_path):
    make(tmp_path, "a.py")
    limits = WalkLimits(max_depth=5, max_entries=100, max_seconds=9.0)
    result = run(tmp_path, limits=limits)
    assert result.evidence.types_version == 3
    assert result.evidence.exclusions == tuple(sorted(DEFAULT_EXCLUSIONS))
    assert result.evidence.limits == limits
    assert result.complete and result.stopped_by is None


def test_result_does_not_depend_on_directory_listing_order(tmp_path, monkeypatch):
    make(tmp_path, "a.py", "b.md", "c.csv", "x/d.py", "y/e.md", "z/f.go")
    natural = run(tmp_path)
    real_walk = os.walk

    def reversed_walk(*args, **kwargs):
        for dirpath, dirnames, filenames in real_walk(*args, **kwargs):
            dirnames.reverse()
            filenames.reverse()
            yield dirpath, dirnames, filenames

    monkeypatch.setattr(os, "walk", reversed_walk)
    assert run(tmp_path) == natural


def test_partial_result_does_not_depend_on_listing_order(tmp_path, monkeypatch):
    make(tmp_path, *[f"d{i}/f{j}.py" for i in range(4) for j in range(4)])
    limits = WalkLimits(max_entries=7)
    natural = run(tmp_path, limits=limits)
    real_walk = os.walk

    def reversed_walk(*args, **kwargs):
        for dirpath, dirnames, filenames in real_walk(*args, **kwargs):
            dirnames.reverse()
            filenames.reverse()
            yield dirpath, dirnames, filenames

    monkeypatch.setattr(os, "walk", reversed_walk)
    assert run(tmp_path, limits=limits) == natural


def test_composition_invariants():
    types = TYPES
    assert types.version == 3
    sample = FileComposition(2, 1, 4, None, None)  # evidence is not used by the properties
    assert sample.total == 7 and sample.documentation_only is False
    partial = FileComposition(0, 5, 0, "depth", None)
    assert partial.documentation_only is None and not partial.complete
