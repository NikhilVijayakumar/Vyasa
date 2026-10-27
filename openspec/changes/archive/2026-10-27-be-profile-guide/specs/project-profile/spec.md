# Specifications: be-profile-guide

## 1. Specification Overview

- **OpenSpec Change ID:** `be-profile-guide`
- **Purpose:** Tell an agent exactly how to write a valid project profile.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/canonical-profile-and-draft.md`
- **Team focus:** Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: project-profile

### Purpose

Keep the documented profile rules and the enforced rules identical.

### Scope

The generated guide and the committed JSON Schema.

## ADDED Requirements

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
