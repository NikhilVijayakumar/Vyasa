# Specifications: be-profile-v2 (project-profile)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-profile-v2`
- **Purpose:** Read a comprehensive version 2 profile field by field and describe it to writers.
- **Related proposal:** `proposal.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/profile-schema-v2-full-template.md`

## 2. Capability: project-profile

### Purpose

Let a repository declare, in a predefined and validated shape, what a project is and where its documents are.

### Scope

Validation and description of the profile. Reading the file is unchanged.

## ADDED Requirements

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

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
