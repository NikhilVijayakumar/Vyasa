"""A repository's ignore rules: directories Vyasa must not scan inside it.

The file is untrusted. Parsing is pure text work, and the only thing a rule can do is
remove a directory below its own repository from scanning.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

MAX_IGNORE_BYTES = 65536
MAX_IGNORE_PATTERNS = 1000
IGNORE_FILE = ".vyasaignore"

_DRIVE = re.compile(r"^[A-Za-z]:")


def _glob(body: str) -> re.Pattern[str]:
    """Translate ``*``, ``**`` and ``?`` to a regular expression; everything else is literal."""
    out: list[str] = []
    i = 0
    while i < len(body):
        if body.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        char = body[i]
        out.append("[^/]*" if char == "*" else "[^/]" if char == "?" else re.escape(char))
        i += 1
    return re.compile("".join(out))


@dataclass(frozen=True)
class IgnoreRules:
    """Compiled directory patterns. ``patterns`` are normalized; a leading ``/`` marks one anchored at the root."""

    patterns: tuple[str, ...]
    _compiled: tuple[tuple[bool, re.Pattern[str]], ...] = field(default=(), repr=False, compare=False)

    @property
    def digest(self) -> str:
        return hashlib.sha256("\n".join(self.patterns).encode("utf-8")).hexdigest()

    def matches(self, relative: str) -> bool:
        """Whether the directory at ``relative`` (``/`` separated, from the repository root) is ignored."""
        path = relative.casefold()
        name = path.rsplit("/", 1)[-1]
        return any(rx.fullmatch(path if anchored else name) for anchored, rx in self._compiled)


def parse_ignore(text: str) -> tuple[IgnoreRules, tuple[str, ...]]:
    """Parse ignore-file text into rules and a tuple of problems. Never raises."""
    patterns: list[str] = []
    compiled: list[tuple[bool, re.Pattern[str]]] = []
    problems: list[str] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("!"):
            problems.append(f"line {number}: negation is not supported")
            continue
        line = line.replace("\\", "/")
        if _DRIVE.match(line):
            problems.append(f"line {number}: drive letters are not allowed")
            continue
        segments = [part for part in line.split("/") if part and part != "."]
        if not segments:
            problems.append(f"line {number}: empty pattern")
            continue
        if ".." in segments:
            problems.append(f"line {number}: '..' is not allowed")
            continue
        if len(patterns) >= MAX_IGNORE_PATTERNS:
            problems.append(f"too many patterns; the first {MAX_IGNORE_PATTERNS} apply")
            break
        anchored = line.startswith(("/", "./")) or len(segments) > 1
        body = "/".join(segments)
        patterns.append(("/" if anchored else "") + body)
        compiled.append((anchored, _glob(body.casefold())))
    return IgnoreRules(tuple(patterns), tuple(compiled)), tuple(problems)
