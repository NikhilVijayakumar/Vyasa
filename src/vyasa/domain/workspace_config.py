"""Results of loading the workspace configuration. Nothing here touches the filesystem."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from vyasa.domain.report import ReportLimits

ACCESSIBLE = "accessible"
MISSING = "missing"
NOT_A_DIRECTORY = "not_a_directory"
UNREADABLE = "unreadable"


class ConfigError(ValueError):
    """The configuration is invalid. ``problems`` lists every problem found."""

    def __init__(self, problems: tuple[str, ...]):
        self.problems = problems
        super().__init__("; ".join(problems))


@dataclass(frozen=True)
class WorkspaceConfig:
    """Valid configuration with at least one root."""

    roots: tuple[Path, ...]
    source: Path
    warnings: tuple[str, ...] = ()
    report: ReportLimits = ReportLimits()


@dataclass(frozen=True)
class NotConfigured:
    """No usable configuration. Nothing may be scanned."""

    reason: str


@dataclass(frozen=True)
class RootCheck:
    """The state of one configured root."""

    root: Path
    status: str
