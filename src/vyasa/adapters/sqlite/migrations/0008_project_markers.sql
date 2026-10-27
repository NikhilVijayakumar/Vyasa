-- Project markers found in the same walk as a language observation. A null markers_version means the observation
-- was not assessed for markers: one made before this migration, or a failed one. It never means "none found".
ALTER TABLE language_observations ADD COLUMN markers_version INTEGER CHECK (markers_version IS NULL OR markers_version >= 1);

-- One row per detected marker. A marker that was not detected has no row; whether that means "not detected" or
-- "unknown" depends on whether the observation was complete.
CREATE TABLE checkout_markers (
    observation_id INTEGER NOT NULL REFERENCES language_observations (observation_id) ON DELETE CASCADE,
    marker TEXT NOT NULL CHECK (marker IN ('readme', 'docs', 'agent_instructions', 'openspec_directory',
                                           'openspec_config', 'openspec_specs', 'openspec_changes', 'tests')),
    total INTEGER NOT NULL CHECK (total > 0),
    rules TEXT NOT NULL,
    paths TEXT NOT NULL,
    PRIMARY KEY (observation_id, marker)
);
CREATE INDEX checkout_markers_marker ON checkout_markers (marker);
