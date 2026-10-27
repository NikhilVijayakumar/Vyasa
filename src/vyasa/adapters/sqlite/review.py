"""Review candidates: open flags explained by their rule, and a reviewer's local decisions about them."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from vyasa.domain.index import (
    CANDIDATE_NOT_FOUND,
    FLAG_OPEN,
    INVALID_DECISION,
    MAX_NOTE,
    REVIEW_OPEN,
    REVIEW_STATUSES,
    RULES,
    IndexStoreError,
)


def decide(
    connection: sqlite3.Connection, project_id: str, kind: str, status: str, note: str | None = None, *, now: datetime
) -> None:
    """Record a decision about an open candidate. Writes ``review_decisions`` and nothing else."""
    if status not in REVIEW_STATUSES or (note is not None and len(note) > MAX_NOTE):
        raise IndexStoreError(INVALID_DECISION, f"status must be one of {', '.join(REVIEW_STATUSES)}; note at most {MAX_NOTE} characters")
    flag = connection.execute(
        "SELECT evidence FROM review_flags WHERE project_id = ? AND kind = ? AND state = ?", (project_id, kind, FLAG_OPEN)
    ).fetchone()
    if flag is None:
        raise IndexStoreError(CANDIDATE_NOT_FOUND, "no open candidate of that kind for that project")
    connection.execute(
        "INSERT INTO review_decisions (project_id, kind, status, evidence, note, decided_at) VALUES (?, ?, ?, ?, ?, ?)"
        " ON CONFLICT (project_id, kind) DO UPDATE SET status = excluded.status, evidence = excluded.evidence,"
        " note = excluded.note, decided_at = excluded.decided_at",
        (project_id, kind, status, flag["evidence"], note, now.isoformat()),
    )


def list_candidates(connection: sqlite3.Connection, review: str | None = None) -> list[dict]:
    """Open flags with their rule, criteria, evidence, and the reviewer's decision while it still holds."""
    rows = connection.execute(
        "SELECT f.project_id, p.display_name, f.kind, f.evidence, d.status, d.evidence AS decided_evidence,"
        " d.note, d.decided_at FROM review_flags f JOIN projects p USING (project_id)"
        " LEFT JOIN review_decisions d ON d.project_id = f.project_id AND d.kind = f.kind"
        " WHERE f.state = ? ORDER BY f.project_id, f.kind",
        (FLAG_OPEN,),
    ).fetchall()
    candidates = []
    for row in rows:
        holds = row["status"] is not None and json.loads(row["decided_evidence"]) == json.loads(row["evidence"])
        rule, confidence, criteria = RULES[row["kind"]]
        candidates.append({
            "project_id": row["project_id"],
            "display_name": row["display_name"],
            "kind": row["kind"],
            "rule": rule,
            "confidence": confidence,
            "criteria": criteria,
            "evidence": row["evidence"],
            "review_status": row["status"] if holds else REVIEW_OPEN,
            "note": row["note"] if holds else None,
            "decided_at": row["decided_at"] if holds else None,
        })
    return [c for c in candidates if review is None or c["review_status"] == review]
