"""Read one manifest from the root of a checkout under strict rules.

Repository files are untrusted. This is the only place the framework detector opens one: a regular file directly
inside the checkout root, never a link, read in binary up to a byte limit, decoded strictly. The caller gets text
or a status with a fixed reason; it never gets an exception message or any part of a rejected file.
"""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path

from vyasa.domain.frameworks import MANIFEST_LIMIT, MALFORMED, TOO_LARGE, UNREADABLE

READ = "read"
_FLAGS = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NOCTTY", 0)


@dataclass(frozen=True)
class ManifestRead:
    """``text`` is set exactly when ``status`` is ``read``."""

    text: str | None
    status: str
    reason: str | None = None


def _refuse(status: str, reason: str | None = None) -> ManifestRead:
    return ManifestRead(None, status, reason)


def read_manifest(root: Path | str, name: str, limit: int = MANIFEST_LIMIT) -> ManifestRead:
    """Read ``root/name`` if it is a regular, non-link file of at most ``limit`` bytes that decodes as UTF-8."""
    if not name or os.sep in name or "/" in name or "\\" in name or name in {".", ".."}:
        return _refuse(UNREADABLE, "not_file")
    path = os.path.join(os.fspath(root), name)
    try:
        before = os.lstat(path)
    except OSError:
        return _refuse(UNREADABLE, "io")
    if stat.S_ISLNK(before.st_mode):
        return _refuse(UNREADABLE, "link")
    if not stat.S_ISREG(before.st_mode):
        return _refuse(UNREADABLE, "not_file")
    if before.st_size > limit:
        return _refuse(TOO_LARGE)
    try:
        descriptor = os.open(path, _FLAGS)
    except OSError:
        return _refuse(UNREADABLE, "io")
    try:
        # The file may have been swapped between lstat and open; check what was actually opened.
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            return _refuse(UNREADABLE, "not_file")
        if not os.path.samestat(before, opened):
            return _refuse(UNREADABLE, "io")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            data = handle.read(limit + 1)
    except OSError:
        return _refuse(UNREADABLE, "io")
    finally:
        os.close(descriptor)
    if len(data) > limit:
        return _refuse(TOO_LARGE)
    try:
        return ManifestRead(data.decode("utf-8-sig"), READ)
    except UnicodeDecodeError:
        return _refuse(MALFORMED, "encoding")
