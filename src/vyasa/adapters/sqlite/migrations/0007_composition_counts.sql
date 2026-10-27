-- File counts of the same walk that produced a language observation. Null when the observation has no counts:
-- one made before this migration, or a failed one. Never zero for "not counted".
ALTER TABLE language_observations ADD COLUMN code_files INTEGER CHECK (code_files IS NULL OR code_files >= 0);
ALTER TABLE language_observations ADD COLUMN documentation_files INTEGER CHECK (documentation_files IS NULL OR documentation_files >= 0);
ALTER TABLE language_observations ADD COLUMN other_files INTEGER CHECK (other_files IS NULL OR other_files >= 0);
