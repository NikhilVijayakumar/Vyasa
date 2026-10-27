-- What the scan found about the languages of a checkout. The two newest observations per checkout are kept.
CREATE TABLE language_observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkout_id INTEGER NOT NULL REFERENCES checkouts (checkout_id),
    run_id TEXT NOT NULL REFERENCES scan_runs (run_id),
    observed_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('complete', 'partial', 'failed')),
    stopped_by TEXT CHECK (stopped_by IS NULL OR stopped_by IN ('depth', 'entries', 'time', 'unreadable')),
    types_version INTEGER NOT NULL,
    reason TEXT CHECK (reason IS NULL OR reason IN ('detection_error')),
    duration_ms INTEGER NOT NULL DEFAULT 0,
    CHECK ((status = 'partial') = (stopped_by IS NOT NULL)),
    CHECK ((status = 'failed') = (reason IS NOT NULL))
);
CREATE INDEX language_observations_checkout ON language_observations (checkout_id, observation_id);

CREATE TABLE checkout_languages (
    observation_id INTEGER NOT NULL REFERENCES language_observations (observation_id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('files_detected', 'declared')),
    files INTEGER CHECK (files IS NULL OR files > 0),
    PRIMARY KEY (observation_id, label, status)
);
CREATE INDEX checkout_languages_label ON checkout_languages (label, status);
