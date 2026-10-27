CREATE TABLE scan_runs (
    run_id TEXT PRIMARY KEY,
    root TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'partial', 'failed', 'interrupted')),
    tool_version TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    counts TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('active', 'missing', 'inaccessible')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);

CREATE TABLE checkouts (
    checkout_id INTEGER PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects (project_id),
    path TEXT NOT NULL,
    path_key TEXT NOT NULL UNIQUE,
    root TEXT NOT NULL,
    kind TEXT,
    markers TEXT NOT NULL DEFAULT '[]',
    git TEXT,
    remote_provider TEXT,
    remote_host TEXT,
    remote_identity TEXT,
    remote_status TEXT,
    state TEXT NOT NULL CHECK (state IN ('active', 'missing', 'inaccessible')),
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    last_run_id TEXT REFERENCES scan_runs (run_id)
);

CREATE INDEX checkouts_root ON checkouts (root);

CREATE TABLE index_lock (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    owner TEXT NOT NULL,
    run_id TEXT NOT NULL,
    heartbeat_at TEXT NOT NULL
);
