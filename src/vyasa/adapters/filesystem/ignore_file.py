"""Read a repository's ignore file: bounded, never through a link."""

from __future__ import annotations

import os

from vyasa.domain.ignore import IGNORE_FILE, MAX_IGNORE_BYTES, IgnoreRules, parse_ignore


def read_ignore_file(directory: str) -> tuple[IgnoreRules | None, tuple[str, ...]]:
    """Return the rules of ``<directory>/.vyasaignore`` and any problems.

    ``None`` means no usable file. At most 64 KiB is read, and a link is refused so the file
    cannot be used to read something outside the repository.
    """
    path = os.path.join(directory, IGNORE_FILE)
    if os.path.islink(path):
        return None, (f"{IGNORE_FILE} is a link and was ignored",)
    if not os.path.isfile(path):
        return None, ()
    try:
        with open(path, "rb") as handle:
            data = handle.read(MAX_IGNORE_BYTES + 1)
    except OSError:
        return None, (f"{IGNORE_FILE} cannot be read",)
    if len(data) > MAX_IGNORE_BYTES:
        return None, (f"{IGNORE_FILE} is larger than 64 KiB and was ignored",)
    return parse_ignore(data.decode("utf-8-sig", errors="replace"))
