"""Store and load the project report of a checkout."""

from __future__ import annotations

import json
import sqlite3

from vyasa.domain.report import NOT_PRESENT, PRESENT, SECTIONS, ReportLimits, ReportResult

_ORDER = {name: i for i, (name, _) in enumerate(SECTIONS)}


def store(connection: sqlite3.Connection, checkout_id: int, report: ReportResult | None, run_id: str, stamp: str) -> None:
    """Record one read. A failed read keeps the earlier sections; a present read replaces them.

    No read at all (``None``) stores nothing: a checkout without an observation is reported as not assessed.
    """
    if report is None:
        return
    dropped = json.dumps([{"heading": h, "reason": r} for h, r in report.dropped])
    connection.execute(
        "INSERT INTO report_observations (checkout_id, status, reason, content_hash, scanned_at, max_file_bytes,"
        " max_section_bytes, dropped_json, run_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        " ON CONFLICT (checkout_id) DO UPDATE SET status = excluded.status, reason = excluded.reason,"
        " content_hash = excluded.content_hash, scanned_at = excluded.scanned_at, max_file_bytes = excluded.max_file_bytes,"
        " max_section_bytes = excluded.max_section_bytes, dropped_json = excluded.dropped_json, run_id = excluded.run_id",
        (checkout_id, report.status, report.reason, report.content_hash, stamp,
         report.limits.max_file_bytes, report.limits.max_section_bytes, dropped, run_id),
    )
    if report.status == PRESENT:
        connection.execute("DELETE FROM report_sections WHERE checkout_id = ?", (checkout_id,))
        connection.executemany(
            "INSERT INTO report_sections (checkout_id, name, text, size, position) VALUES (?, ?, ?, ?, ?)",
            [(checkout_id, s.name, s.text, s.size, _ORDER[s.name]) for s in report.sections],
        )
        connection.execute("UPDATE report_observations SET kept_hash = ?, kept_at = ? WHERE checkout_id = ?",
                           (report.content_hash, stamp, checkout_id))
    elif report.status == NOT_PRESENT:
        connection.execute("DELETE FROM report_sections WHERE checkout_id = ?", (checkout_id,))
        connection.execute("UPDATE report_observations SET kept_hash = NULL, kept_at = NULL WHERE checkout_id = ?", (checkout_id,))
    # unreadable and invalid: the earlier sections and kept_* stay as they were


def load(connection: sqlite3.Connection, checkout_id: int) -> dict | None:
    """The stored report of one checkout, or None when the checkout was never read."""
    row = connection.execute("SELECT * FROM report_observations WHERE checkout_id = ?", (checkout_id,)).fetchone()
    if row is None:
        return None
    sections = [
        {"name": r["name"], "text": r["text"], "size": r["size"]}
        for r in connection.execute(
            "SELECT name, text, size FROM report_sections WHERE checkout_id = ? ORDER BY position", (checkout_id,)
        )
    ]
    return {
        "status": row["status"], "reason": row["reason"], "content_hash": row["content_hash"], "scanned_at": row["scanned_at"],
        "sections": sections, "dropped": json.loads(row["dropped_json"]),
        "kept_hash": row["kept_hash"], "kept_at": row["kept_at"],
    }


def latest_limits(connection: sqlite3.Connection) -> ReportLimits | None:
    """The limits the newest report observation was read under, or None when there is none."""
    row = connection.execute(
        "SELECT max_file_bytes, max_section_bytes FROM report_observations ORDER BY scanned_at DESC, checkout_id DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return None
    return ReportLimits(row["max_file_bytes"] // 1024, row["max_section_bytes"] // 1024)
