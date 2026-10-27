"""Find Git repositories under one root without running anything.

Files opened: ``.git`` pointer files (first kilobyte) and a repository's ``.vyasaignore``
(at most 64 KiB). Behaviour is the same on every platform.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from vyasa.adapters.filesystem.ignore_file import read_ignore_file
from vyasa.adapters.filesystem.pruning import prune
from vyasa.domain.discovery import (
    ELIGIBLE,
    INACCESSIBLE,
    KIND_LINKED_WORKTREE,
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


def classify_git_entry(directory: str) -> Candidate:
    """Decide what the ``.git`` entry in ``directory`` is."""
    path = Path(directory)
    git = os.path.join(directory, GIT)
    if os.path.islink(git) or os.path.isjunction(git):
        return Candidate(path, SKIPPED_BY_POLICY, reason="git_link")
    if os.path.isdir(git):
        if os.path.isfile(os.path.join(git, "HEAD")):
            return Candidate(path, ELIGIBLE, kind=KIND_REPOSITORY)
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
    if len(segments) >= 3 and segments[-2] == "worktrees" and segments[-3].endswith(GIT):
        return Candidate(path, ELIGIBLE, kind=KIND_LINKED_WORKTREE)
    if any(a == GIT and b == "modules" for a, b in zip(segments, segments[1:])):
        return Candidate(path, ELIGIBLE, kind=KIND_SUBMODULE)
    return Candidate(path, ELIGIBLE, kind=KIND_REPOSITORY)


def find_repositories(root: Path | str, options: DiscoveryOptions) -> Findings:
    """Walk ``root`` in sorted order and classify every ``.git`` entry found.

    Each repository's ignore rules apply to everything below it, including nested repositories.
    """
    top = os.fspath(root)
    excluded = {name.casefold() for name in options.exclusions}
    repositories: list[Candidate] = []
    issues: list[Candidate] = []
    ignore_problems: list[tuple[Path, str]] = []
    excluded_count = 0
    # directory -> (repository directory, rules) pairs that apply to it
    active: dict[str, tuple[tuple[str, IgnoreRules], ...]] = {}

    def unreadable(error: OSError) -> None:
        issues.append(Candidate(Path(error.filename or top), INACCESSIBLE, reason="unreadable_directory"))

    for dirpath, dirnames, filenames in os.walk(top, topdown=True, onerror=unreadable, followlinks=False):
        inherited = active.pop(dirpath, ())
        if GIT in dirnames or GIT in filenames:
            found = classify_git_entry(dirpath)
            (repositories if found.outcome == ELIGIBLE else issues).append(found)
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

    return Findings(tuple(repositories), tuple(issues), excluded_count, tuple(ignore_problems))
