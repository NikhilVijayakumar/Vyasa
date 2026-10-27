"""Index states, error codes, and freshness. Nothing here touches the filesystem or the database."""

from __future__ import annotations

from datetime import datetime, timedelta

ACTIVE = "active"
MISSING = "missing"
INACCESSIBLE = "inaccessible"
PROJECT_STATES = (ACTIVE, MISSING, INACCESSIBLE)

RUNNING = "running"
COMPLETED = "completed"
PARTIAL = "partial"
FAILED = "failed"
INTERRUPTED = "interrupted"
RUN_STATUSES = (RUNNING, COMPLETED, PARTIAL, FAILED, INTERRUPTED)

DUPLICATE_CHECKOUT = "duplicate_checkout"
IDENTITY_UNRESOLVED = "identity_unresolved"
FLAG_OPEN = "open"
FLAG_CLEARED = "cleared"

REVIEW_OPEN = "open"
DISMISSED = "dismissed"
CONFIRMED = "confirmed"
REVIEW_STATUSES = (REVIEW_OPEN, DISMISSED, CONFIRMED)
MAX_NOTE = 500

# Each flag kind: rule id, confidence tier, and the criteria in plain words.
RULES: dict[str, tuple[str, str, str]] = {
    DUPLICATE_CHECKOUT: (
        "same_remote_identity",
        "high",
        "More than one checkout of this project is active, and they share a remote identity.",
    ),
    IDENTITY_UNRESOLVED: (
        "path_remote_conflict",
        "low",
        "A checkout's path belongs to this project, but its remote identity belongs to another.",
    ),
}

CURRENT = "current"
STALE = "stale"
UNKNOWN = "unknown"

FRESHNESS_WINDOW = timedelta(hours=24)
LOCK_TIMEOUT = timedelta(seconds=60)

SCHEMA_TOO_NEW = "INDEX_SCHEMA_TOO_NEW"
MIGRATION_FAILED = "INDEX_MIGRATION_FAILED"
UNAVAILABLE = "INDEX_UNAVAILABLE"
IN_PROGRESS = "OPERATION_IN_PROGRESS"
CANDIDATE_NOT_FOUND = "CANDIDATE_NOT_FOUND"
INVALID_DECISION = "INVALID_DECISION"
INVALID_INPUT = "INVALID_INPUT"
INVALID_CURSOR = "INVALID_CURSOR"
PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"


class IndexStoreError(Exception):
    """A controlled index failure. ``code`` is the stable error code."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


def freshness(latest_status: str | None, latest_finished: datetime | None, now: datetime, window: timedelta = FRESHNESS_WINDOW) -> str:
    """How current the index is, from its latest run alone."""
    if latest_status is None:
        return UNKNOWN
    if latest_status != COMPLETED or latest_finished is None:
        return PARTIAL
    return CURRENT if now - latest_finished <= window else STALE
