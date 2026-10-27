"""Read a project's Git remote from ``.git/config`` as text: bounded, never through a link, never by running Git."""

from __future__ import annotations

import os

from vyasa.domain.git_remote import STATUS_NONE, STATUS_UNAVAILABLE, GitRemote, choose_remote, parse_remotes

MAX_CONFIG_BYTES = 65536


def _is_link(path: str) -> bool:
    return os.path.islink(path) or os.path.isjunction(path)


def read_remote(directory: str) -> tuple[GitRemote | None, str]:
    """The chosen remote of the project at ``directory`` and a status.

    Only a ``.git`` directory is read. A pointer file (worktree, submodule), a link, an unreadable
    or oversized config give ``unavailable``; a repository with no config or no remote gives ``none``.
    """
    git = os.path.join(directory, ".git")
    if _is_link(git) or not os.path.isdir(git):
        return None, STATUS_UNAVAILABLE
    config = os.path.join(git, "config")
    if _is_link(config):
        return None, STATUS_UNAVAILABLE
    if not os.path.isfile(config):
        return None, STATUS_NONE
    try:
        with open(config, "rb") as handle:
            data = handle.read(MAX_CONFIG_BYTES + 1)
    except OSError:
        return None, STATUS_UNAVAILABLE
    if len(data) > MAX_CONFIG_BYTES:
        return None, STATUS_UNAVAILABLE
    return choose_remote(parse_remotes(data.decode("utf-8-sig", errors="replace")))
