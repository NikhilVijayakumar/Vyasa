CREATE TABLE scan_runs_new (
    run_id TEXT PRIMARY KEY,
    root TEXT,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'partial', 'failed', 'interrupted')),
    tool_version TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    counts TEXT NOT NULL DEFAULT '{}',
    scope_kind TEXT NOT NULL DEFAULT 'workspace' CHECK (scope_kind IN ('workspace', 'project')),
    scope_project_id TEXT REFERENCES projects(project_id),
    CHECK ((scope_kind = 'workspace' AND root IS NOT NULL AND length(root) > 0 AND scope_project_id IS NULL)
        OR (scope_kind = 'project' AND root IS NULL AND scope_project_id IS NOT NULL AND length(scope_project_id) > 0))
);
INSERT INTO scan_runs_new (run_id,root,status,tool_version,started_at,finished_at,counts)
SELECT run_id,root,status,tool_version,started_at,finished_at,counts FROM scan_runs;
DROP TABLE scan_runs;
ALTER TABLE scan_runs_new RENAME TO scan_runs;
CREATE TABLE scan_checkout_results (
    run_id TEXT NOT NULL REFERENCES scan_runs(run_id),
    checkout_id INTEGER NOT NULL REFERENCES checkouts(checkout_id),
    status TEXT NOT NULL CHECK (status IN ('completed', 'failed')),
    reason TEXT,
    PRIMARY KEY (run_id, checkout_id),
    CHECK ((status = 'completed' AND reason IS NULL) OR (status = 'failed' AND reason IS NOT NULL))
);
