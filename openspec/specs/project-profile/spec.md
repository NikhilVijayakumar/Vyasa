# project-profile Specification

## Purpose
TBD - created by archiving change be-profile-read. Update Purpose after archive.

## Requirements

### Requirement: The profile is read safely

The system SHALL read `.vyasa/project-profile.toml` at the root of each eligible project as text, at most 64 KiB, only when `.vyasa` is a real directory and the file a real file, SHALL NOT run anything from it, and SHALL NOT let a failure stop the scan.

#### Scenario: Valid file

- **GIVEN** a project with a well-formed profile
- **WHEN** the scan runs
- **THEN** the profile status is `valid`

#### Scenario: No file

- **GIVEN** a project with no profile
- **WHEN** the scan runs
- **THEN** the status is `absent` and nothing is flagged

#### Scenario: Link, oversize, or malformed

- **GIVEN** a profile that is a link, over 64 KiB, or not valid TOML
- **WHEN** the scan runs
- **THEN** the status is `unreadable` with a reason and the rest of the scan completes

#### Scenario: Repository unchanged

- **GIVEN** a repository with a profile
- **WHEN** the scan runs
- **THEN** every file in it is byte-identical afterwards

### Requirement: Fields are validated one by one

The system SHALL validate each field of schema version 1 on its own, keep the valid ones, and report each invalid one with its field name and reason, and SHALL mark a missing or unsupported `schema_version` as `unsupported` with no fields used.

#### Scenario: One bad field

- **GIVEN** a profile with a valid purpose and an unknown lifecycle value
- **WHEN** it is read
- **THEN** the status is `invalid`, the purpose is kept, and a problem names `lifecycle`

#### Scenario: Unsupported version

- **GIVEN** a profile with `schema_version = 2` or none
- **WHEN** it is read
- **THEN** the status is `unsupported` and no field is kept

#### Scenario: Limits

- **GIVEN** a purpose over 500 characters, a list over 20 entries, or an item over its length cap
- **WHEN** it is read
- **THEN** that field is reported invalid and not kept

#### Scenario: Entry point must be relative

- **GIVEN** `documentation.entry_point` that is absolute, contains `..`, or has a drive letter
- **WHEN** it is read
- **THEN** that field is invalid

#### Scenario: Unknown fields

- **GIVEN** a field not in the schema
- **WHEN** it is read
- **THEN** it is reported as unknown and ignored, and the status is `invalid`

#### Scenario: Control characters

- **GIVEN** string values containing control characters
- **WHEN** they are read
- **THEN** the control characters are removed before the value is kept

### Requirement: Declared values keep their source

The system SHALL store the valid fields and problems with each checkout and SHALL present each kept value as `declared` with the profile path as its source.

#### Scenario: Stored

- **GIVEN** a scanned project with a valid profile
- **WHEN** the index is read after a restart
- **THEN** the declared values and status are present

#### Scenario: Profile edited

- **GIVEN** a stored profile that is edited and rescanned
- **WHEN** the scan completes
- **THEN** the new values replace the old for that checkout

#### Scenario: Profile removed

- **GIVEN** a stored profile that is deleted and rescanned
- **WHEN** the scan completes
- **THEN** the status is `absent` and no stale values are shown

### Requirement: Project details show the profile

The system SHALL include in `get_project` a `profile` object with its status, its `declared` values (each with value and status `declared`), its problems, and its source, choosing among a project's checkouts the active one first and then the earliest seen that has a readable profile.

#### Scenario: Declared values shown

- **GIVEN** a project with a valid profile
- **WHEN** `get_project` is called
- **THEN** `profile.status` is `valid` and `profile.declared.purpose` is `{"value": ..., "status": "declared"}`

#### Scenario: No profile

- **GIVEN** a project with no profile
- **WHEN** `get_project` is called
- **THEN** `profile.status` is `absent` and `declared` is empty

#### Scenario: Invalid profile

- **GIVEN** a project with an invalid field
- **WHEN** `get_project` is called
- **THEN** the valid fields and the problems are both present

#### Scenario: Declared name does not replace the display name

- **GIVEN** a profile with a `name`
- **WHEN** `get_project` is called
- **THEN** `display_name` is unchanged and the declared name appears under `profile.declared`

### Requirement: The guide is generated from the validation rules

The system SHALL produce a guide containing the profile path, format, schema version, every field with its type, whether it is required, its limits and allowed values, a complete example, and rules for the writer, all derived from the same constants the validator uses.

#### Scenario: Example is valid

- **GIVEN** the guide
- **WHEN** its example is parsed as TOML and validated
- **THEN** the status is `valid` and every field in the guide appears in it

#### Scenario: Limits follow the rules

- **GIVEN** the guide
- **WHEN** a field's limit or allowed values are read
- **THEN** they equal the validator's constants

#### Scenario: Writer rules

- **GIVEN** the guide
- **WHEN** its rules are read
- **THEN** they tell the writer to omit unknown fields, describe only what the repository shows, include no credentials or absolute paths, write the file once at the stated path, and note that Vyasa reads it on the next scan and never writes it

### Requirement: A JSON Schema is committed

The system SHALL commit `schemas/project-profile.v1.json` and a test SHALL fail when it differs from the schema generated from the validation rules.

#### Scenario: Schema matches

- **GIVEN** the committed file
- **WHEN** it is compared with the generated schema
- **THEN** they are equal

#### Scenario: Schema accepts the example

- **GIVEN** the generated schema's field names, types, and bounds
- **WHEN** the guide's example is checked against them
- **THEN** it conforms
