"""Find projects under one root without running anything.

A project is a directory with a ``.git`` entry, or with a recognized manifest (``pyproject.toml``,
``package.json``, ``Cargo.toml``, a ``.uproject``, ...), or with a README and a docs folder and
no other project inside it. Git is optional; for a manifest project it is looked for in the
directory's immediate children too (Unreal keeps it in ``Source``).

Files opened: ``.git`` pointer files (first kilobyte) and, when nested repositories are enabled,
a repository's ``.vyasaignore`` (at most 64 KiB). Behaviour is the same on every platform.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from vyasa.adapters.filesystem.ignore_file import read_ignore_file
from vyasa.adapters.filesystem.pruning import prune
from vyasa.domain.discovery import (
    DOCUMENTATION_DIRS,
    ELIGIBLE,
    INACCESSIBLE,
    KIND_DOCUMENTATION,
    KIND_LINKED_WORKTREE,
    KIND_PROJECT,
    KIND_REPOSITORY,
    KIND_SUBMODULE,
    MALFORMED,
    SKIPPED_BY_POLICY,
    Candidate,
    DiscoveryOptions,
)
from vyasa.domain.ignore import IgnoreRules

GIT = ".git"
POINTER_BYTES = 1024
GITDIR = "gitdir:"


@dataclass(frozen=True)
class Findings:
    repositories: tuple[Candidate, ...]
    issues: tuple[Candidate, ...]
    excluded: int
    ignore_problems: tuple[tuple[Path, str], ...] = ()


def classify_git_entry(directory: str, markers: tuple[str, ...] = ()) -> Candidate:
    """Decide what the ``.git`` entry in ``directory`` is."""
    path = Path(directory)
    git = os.path.join(directory, GIT)
    if os.path.islink(git) or os.path.isjunction(git):
        return Candidate(path, SKIPPED_BY_POLICY, reason="git_link")
    if os.path.isdir(git):
        if os.path.isfile(os.path.join(git, "HEAD")):
            return Candidate(path, ELIGIBLE, kind=KIND_REPOSITORY, markers=markers, git=".")
        return Candidate(path, MALFORMED, reason="missing_head")
    try:
        with open(git, "rb") as pointer:
            head = pointer.read(POINTER_BYTES)
    except OSError:
        return Candidate(path, INACCESSIBLE, reason="unreadable_git_file")
    lines = head.decode("utf-8", errors="replace").splitlines()
    first = lines[0].strip() if lines else ""
    target = first[len(GITDIR):].strip() if first.startswith(GITDIR) else ""
    if not target:
        return Candidate(path, MALFORMED, reason="invalid_git_file")
    segments = [part for part in target.replace("\\", "/").split("/") if part]
    # Git writes <repo>/worktrees/<name> and <super>/.git/modules/<name>; a bare directory
    # called "modules" or "worktrees" elsewhere in the path proves nothing.
    kind = KIND_REPOSITORY
    if len(segments) >= 3 and segments[-2] == "worktrees" and segments[-3].endswith(GIT):
        kind = KIND_LINKED_WORKTREE
    elif any(a == GIT and b == "modules" for a, b in zip(segments, segments[1:])):
        kind = KIND_SUBMODULE
    return Candidate(path, ELIGIBLE, kind=kind, markers=markers, git=".")


def _markers(filenames: list[str], options: DiscoveryOptions) -> tuple[str, ...]:
    names = {name.casefold() for name in options.markers}
    return tuple(
        sorted(f for f in filenames if f.casefold() in names or f.casefold().endswith(options.marker_suffixes))
    )


def _is_documentation_project(dirnames: list[str], filenames: list[str]) -> bool:
    return any(f.casefold().startswith("readme") for f in filenames) and any(
        d.casefold() in DOCUMENTATION_DIRS for d in dirnames
    )


def _child_git(dirpath: str, dirnames: list[str], excluded: set[str]) -> str | None:
    """The immediate child directory holding a valid ``.git``, if any (Unreal: ``Source``)."""
    for name in sorted(dirnames):
        full = os.path.join(dirpath, name)
        if name.casefold() in excluded or os.path.islink(full) or os.path.isjunction(full):
            continue
        if os.path.lexists(os.path.join(full, GIT)) and classify_git_entry(full).outcome == ELIGIBLE:
            return name
    return None


def find_repositories(root: Path | str, options: DiscoveryOptions) -> Findings:
    """Walk ``root`` in sorted order and recognize projects.

    A recognized project is a boundary and is not entered, unless ``options.descend_into_repositories``
    is set; then projects inside it are found too, and each repository's ignore rules apply to
    everything below it. A README-and-docs directory is kept only if no project lies below it.
    """
    top = os.fspath(root)
    excluded = {name.casefold() for name in options.exclusions}
    projects: list[Candidate] = []
    documentation: list[Candidate] = []
    issues: list[Candidate] = []
    ignore_problems: list[tuple[Path, str]] = []
    excluded_count = 0
    # directory -> (repository directory, rules) pairs that apply to it
    active: dict[str, tuple[tuple[str, IgnoreRules], ...]] = {}

    def unreadable(error: OSError) -> None:
        issues.append(Candidate(Path(error.filename or top), INACCESSIBLE, reason="unreadable_directory"))

    for dirpath, dirnames, filenames in os.walk(top, topdown=True, onerror=unreadable, followlinks=False):
        inherited = active.pop(dirpath, ())
        markers = _markers(filenames, options)
        found: Candidate | None = None
        if GIT in dirnames or GIT in filenames:
            found = classify_git_entry(dirpath, markers)
            (projects if found.outcome == ELIGIBLE else issues).append(found)
        elif markers:
            found = Candidate(
                Path(dirpath), ELIGIBLE, kind=KIND_PROJECT, markers=markers, git=_child_git(dirpath, dirnames, excluded)
            )
            projects.append(found)
        elif _is_documentation_project(dirnames, filenames):
            documentation.append(
                Candidate(Path(dirpath), ELIGIBLE, kind=KIND_DOCUMENTATION, git=_child_git(dirpath, dirnames, excluded))
            )

        if found is not None:
            if not options.descend_into_repositories:
                dirnames[:] = []  # a project is a boundary: recognize it, do not enter it
                continue
            if found.outcome == ELIGIBLE:
                rules, problems = read_ignore_file(dirpath)
                ignore_problems.extend((Path(dirpath), message) for message in problems)
                if rules is not None:
                    inherited = (*inherited, (dirpath, rules))

        pruned = prune(dirpath, [name for name in dirnames if name != GIT], excluded)
        excluded_count += pruned.excluded
        issues.extend(Candidate(Path(dirpath, name), SKIPPED_BY_POLICY, reason="symlink") for name in pruned.linked)

        kept = []
        for name in pruned.kept:
            child = Path(dirpath, name)
            if any(rules.matches(child.relative_to(base).as_posix()) for base, rules in inherited):
                excluded_count += 1
            else:
                kept.append(name)

        if len(Path(dirpath).relative_to(top).parts) >= options.max_depth:
            issues.extend(Candidate(Path(dirpath, name), SKIPPED_BY_POLICY, reason="max_depth") for name in kept)
            kept = []
        for name in kept:
            active[os.path.join(dirpath, name)] = inherited
        dirnames[:] = kept

    # A README-and-docs folder that contains projects is a container, not a project. Its own Git
    # folder (Unreal's Source) is where its Git lives, not a project inside it.
    for candidate in documentation:
        home = candidate.path / candidate.git if candidate.git else None
        inside = [p for p in projects if p.path != home and candidate.path in p.path.parents]
        if not inside:
            projects = [p for p in projects if p.path != home]
            projects.append(candidate)
    return Findings(tuple(projects), tuple(issues), excluded_count, tuple(ignore_problems))
