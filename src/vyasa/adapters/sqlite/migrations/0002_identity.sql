ALTER TABLE projects ADD COLUMN identity_status TEXT NOT NULL DEFAULT 'provisional'
    CHECK (identity_status IN ('resolved', 'provisional', 'ambiguous'));
ALTER TABLE projects ADD COLUMN identity_source TEXT NOT NULL DEFAULT 'path'
    CHECK (identity_source IN ('remote', 'path'));

CREATE TABLE project_aliases (
    alias_kind TEXT NOT NULL CHECK (alias_kind IN ('remote')),
    alias_value TEXT NOT NULL,
    project_id TEXT NOT NULL REFERENCES projects (project_id),
    first_seen_at TEXT NOT NULL,
    PRIMARY KEY (alias_kind, alias_value)
);

CREATE INDEX project_aliases_project ON project_aliases (project_id);

CREATE TABLE identity_events (
    event_id INTEGER PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects (project_id),
    kind TEXT NOT NULL CHECK (kind IN ('created', 'alias_added', 'identity_conflict')),
    detail TEXT NOT NULL DEFAULT '{}',
    run_id TEXT REFERENCES scan_runs (run_id),
    at TEXT NOT NULL
);

CREATE INDEX identity_events_project ON identity_events (project_id);

-- The earliest checkout stored with a remote identity owns that alias.
INSERT OR IGNORE INTO project_aliases (alias_kind, alias_value, project_id, first_seen_at)
SELECT 'remote', remote_identity, project_id, first_seen_at
FROM checkouts
WHERE remote_identity IS NOT NULL
ORDER BY checkout_id;

UPDATE projects SET identity_status = 'resolved', identity_source = 'remote'
WHERE project_id IN (SELECT project_id FROM project_aliases);
