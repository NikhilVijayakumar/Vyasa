-- The package name a parsed root manifest declares (project name, package name, crate name, module path), stored
-- normalized for its ecosystem. Null when the manifest declares none or was not parsed, and for observations made
-- before this migration: it never means "this project publishes no package".
ALTER TABLE checkout_manifests ADD COLUMN declared_name TEXT CHECK (declared_name IS NULL OR length(declared_name) BETWEEN 1 AND 214);
CREATE INDEX checkout_manifests_declared_name ON checkout_manifests (ecosystem, declared_name);

-- 1 when the observation recorded declared names, so a null name on its manifests means "declares none". Null for
-- observations made before this migration: their manifests may well declare a name that was not kept.
ALTER TABLE language_observations ADD COLUMN names_recorded INTEGER CHECK (names_recorded IS NULL OR names_recorded = 1);
