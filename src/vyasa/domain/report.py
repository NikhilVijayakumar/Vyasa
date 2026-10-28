"""The project report: its size limits, and (in later slices) its sections, reader, and template.

Nothing here touches the filesystem.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_FILE_KIB = 256
DEFAULT_SECTION_KIB = 16
FILE_KIB_RANGE = (16, 4096)
SECTION_KIB_RANGE = (1, 1024)


@dataclass(frozen=True)
class ReportLimits:
    max_file_kib: int = DEFAULT_FILE_KIB
    max_section_kib: int = DEFAULT_SECTION_KIB

    @property
    def max_file_bytes(self) -> int:
        return self.max_file_kib * 1024

    @property
    def max_section_bytes(self) -> int:
        return self.max_section_kib * 1024


def _integer(table: dict, key: str, default: int, bounds: tuple[int, int], problems: list[str]) -> int:
    value = table.get(key, default)
    name = f"report.{key}"
    if isinstance(value, bool) or not isinstance(value, int):
        problems.append(f"{name} must be an integer")
        return default
    if not bounds[0] <= value <= bounds[1]:
        problems.append(f"{name} must be from {bounds[0]} to {bounds[1]}")
        return default
    return value


def limits_from_table(table: object, problems: list[str]) -> ReportLimits:
    """Validate the optional ``report`` table of the configuration; every problem is appended."""
    if table is None:
        return ReportLimits()
    if not isinstance(table, dict):
        problems.append("'report' must be a table")
        return ReportLimits()
    problems += [f"unknown key 'report.{key}'" for key in table if key not in ("max_file_kib", "max_section_kib")]
    file_kib = _integer(table, "max_file_kib", DEFAULT_FILE_KIB, FILE_KIB_RANGE, problems)
    section_kib = _integer(table, "max_section_kib", DEFAULT_SECTION_KIB, SECTION_KIB_RANGE, problems)
    if section_kib > file_kib:
        problems.append("report.max_section_kib must not be above report.max_file_kib")
        section_kib = file_kib
    return ReportLimits(file_kib, section_kib)
