# Specifications: be-get-project-dependencies (framework-detection)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-get-project-dependencies`
- **Purpose:** Record the package name each parsed root manifest declares.
- **Related proposal:** `proposal.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/internal-dependencies-by-declared-package-name.md`

## 2. Capability: framework-detection

### Purpose

Keep the evidence needed to link a dependency to the project that publishes it.

### Scope

The parsers and the stored manifest rows. Existing detection behavior is unchanged.

## ADDED Requirements

### Requirement: Parsed manifests record the package name they declare

The system SHALL record, for each parsed root manifest, the package name it declares: the `[project]` name or the Poetry name in `pyproject.toml`, the `name` in `package.json`, the `[package]` name in `Cargo.toml`, and the `module` path in `go.mod`. A name SHALL be stored in the form used to match dependencies (normalized for its ecosystem), at most 214 characters, and SHALL be absent when the manifest declares none, declares a value that is not text, or is a `requirements*.txt` file. A manifest that is not parsed SHALL have no declared name. Reading the name SHALL NOT change the dependencies, scopes, skipped counts, or statuses reported.

#### Scenario: Name in each ecosystem

- **GIVEN** a `pyproject.toml` named Billing_API, a `package.json` named @acme/ui, a `Cargo.toml` package named ledger-core, and a `go.mod` with module example.com/acme/tool
- **WHEN** the manifests are parsed
- **THEN** the declared names are billing-api, @acme/ui, ledger-core, and example.com/acme/tool

#### Scenario: No name declared

- **GIVEN** a `pyproject.toml` without a project name and a `requirements.txt`
- **WHEN** they are parsed
- **THEN** no declared name is recorded and their dependencies are unchanged

#### Scenario: Name that is not text or too long

- **GIVEN** a `package.json` whose name is a number, and another whose name is 215 characters
- **WHEN** they are parsed
- **THEN** no declared name is recorded for either and the manifests are still reported as parsed

#### Scenario: Unparsed manifest

- **GIVEN** a malformed `package.json`
- **WHEN** the checkout is scanned
- **THEN** the manifest has status malformed and no declared name

#### Scenario: Stored with the observation

- **GIVEN** a scanned checkout with a named manifest
- **WHEN** the index is read
- **THEN** the manifest row carries the declared name and the observation is marked as having recorded names, while an observation made before the migration has neither
