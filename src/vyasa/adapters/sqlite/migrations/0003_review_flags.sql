CREATE TABLE review_flags (
    flag_id INTEGER PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects (project_id),
    kind TEXT NOT NULL CHECK (kind IN ('duplicate_checkout', 'identity_unresolved')),
    state TEXT NOT NULL CHECK (state IN ('open', 'cleared')),
    evidence TEXT NOT NULL,
    raised_at TEXT NOT NULL,
    cleared_at TEXT,
    run_id TEXT REFERENCES scan_runs (run_id),
    UNIQUE (project_id, kind)
);

-- SQLite cannot widen a CHECK in place: rebuild the events table and keep every row.
CREATE TABLE identity_events_new (
    event_id INTEGER PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects (project_id),
    kind TEXT NOT NULL CHECK (kind IN ('created', 'alias_added', 'identity_conflict', 'flagged', 'resolved')),
    detail TEXT NOT NULL DEFAULT '{}',
    run_id TEXT REFERENCES scan_runs (run_id),
    at TEXT NOT NULL
);
INSERT INTO identity_events_new (event_id, project_id, kind, detail, run_id, at)
SELECT event_id, project_id, kind, detail, run_id, at FROM identity_events;
DROP TABLE identity_events;
ALTER TABLE identity_events_new RENAME TO identity_events;
CREATE INDEX identity_events_project ON identity_events (project_id);

-- Duplicates already present. Conflicts are only visible at scan time, so the next scan raises them.
INSERT INTO review_flags (project_id, kind, state, evidence, raised_at)
SELECT c.project_id, 'duplicate_checkout', 'open',
       json_object(
           'rule', 'same_remote_identity',
           'aliases', json((SELECT COALESCE(json_group_array(alias_value), '[]')
                            FROM (SELECT alias_value FROM project_aliases a
                                  WHERE a.project_id = c.project_id ORDER BY alias_value))),
           'active_checkouts', COUNT(*)),
       strftime('%Y-%m-%dT%H:%M:%S+00:00', 'now')
FROM checkouts c
WHERE c.state = 'active'
GROUP BY c.project_id
HAVING COUNT(*) > 1;
