"""Read ``.vyasa/project-report.md`` as text: bounded, never through a link, never executed."""

from __future__ import annotations

import hashlib
import os

from vyasa.domain.report import INVALID, NOT_PRESENT, UNREADABLE, ReportLimits, ReportResult, read_report

NOT_REGULAR = "must be a regular file, not a link"


def _link(path: str) -> bool:
    return os.path.islink(path) or os.path.isjunction(path)


def read_report_file(directory: str, limits: ReportLimits) -> ReportResult:
    """The report of the project at ``directory``; every failure is a status, never an exception."""
    folder = os.path.join(directory, ".vyasa")
    path = os.path.join(folder, "project-report.md")
    if not os.path.lexists(folder):
        return ReportResult(NOT_PRESENT, limits=limits)
    if _link(folder):
        return ReportResult(UNREADABLE, limits=limits, reason=NOT_REGULAR)
    if not os.path.lexists(path):
        return ReportResult(NOT_PRESENT, limits=limits)
    if _link(path) or not os.path.isdir(folder) or not os.path.isfile(path):
        return ReportResult(UNREADABLE, limits=limits, reason=NOT_REGULAR)
    try:
        with open(path, "rb") as handle:
            data = handle.read(limits.max_file_bytes + 1)
    except OSError:
        return ReportResult(UNREADABLE, limits=limits, reason="could not be read")
    if len(data) > limits.max_file_bytes:
        return ReportResult(INVALID, limits=limits, reason=f"is larger than {limits.max_file_kib} KiB")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return ReportResult(INVALID, limits=limits, reason="is not valid UTF-8")
    return read_report(text, limits, hashlib.sha256(data).hexdigest())
