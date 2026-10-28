-- The project report a repository declares in .vyasa/project-report.md, as read on the last scan that reached the
-- checkout. status is the latest read; sections come from the last read that succeeded (kept_hash, kept_at), so an
-- unreadable or invalid read does not erase earlier text. The limits applied are stored so the template can show them.
CREATE TABLE report_observations (
    checkout_id INTEGER PRIMARY KEY REFERENCES checkouts (checkout_id),
    status TEXT NOT NULL CHECK (status IN ('present', 'not_present', 'unreadable', 'invalid')),
    reason TEXT,
    content_hash TEXT,
    scanned_at TEXT NOT NULL,
    max_file_bytes INTEGER NOT NULL,
    max_section_bytes INTEGER NOT NULL,
    dropped_json TEXT NOT NULL DEFAULT '[]',
    kept_hash TEXT,
    kept_at TEXT,
    run_id TEXT REFERENCES scan_runs (run_id)
);

CREATE TABLE report_sections (
    checkout_id INTEGER NOT NULL REFERENCES checkouts (checkout_id),
    name TEXT NOT NULL,
    text TEXT NOT NULL,
    size INTEGER NOT NULL,
    position INTEGER NOT NULL,
    PRIMARY KEY (checkout_id, name)
);
