-- What a repository declares about itself, as read from its profile on the last scan that reached the checkout.
CREATE TABLE checkout_profiles (
    checkout_id INTEGER PRIMARY KEY REFERENCES checkouts (checkout_id),
    status TEXT NOT NULL CHECK (status IN ('valid', 'invalid', 'unsupported', 'unreadable', 'absent')),
    fields TEXT NOT NULL DEFAULT '{}',
    problems TEXT NOT NULL DEFAULT '[]',
    read_at TEXT NOT NULL,
    run_id TEXT REFERENCES scan_runs (run_id)
);
