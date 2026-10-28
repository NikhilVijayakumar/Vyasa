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

### Requirement: A version 2 profile is read field by field

The system SHALL read a profile whose `schema_version` is 2, SHALL validate every field on its own against the version 2 definitions, SHALL keep the valid fields under dotted names such as `project.summary`, and SHALL drop and report each invalid field without affecting the others.

#### Scenario: Valid profile

- **GIVEN** a version 2 profile with `project`, `project.business`, `project.scope`, and `project.architecture` tables
- **WHEN** it is read
- **THEN** its status is `valid` and the values are stored under dotted names

#### Scenario: One invalid field

- **GIVEN** a version 2 profile with a lifecycle status outside the allowed values and a valid summary
- **WHEN** it is read
- **THEN** its status is `invalid`, the summary is kept, and the lifecycle problem is reported

#### Scenario: Empty profile

- **GIVEN** a version 2 profile containing only `schema_version`
- **WHEN** it is read
- **THEN** its status is `valid` and no field is stored

#### Scenario: Nested tables

- **GIVEN** values in `project.engineering.security` and `project.engineering.operations`
- **WHEN** it is read
- **THEN** they are stored as `project.engineering.security.classification` and `project.engineering.operations.runbook`

### Requirement: Version 1 profiles keep working

The system SHALL read a profile whose `schema_version` is 1 exactly as before this change, and SHALL read a declared value from either version through one accessor.

#### Scenario: Version 1 unchanged

- **GIVEN** a valid version 1 profile
- **WHEN** it is read
- **THEN** the stored fields are the same names and values as before

#### Scenario: Accessor reads either version

- **GIVEN** a version 1 profile declaring `name` and a version 2 profile declaring `project.name`
- **WHEN** the accessor is asked for the project name
- **THEN** it returns the declared name from each

### Requirement: Unknown fields and versions are reported

The system SHALL report each field that is not in the version 2 definitions as unknown and drop it, and SHALL report a `schema_version` that is neither 1 nor 2 as unsupported without reading the profile.

#### Scenario: Unknown field

- **GIVEN** a version 2 profile with a field named `project.priority`
- **WHEN** it is read
- **THEN** the field is reported unknown and not stored

#### Scenario: Unsupported version

- **GIVEN** a profile with `schema_version = 3`
- **WHEN** it is read
- **THEN** its status is `unsupported` and no field is stored

#### Scenario: Wrong shape of a table

- **GIVEN** a version 2 profile where `project.business` is text
- **WHEN** it is read
- **THEN** the table is reported as invalid and the rest is kept

### Requirement: Declared ids are labels only

The system SHALL accept `project.id` and the relationship ids as labels of letters, digits, and `._:-` up to 100 characters, SHALL store them as declared text, and SHALL NOT use them to identify, match, merge, or split projects.

#### Scenario: Label accepted

- **GIVEN** a version 2 profile with `project.id = "billing-api"`
- **WHEN** it is read
- **THEN** `project.id` is stored as declared text

#### Scenario: Label rejected

- **GIVEN** an id containing a slash, a space, or a URL
- **WHEN** it is read
- **THEN** the id is dropped and reported

#### Scenario: Identity unaffected

- **GIVEN** two repositories whose profiles declare the same `project.id`
- **WHEN** both are scanned
- **THEN** they remain separate projects

### Requirement: Text, contacts, and paths are safe

The system SHALL strip control characters from text, SHALL reject text containing a URL that carries credentials, SHALL reject a contact reference that is an email address or a URL, and SHALL accept a path only if it is relative to the repository, uses no `..` segment, has no drive letter or URL scheme, and is at most 200 characters.

#### Scenario: Credentials in a URL

- **GIVEN** a description containing `https://user:secret@example.com/x`
- **WHEN** it is read
- **THEN** the description is dropped and reported and the secret is not stored

#### Scenario: Email as a contact

- **GIVEN** `project.owner.contact_reference = "dev@example.com"`
- **WHEN** it is read
- **THEN** the field is dropped and reported

#### Scenario: Absolute or parent path

- **GIVEN** a documentation path `/etc/passwd`, `C:\secrets`, and `../outside`
- **WHEN** it is read
- **THEN** each is dropped and reported

#### Scenario: Control characters

- **GIVEN** a summary containing a control character
- **WHEN** it is read
- **THEN** the stored summary has the character removed

#### Scenario: Plain URL is allowed in text

- **GIVEN** a description mentioning `https://example.com/docs` with no credentials
- **WHEN** it is read
- **THEN** the description is kept

### Requirement: Lists, tables, and text are bounded

The system SHALL enforce the maximum text length of each field, the maximum item count and item length of each list, and the maximum row count of each list of tables, SHALL drop a field that exceeds a bound, and SHALL remove duplicate list items.

#### Scenario: Too long

- **GIVEN** a summary of 201 characters
- **WHEN** it is read
- **THEN** the summary is dropped and reported with its limit

#### Scenario: Too many rows

- **GIVEN** 40 capabilities
- **WHEN** it is read
- **THEN** the capabilities field is dropped and reported

#### Scenario: Duplicates

- **GIVEN** a list with the same item twice
- **WHEN** it is read
- **THEN** the item is stored once

#### Scenario: Row with an unknown key

- **GIVEN** a capability table with a key that is not defined
- **WHEN** it is read
- **THEN** the row is dropped and reported and the other rows are kept

### Requirement: Enumerations, dates, and commits have fixed forms

The system SHALL accept an enumerated field only with one of its documented values, a date only as a calendar date, a tri-state field only as `true`, `false`, or `"unknown"`, and a commit reference only as 7 to 64 hexadecimal characters.

#### Scenario: Enumeration

- **GIVEN** `project.engineering.security.classification = "secret"`
- **WHEN** it is read
- **THEN** the field is dropped and reported with the allowed values

#### Scenario: Date

- **GIVEN** `created_date = 2026-10-28` as a TOML date and another as the text `yesterday`
- **WHEN** it is read
- **THEN** the first is stored as `2026-10-28` and the second is dropped and reported

#### Scenario: Tri-state

- **GIVEN** `project.engineering.openspec.enabled` set to `true`, to `"unknown"`, and to `"yes"`
- **WHEN** each is read
- **THEN** the first two are stored and the third is dropped and reported

#### Scenario: Commit reference

- **GIVEN** `last_verified_commit` set to `"a1b2c3d"` and to `"not-a-commit"`
- **WHEN** each is read
- **THEN** the first is stored and the second is dropped and reported

### Requirement: The guide and the JSON Schema describe version 2

The system SHALL generate the writer guide and the JSON Schema from the same definitions as the validation, SHALL state in the guide that version 1 is still read, SHALL include a complete version 2 example that validates, and SHALL commit the version 2 schema file.

#### Scenario: Guide lists every field

- **GIVEN** the guide is requested
- **WHEN** it is returned
- **THEN** it lists every version 2 field with type, limits, and allowed values and states that version 1 is still read

#### Scenario: Example validates

- **GIVEN** the example in the guide
- **WHEN** it is parsed and validated
- **THEN** its status is `valid` with no problems

#### Scenario: Schema file matches

- **GIVEN** the committed `schemas/project-profile.v2.json`
- **WHEN** it is compared with the generated schema
- **THEN** they are equal

#### Scenario: Every stored name has a definition

- **GIVEN** every field the validator can store
- **WHEN** the guide and the schema are inspected
- **THEN** each has a description in both

---
