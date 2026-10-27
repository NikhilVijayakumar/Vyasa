-- A reviewer's decisions are local, human-owned state. No export or synchronization reads this table.
CREATE TABLE review_decisions (
    project_id TEXT NOT NULL REFERENCES projects (project_id),
    kind TEXT NOT NULL CHECK (kind IN ('duplicate_checkout', 'identity_unresolved')),
    status TEXT NOT NULL CHECK (status IN ('open', 'dismissed', 'confirmed')),
    evidence TEXT NOT NULL,
    note TEXT CHECK (note IS NULL OR length(note) <= 500),
    decided_at TEXT NOT NULL,
    PRIMARY KEY (project_id, kind)
);
