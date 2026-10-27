"""Read ``.vyasa/project-profile.toml`` as text: bounded, never through a link, never executed."""

from __future__ import annotations

import os
import tomllib

from vyasa.domain.profile import ABSENT, MAX_BYTES, UNREADABLE, ProfileResult, validate_profile


def _link(path: str) -> bool:
    return os.path.islink(path) or os.path.isjunction(path)


def read_profile(directory: str) -> ProfileResult:
    """The profile of the project at ``directory``; every failure is a status, never an exception."""
    folder = os.path.join(directory, ".vyasa")
    path = os.path.join(folder, "project-profile.toml")
    if not os.path.lexists(folder):
        return ProfileResult(ABSENT)
    if _link(folder):
        return ProfileResult(UNREADABLE, {}, (("profile", "must be a regular file, not a link"),))
    if not os.path.lexists(path):
        return ProfileResult(ABSENT)
    if _link(path) or not os.path.isdir(folder) or not os.path.isfile(path):
        return ProfileResult(UNREADABLE, {}, (("profile", "must be a regular file, not a link"),))
    try:
        with open(path, "rb") as handle:
            data = handle.read(MAX_BYTES + 1)
    except OSError:
        return ProfileResult(UNREADABLE, {}, (("profile", "could not be read"),))
    if len(data) > MAX_BYTES:
        return ProfileResult(UNREADABLE, {}, (("profile", f"is larger than {MAX_BYTES // 1024} KiB"),))
    try:
        parsed = tomllib.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError):
        return ProfileResult(UNREADABLE, {}, (("profile", "is not valid TOML"),))
    return validate_profile(parsed)
