import builtins
import os
from datetime import datetime, timedelta, timezone

import pytest

import vyasa
from vyasa.application.scanning.discovery import discover_repositories
from vyasa.domain.discovery import (
    COMPLETE,
    EXCLUDED,
    FAILED,
    INACCESSIBLE,
    KIND_LINKED_WORKTREE,
    KIND_REPOSITORY,
    KIND_SUBMODULE,
    MALFORMED,
    OUTCOMES,
    PARTIAL,
    SKIPPED_BY_POLICY,
    DiscoveryOptions,
)

T0 = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)


def repo(root, relative="."):
    git = root / relative / ".git"
    git.mkdir(parents=True)
    (git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    return root / relative


def pointer(root, relative, text):
    directory = root / relative
    directory.mkdir(parents=True, exist_ok=True)
    (directory / ".git").write_text(text, encoding="utf-8")
    return directory


def ticking():
    state = {"n": 0}

    def now():
        state["n"] += 1
        return T0 + timedelta(seconds=state["n"])

    return now


def run(root, **options):
    return discover_repositories(root, DiscoveryOptions(**options), now=ticking(), new_id=lambda: "run-1")


def found(result):
    return [c.path.relative_to(result.root).as_posix() for c in result.repositories]


def reasons(result):
    return sorted((c.reason, c.outcome) for c in result.issues)


def warned(result):
    return {w.reason: w.count for w in result.warnings}


# -- recognition -------------------------------------------------------------------


def test_git_directory_with_head_is_an_eligible_repository(tmp_path):
    repo(tmp_path, "proj")
    result = run(tmp_path)
    assert found(result) == ["proj"]
    assert result.repositories[0].kind == KIND_REPOSITORY
    assert result.repositories[0].outcome == "eligible" and result.repositories[0].reason is None


def test_the_root_itself_can_be_a_repository(tmp_path):
    repo(tmp_path)
    result = run(tmp_path)
    assert found(result) == ["."]


def test_submodule_pointer(tmp_path):
    pointer(tmp_path, "lib", "gitdir: ../.git/modules/lib\n")
    assert run(tmp_path).repositories[0].kind == KIND_SUBMODULE


def test_linked_worktree_pointer(tmp_path):
    pointer(tmp_path, "wt", "gitdir: /somewhere/repo/.git/worktrees/wt\n")
    assert run(tmp_path).repositories[0].kind == KIND_LINKED_WORKTREE


def test_windows_style_pointer_paths_are_classified_the_same_way(tmp_path):
    pointer(tmp_path, "wt", "gitdir: C:\\repo\\.git\\worktrees\\wt\n")
    assert run(tmp_path).repositories[0].kind == KIND_LINKED_WORKTREE


def test_pointer_elsewhere_is_a_repository(tmp_path):
    pointer(tmp_path, "r", "gitdir: /elsewhere/repo.git\n")
    assert run(tmp_path).repositories[0].kind == KIND_REPOSITORY


def test_ordinary_directories_are_not_candidates(tmp_path):
    (tmp_path / "docs" / "deep").mkdir(parents=True)
    (tmp_path / "docs" / "note.md").write_text("x", encoding="utf-8")
    result = run(tmp_path)
    assert result.repositories == () and result.issues == ()
    assert result.status == COMPLETE


def test_nested_repositories_are_separate_candidates(tmp_path):
    repo(tmp_path, "outer")
    repo(tmp_path, "outer/vendor/inner")
    result = run(tmp_path, descend_into_repositories=True)
    assert found(result) == ["outer", "outer/vendor/inner"]


def test_repositories_are_sorted_by_path_parts(tmp_path):
    repo(tmp_path, "b")
    repo(tmp_path, "a-x")
    repo(tmp_path, "a/z")
    assert found(run(tmp_path)) == ["a/z", "a-x", "b"]


# -- outcomes ------------------------------------------------------------------------------


def test_git_directory_without_head_is_malformed_and_others_continue(tmp_path):
    (tmp_path / "bad" / ".git").mkdir(parents=True)
    repo(tmp_path, "good")
    result = run(tmp_path)
    assert found(result) == ["good"]
    assert reasons(result) == [("missing_head", MALFORMED)]
    assert result.status == PARTIAL


@pytest.mark.parametrize("text", ["", "not a pointer\n", "gitdir:\n", "gitdir:    \n", "\ngitdir: x\n"])
def test_bad_git_file_is_malformed(tmp_path, text):
    pointer(tmp_path, "r", text)
    result = run(tmp_path)
    assert result.repositories == ()
    assert reasons(result) == [("invalid_git_file", MALFORMED)]


def test_unreadable_git_file_is_inaccessible(tmp_path, monkeypatch):
    pointer(tmp_path, "r", "gitdir: x\n")
    real = builtins.open

    def guarded(file, *args, **kwargs):
        if os.path.basename(os.fspath(file)) == ".git":
            raise PermissionError(13, "denied", os.fspath(file))
        return real(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", guarded)
    result = run(tmp_path)
    assert reasons(result) == [("unreadable_git_file", INACCESSIBLE)]


def test_unreadable_directory_is_reported_and_the_rest_is_searched(tmp_path, monkeypatch):
    repo(tmp_path, "good")
    repo(tmp_path, "locked/hidden")
    locked = os.fspath(tmp_path / "locked")
    real = os.scandir

    def scandir(path="."):
        if os.fspath(path) == locked:
            raise PermissionError(13, "denied", locked)
        return real(path)

    monkeypatch.setattr(os, "scandir", scandir)
    result = run(tmp_path)
    assert found(result) == ["good"]
    assert reasons(result) == [("unreadable_directory", INACCESSIBLE)]
    assert result.issues[0].path == tmp_path / "locked"
    assert result.status == PARTIAL


# -- boundaries ----------------------------------------------------------------------------------


def test_repository_beyond_the_depth_limit_is_not_found_and_the_skip_is_reported(tmp_path):
    repo(tmp_path, "a/b/c/d")
    result = run(tmp_path, max_depth=3)
    assert result.repositories == ()
    assert result.issues == ()
    assert warned(result) == {"max_depth": 1}
    assert result.warnings[0].examples == (tmp_path / "a" / "b" / "c" / "d",)
    assert result.counts[SKIPPED_BY_POLICY] == 1
    assert result.status == COMPLETE


def test_repository_exactly_at_the_depth_limit_is_found(tmp_path):
    repo(tmp_path, "a/b/c")
    result = run(tmp_path, max_depth=3)
    assert found(result) == ["a/b/c"]
    assert result.status == COMPLETE


def test_excluded_directories_are_not_entered_and_are_counted_not_listed(tmp_path):
    repo(tmp_path, "node_modules/dep")
    repo(tmp_path, "Build/out")
    repo(tmp_path, "real")
    result = run(tmp_path)
    assert found(result) == ["real"]
    assert result.counts[EXCLUDED] == 2
    assert result.issues == ()
    assert result.status == COMPLETE


def test_git_directories_do_not_inflate_the_excluded_count(tmp_path):
    repo(tmp_path, "one")
    repo(tmp_path, "two")
    assert run(tmp_path).counts[EXCLUDED] == 0


def test_custom_exclusions_replace_the_defaults(tmp_path):
    repo(tmp_path, "node_modules/dep")
    repo(tmp_path, "skip/me")
    result = run(tmp_path, exclusions=frozenset({"skip"}))
    assert found(result) == ["node_modules/dep"]
    assert result.counts[EXCLUDED] == 1


def symlink_dir(link, target):
    try:
        os.symlink(target, link, target_is_directory=True)
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"this platform or account cannot create directory symlinks: {error}")


def test_directory_symlink_is_not_followed_and_is_reported(tmp_path):
    outside = tmp_path / "outside"
    repo(outside, "elsewhere")
    root = tmp_path / "root"
    repo(root, "own")
    symlink_dir(root / "link", outside)
    result = run(root)
    assert found(result) == ["own"]
    assert warned(result) == {"symlink": 1}
    assert result.status == COMPLETE


def test_junction_is_not_followed_and_is_reported(tmp_path):
    winapi = pytest.importorskip("_winapi", reason="directory junctions exist only on Windows")
    outside = tmp_path / "outside"
    repo(outside, "elsewhere")
    root = tmp_path / "root"
    repo(root, "own")
    winapi.CreateJunction(os.fspath(outside), os.fspath(root / "junction"))
    result = run(root)
    assert found(result) == ["own"]
    assert warned(result) == {"symlink": 1}


def test_a_symlinked_git_entry_is_skipped_by_policy(tmp_path):
    real_git = tmp_path / "elsewhere" / "real.git"
    real_git.mkdir(parents=True)
    (real_git / "HEAD").write_text("x", encoding="utf-8")
    project = tmp_path / "root" / "proj"
    project.mkdir(parents=True)
    symlink_dir(project / ".git", real_git)
    result = run(tmp_path / "root")
    assert result.repositories == ()
    assert warned(result) == {"git_link": 1}


# -- status ---------------------------------------------------------------------------------------------


def test_complete_run(tmp_path):
    repo(tmp_path, "a")
    (tmp_path / "plain").mkdir()
    result = run(tmp_path)
    assert result.status == COMPLETE and result.issues == ()


def test_missing_root_fails(tmp_path):
    result = run(tmp_path / "missing")
    assert result.status == FAILED
    assert reasons(result) == [("root_not_found", INACCESSIBLE)]
    assert result.repositories == ()


def test_root_that_is_a_file_fails(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("x", encoding="utf-8")
    result = run(file)
    assert result.status == FAILED
    assert reasons(result) == [("root_not_a_directory", INACCESSIBLE)]


def test_unreadable_root_fails(tmp_path, monkeypatch):
    root = os.fspath(tmp_path)
    real = os.scandir

    def scandir(path="."):
        if os.fspath(path) == root:
            raise PermissionError(13, "denied", root)
        return real(path)

    monkeypatch.setattr(os, "scandir", scandir)
    result = run(tmp_path)
    assert result.status == FAILED
    assert reasons(result) == [("root_unreadable", INACCESSIBLE)]


# -- the record ----------------------------------------------------------------------------------------------


def test_record_contents(tmp_path):
    repo(tmp_path, "a")
    options = DiscoveryOptions(max_depth=4)
    result = discover_repositories(tmp_path, options, now=ticking(), new_id=lambda: "abc")
    assert result.run_id == "abc"
    assert result.root == tmp_path
    assert result.started_at == T0 + timedelta(seconds=1)
    assert result.finished_at == T0 + timedelta(seconds=2)
    assert result.started_at.tzinfo is not None
    assert result.status == COMPLETE
    assert result.tool_version == vyasa.__version__
    assert result.options == options
    assert set(result.counts) == set(OUTCOMES)
    assert result.counts["eligible"] == 1


def test_counts_cover_every_outcome_and_match_the_lists(tmp_path):
    repo(tmp_path, "ok")
    (tmp_path / "bad" / ".git").mkdir(parents=True)
    pointer(tmp_path, "worse", "junk")
    repo(tmp_path, "node_modules/x")
    repo(tmp_path, "a/b/c/d/e/f/g")
    result = run(tmp_path, max_depth=6)
    assert result.counts["eligible"] == len(result.repositories) == 1
    assert result.counts[MALFORMED] == 2
    assert result.counts[EXCLUDED] == 1
    assert result.counts[SKIPPED_BY_POLICY] == 1
    assert sum(result.counts[o] for o in (INACCESSIBLE, MALFORMED)) == len(result.issues) + result.issues_omitted
    assert result.counts[SKIPPED_BY_POLICY] == sum(w.count for w in result.warnings)


def test_issues_are_bounded_but_fully_counted(tmp_path):
    for i in range(5):
        (tmp_path / f"bad{i}" / ".git").mkdir(parents=True)
    result = run(tmp_path, max_issues=2)
    assert len(result.issues) == 2
    assert result.issues_omitted == 3
    assert result.counts[MALFORMED] == 5


def test_unchanged_tree_gives_the_same_result(tmp_path):
    repo(tmp_path, "a")
    repo(tmp_path, "b/c")
    (tmp_path / "bad" / ".git").mkdir(parents=True)
    first, second = run(tmp_path), run(tmp_path)
    assert (first.repositories, first.issues, first.counts, first.status) == (
        second.repositories, second.issues, second.counts, second.status
    )


def test_result_does_not_depend_on_listing_order(tmp_path, monkeypatch):
    repo(tmp_path, "a")
    repo(tmp_path, "b/c")
    repo(tmp_path, "d")
    (tmp_path / "bad" / ".git").mkdir(parents=True)
    natural = run(tmp_path)
    real_walk = os.walk

    def reversed_walk(*args, **kwargs):
        for dirpath, dirnames, filenames in real_walk(*args, **kwargs):
            dirnames.reverse()
            filenames.reverse()
            yield dirpath, dirnames, filenames

    monkeypatch.setattr(os, "walk", reversed_walk)
    other = run(tmp_path)
    assert (other.repositories, other.issues, other.counts) == (natural.repositories, natural.issues, natural.counts)


# -- safety ----------------------------------------------------------------------------------------------------


def test_only_git_pointer_files_are_opened(tmp_path, monkeypatch):
    repo(tmp_path, "plain")
    pointer(tmp_path, "sub", "gitdir: ../.git/modules/sub\n")
    (tmp_path / "plain" / "secret.txt").write_text("x", encoding="utf-8")
    (tmp_path / "other.md").write_text("x", encoding="utf-8")
    opened = []
    real = builtins.open

    def recording(file, *args, **kwargs):
        opened.append(os.path.basename(os.fspath(file)))
        return real(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", recording)
    result = run(tmp_path)
    assert len(result.repositories) == 2
    assert opened == [".git"]


def test_pointer_reads_at_most_one_kilobyte(tmp_path, monkeypatch):
    pointer(tmp_path, "big", "gitdir: " + "x/" * 5000 + "\n")
    sizes = []
    real = builtins.open

    class Watching:
        def __init__(self, handle):
            self.handle = handle

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.handle.close()

        def read(self, size=-1):
            sizes.append(size)
            return self.handle.read(size)

    def watching(file, *args, **kwargs):
        handle = real(file, *args, **kwargs)
        return Watching(handle) if os.path.basename(os.fspath(file)) == ".git" else handle

    monkeypatch.setattr(builtins, "open", watching)
    run(tmp_path)
    assert sizes == [1024]


# -- found by the grill --------------------------------------------------------------------------------------


def test_policy_skips_are_summarized_per_reason_with_a_few_examples_and_advice(tmp_path):
    for i in range(8):
        (tmp_path / f"a{i}" / "b" / "c").mkdir(parents=True)
    result = run(tmp_path, max_depth=2)
    assert result.counts[SKIPPED_BY_POLICY] == 8
    assert len(result.warnings) == 1
    warning = result.warnings[0]
    assert (warning.reason, warning.count) == ("max_depth", 8)
    assert len(warning.examples) == 5
    assert ".vyasaignore" in warning.advice and "max_depth" in warning.advice
    assert result.issues == () and result.status == COMPLETE


def test_a_real_failure_is_never_hidden_by_skips(tmp_path):
    for i in range(6):
        (tmp_path / f"a{i}" / "b" / "c").mkdir(parents=True)
    (tmp_path / "zz-bad" / ".git").mkdir(parents=True)
    result = run(tmp_path, max_depth=2, max_issues=2)
    assert [(c.outcome, c.reason) for c in result.issues] == [(MALFORMED, "missing_head")]
    assert result.status == PARTIAL
    assert warned(result) == {"max_depth": 6}


def test_default_depth_is_eight(tmp_path):
    assert DiscoveryOptions().max_depth == 8
    repo(tmp_path, "a/b/c/d/e/f/g/h")
    assert found(run(tmp_path)) == ["a/b/c/d/e/f/g/h"]


def test_a_modules_directory_alone_does_not_make_a_submodule(tmp_path):
    pointer(tmp_path, "r", "gitdir: /home/me/modules/repo.git\n")
    assert run(tmp_path).repositories[0].kind == KIND_REPOSITORY


def test_a_worktrees_directory_alone_does_not_make_a_worktree(tmp_path):
    pointer(tmp_path, "r", "gitdir: /home/me/worktrees/repo.git\n")
    assert run(tmp_path).repositories[0].kind == KIND_REPOSITORY


def test_worktree_of_a_bare_repository_and_nested_submodule_pointers(tmp_path):
    pointer(tmp_path, "w", "gitdir: /srv/bare.git/worktrees/feature\n")
    pointer(tmp_path, "s", "gitdir: ../.git/modules/outer/modules/inner\n")
    kinds = {c.path.name: c.kind for c in run(tmp_path).repositories}
    assert kinds == {"w": KIND_LINKED_WORKTREE, "s": KIND_SUBMODULE}


def test_a_root_that_is_itself_a_symlink_is_searched(tmp_path):
    real = tmp_path / "real"
    repo(real, "proj")
    link = tmp_path / "link"
    symlink_dir(link, real)
    result = run(link)
    assert found(result) == ["proj"]
    assert result.status == COMPLETE


# -- repository-provided ignore file -----------------------------------------------------------------------


def ignore(directory, text):
    (directory / ".vyasaignore").write_text(text, encoding="utf-8")


def warning(result, reason):
    return next((w for w in result.warnings if w.reason == reason), None)


def test_an_ignored_directory_is_not_entered_counted_as_excluded_and_not_warned(tmp_path):
    root = repo(tmp_path, "proj")
    repo(root, "data/inner")
    repo(root, "src/real")
    ignore(root, "data\n")
    result = run(tmp_path, descend_into_repositories=True)
    assert found(result) == ["proj", "proj/src/real"]
    assert result.counts[EXCLUDED] == 1
    assert result.warnings == () and result.status == COMPLETE


def test_a_bare_name_is_ignored_at_every_depth(tmp_path):
    root = repo(tmp_path, "proj")
    repo(root, "a/fixtures/x")
    repo(root, "a/b/fixtures/y")
    ignore(root, "fixtures\n")
    result = run(tmp_path, descend_into_repositories=True)
    assert found(result) == ["proj"]
    assert result.counts[EXCLUDED] == 2


def test_a_path_pattern_is_anchored_at_the_repository_root(tmp_path):
    root = repo(tmp_path, "proj")
    repo(root, "data/novel/output/hidden")
    repo(root, "other/data/novel/output/shown")
    ignore(root, "data/novel/output\n")
    assert found(run(tmp_path, descend_into_repositories=True)) == ["proj", "proj/other/data/novel/output/shown"]


def test_glob_patterns_apply(tmp_path):
    root = repo(tmp_path, "proj")
    repo(root, "data/x/cache/gone")
    repo(root, "data/x/y/cache/kept")
    ignore(root, "data/*/cache\n")
    assert found(run(tmp_path, descend_into_repositories=True)) == ["proj", "proj/data/x/y/cache/kept"]


def test_an_ignore_file_does_not_reach_a_sibling_repository(tmp_path):
    first = repo(tmp_path, "first")
    second = repo(tmp_path, "second")
    repo(first, "data/inner")
    repo(second, "data/inner")
    ignore(first, "data\n")
    assert found(run(tmp_path, descend_into_repositories=True)) == ["first", "second", "second/data/inner"]


def test_a_nested_repository_keeps_the_enclosing_rules_and_adds_its_own(tmp_path):
    outer = repo(tmp_path, "outer")
    inner = repo(outer, "pkg/inner")
    for where in (outer, inner):
        for name in ("vendor-data", "cache", "keep"):
            repo(where, f"{name}/probe")
    ignore(outer, "vendor-data\n")
    ignore(inner, "cache\n")
    result = run(tmp_path, descend_into_repositories=True)
    kept = found(result)
    assert "outer/pkg/inner/keep/probe" in kept
    assert "outer/pkg/inner/vendor-data/probe" not in kept
    assert "outer/pkg/inner/cache/probe" not in kept
    assert "outer/cache/probe" in kept
    assert "outer/vendor-data/probe" not in kept


def test_an_ignored_directory_below_the_depth_limit_is_excluded_not_warned(tmp_path):
    root = repo(tmp_path, "proj")
    (root / "x" / "deep").mkdir(parents=True)
    ignore(root, "deep\n")
    result = run(tmp_path, max_depth=2, descend_into_repositories=True)
    assert result.counts[EXCLUDED] == 1
    assert warning(result, "max_depth") is None


def test_a_bad_line_is_reported_and_the_valid_line_still_applies(tmp_path):
    root = repo(tmp_path, "proj")
    repo(root, "data/inner")
    ignore(root, "!keep\ndata\n")
    result = run(tmp_path, descend_into_repositories=True)
    assert found(result) == ["proj"]
    assert result.status == COMPLETE
    notice = warning(result, "ignore_file")
    assert notice is not None
    assert notice.count == 1 and notice.examples == (root,)
    assert notice.details == ("proj/.vyasaignore: line 1: negation is not supported",)
    assert ".vyasaignore" in notice.advice


def test_an_oversized_ignore_file_is_reported_and_none_of_it_applies(tmp_path):
    root = repo(tmp_path, "proj")
    repo(root, "data/inner")
    (root / ".vyasaignore").write_text("data\n" + "x\n" * 40000, encoding="utf-8")
    result = run(tmp_path, descend_into_repositories=True)
    assert "proj/data/inner" in found(result)
    notice = warning(result, "ignore_file")
    assert notice is not None and "larger than 64 KiB" in notice.details[0]


def test_the_ignore_file_of_a_non_repository_is_not_read(tmp_path):
    (tmp_path / "plain" / "data" / "inner").mkdir(parents=True)
    repo(tmp_path, "plain/data/inner")
    ignore(tmp_path / "plain", "data\n")
    assert found(run(tmp_path)) == ["plain/data/inner"]


def test_an_ignore_file_at_the_root_of_a_repository_that_is_the_workspace_root_applies(tmp_path):
    repo(tmp_path)
    repo(tmp_path, "data/inner")
    ignore(tmp_path, "data\n")
    assert found(run(tmp_path)) == ["."]


def test_only_pointer_and_ignore_files_are_opened(tmp_path, monkeypatch):
    plain = repo(tmp_path, "plain")
    pointer(tmp_path, "sub", "gitdir: ../.git/modules/sub\n")
    ignore(plain, "data\n")
    (plain / "secret.txt").write_text("x", encoding="utf-8")
    opened = []
    real = builtins.open

    def recording(file, *args, **kwargs):
        opened.append(os.path.basename(os.fspath(file)))
        return real(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", recording)
    run(tmp_path, descend_into_repositories=True)
    assert sorted(opened) == [".git", ".vyasaignore"]


# -- projects by manifest, README and docs; boundaries -----------------------------------------------------------


def touch(root, *relative):
    for item in relative:
        path = root / item
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x", encoding="utf-8")


def kinds(result):
    return {c.path.relative_to(result.root).as_posix(): c.kind for c in result.repositories}


@pytest.mark.parametrize(
    "manifest",
    ["pyproject.toml", "requirements.txt", "setup.py", "package.json", "Cargo.toml", "go.mod", "Tantra.uproject", "X.UPROJECT"],
)
def test_a_manifest_makes_a_project_even_without_git(tmp_path, manifest):
    touch(tmp_path, f"proj/{manifest}")
    result = run(tmp_path)
    assert kinds(result) == {"proj": "project"}
    assert result.repositories[0].git is None
    assert result.repositories[0].markers == (manifest,)


def test_source_files_and_a_readme_alone_are_not_a_project(tmp_path):
    touch(tmp_path, "scripts/tool.py", "scripts/notes.md", "web/app.ts", "web/README.md", "lib.rs")
    assert run(tmp_path).repositories == ()


def test_a_git_repository_also_records_the_manifests_it_holds(tmp_path):
    root = repo(tmp_path, "proj")
    touch(root, "package.json", "pyproject.toml")
    candidate = run(tmp_path).repositories[0]
    assert candidate.kind == KIND_REPOSITORY and candidate.git == "."
    assert candidate.markers == ("package.json", "pyproject.toml")


def test_an_unreal_project_keeps_git_in_its_source_folder(tmp_path):
    touch(tmp_path, "tutorials/tps/Tantra/Tantra.uproject")
    repo(tmp_path, "tutorials/tps/Tantra/Source")
    result = run(tmp_path)
    assert kinds(result) == {"tutorials/tps/Tantra": "project"}
    assert result.repositories[0].git == "Source"
    assert result.status == COMPLETE and result.warnings == ()


def test_a_broken_git_in_a_child_folder_is_not_reported_as_git(tmp_path):
    touch(tmp_path, "proj/package.json")
    (tmp_path / "proj" / "Source" / ".git").mkdir(parents=True)
    candidate = run(tmp_path).repositories[0]
    assert candidate.git is None


def test_a_project_is_a_boundary_and_is_not_entered(tmp_path):
    touch(tmp_path, "outer/package.json", "outer/sub/pyproject.toml")
    repo(tmp_path, "outer/vendor/inner")
    result = run(tmp_path)
    assert kinds(result) == {"outer": "project"}
    assert result.warnings == () and result.counts[SKIPPED_BY_POLICY] == 0


def test_nested_projects_are_found_when_asked(tmp_path):
    touch(tmp_path, "outer/package.json", "outer/sub/pyproject.toml")
    result = run(tmp_path, descend_into_repositories=True)
    assert sorted(kinds(result)) == ["outer", "outer/sub"]


def test_plain_folders_are_searched_down_to_the_project(tmp_path):
    touch(tmp_path, "a/b/c/d/proj/package.json")
    assert kinds(run(tmp_path)) == {"a/b/c/d/proj": "project"}


def test_the_default_run_opens_only_git_pointer_files(tmp_path, monkeypatch):
    plain = repo(tmp_path, "plain")
    ignore(plain, "data\n")
    pointer(tmp_path, "sub", "gitdir: ../.git/modules/sub\n")
    touch(tmp_path, "app/package.json")
    opened = []
    real = builtins.open

    def recording(file, *args, **kwargs):
        opened.append(os.path.basename(os.fspath(file)))
        return real(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", recording)
    assert len(run(tmp_path).repositories) == 3
    assert opened == [".git"]


def test_a_documentation_only_folder_without_git_is_ignored(tmp_path):
    touch(tmp_path, "idea/README.md", "idea/docs/vision.md", "notes/README.md", "notes/a.md")
    result = run(tmp_path)
    assert result.repositories == () and result.issues == () and result.warnings == ()
    assert result.status == COMPLETE


def test_a_documentation_only_repository_with_git_is_tracked(tmp_path):
    root = repo(tmp_path, "idea")
    touch(root, "README.md", "docs/vision.md")
    result = run(tmp_path)
    assert kinds(result) == {"idea": "repository"}
    assert result.repositories[0].git == "."
