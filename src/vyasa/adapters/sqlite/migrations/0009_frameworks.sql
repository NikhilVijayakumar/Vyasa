-- What the scan learned from the supported root manifests of a checkout, stored with the observation of the same walk.
-- A null frameworks_version means the observation was not assessed for frameworks: one made before this migration,
-- or a failed one. It never means "no frameworks".
ALTER TABLE language_observations ADD COLUMN frameworks_version INTEGER CHECK (frameworks_version IS NULL OR frameworks_version >= 1);

-- One row per supported manifest read at the checkout root. Only a fixed status and reason are kept for a manifest
-- that could not be used; never any of its text.
CREATE TABLE checkout_manifests (
    observation_id INTEGER NOT NULL REFERENCES language_observations (observation_id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    ecosystem TEXT NOT NULL CHECK (ecosystem IN ('python', 'javascript', 'rust', 'go')),
    status TEXT NOT NULL CHECK (status IN ('parsed', 'malformed', 'too_large', 'unreadable')),
    reason TEXT CHECK (reason IS NULL OR reason IN ('syntax', 'encoding', 'structure', 'too_deep', 'link', 'not_file', 'io')),
    total_dependencies INTEGER NOT NULL CHECK (total_dependencies >= 0),
    skipped INTEGER NOT NULL CHECK (skipped >= 0),
    workspace INTEGER NOT NULL CHECK (workspace IN (0, 1)),
    PRIMARY KEY (observation_id, path)
);

-- Direct dependencies of a parsed manifest, at most 200 per manifest.
CREATE TABLE checkout_dependencies (
    observation_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    name TEXT NOT NULL,
    constraint_text TEXT,
    scope TEXT NOT NULL CHECK (scope IN ('runtime', 'dev', 'optional', 'build')),
    PRIMARY KEY (observation_id, path, name, scope),
    FOREIGN KEY (observation_id, path) REFERENCES checkout_manifests (observation_id, path) ON DELETE CASCADE
);

-- Technologies mapped through the registry: the scopes they were declared in and the manifests that declared them.
CREATE TABLE checkout_technologies (
    observation_id INTEGER NOT NULL REFERENCES language_observations (observation_id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    scopes TEXT NOT NULL,
    manifests TEXT NOT NULL,
    PRIMARY KEY (observation_id, key)
);
CREATE INDEX checkout_technologies_key ON checkout_technologies (key);

-- Supported manifests found below the root: counted, never parsed.
CREATE TABLE checkout_nested_manifests (
    observation_id INTEGER NOT NULL REFERENCES language_observations (observation_id) ON DELETE CASCADE,
    ecosystem TEXT NOT NULL CHECK (ecosystem IN ('python', 'javascript', 'rust', 'go')),
    count INTEGER NOT NULL CHECK (count > 0),
    PRIMARY KEY (observation_id, ecosystem)
);
