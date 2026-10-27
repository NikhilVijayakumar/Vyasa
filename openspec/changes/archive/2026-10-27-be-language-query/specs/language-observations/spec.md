# Specifications: be-language-query (language-observations)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-language-query`
- **Purpose:** Store language observations during the scan.
- **Related proposal:** `proposal.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/language-observations-in-index.md`

## 2. Capability: language-observations

### Purpose

Keep what the scan learned about the languages of each checkout, honestly, across rescans.

### Scope

Storage during a scan. Reading is specified in the `project-query` capability.

## ADDED Requirements

### Requirement: Scan stores an observation per checkout

The system SHALL, during a scan, detect languages for each eligible checkout and store one observation holding the run, the time, the completeness, the data version, and one row per language and status.

#### Scenario: Scan stores languages

- **GIVEN** a workspace with a Python repository
- **WHEN** a scan completes
- **THEN** the checkout has an observation with Python as `files_detected`

#### Scenario: Declared language stored

- **GIVEN** a repository with a `Cargo.toml` and no Rust files
- **WHEN** a scan completes
- **THEN** the observation has Rust as `declared` and no `files_detected` row for Rust

### Requirement: Current and previous observation are kept

The system SHALL keep, per checkout, the current observation and the one before it, and SHALL discard older ones.

#### Scenario: Third scan

- **GIVEN** a checkout scanned three times
- **WHEN** the third scan completes
- **THEN** only the second and third observations exist

#### Scenario: Unchanged tree

- **GIVEN** a tree that has not changed
- **WHEN** it is scanned again
- **THEN** the current observation is the new one with the same languages

### Requirement: Partial rescan is current and flagged

The system SHALL make the newest observation current even when partial, record the stopping bound, and keep the previous observation, and SHALL NOT remove language rows to represent a language that was not found.

#### Scenario: Entry cap on rescan

- **GIVEN** a complete observation listing Python
- **WHEN** a rescan stops at the entry cap and finds no Python
- **THEN** the current observation is partial naming the entry cap
- **AND** the previous complete observation still lists Python

### Requirement: Detection failure is isolated

The system SHALL store a failed observation with a safe reason when detection raises for a checkout, SHALL continue with the other checkouts, and SHALL mark the run partial.

#### Scenario: One checkout fails

- **GIVEN** detection raises for one of two checkouts
- **WHEN** the scan runs
- **THEN** the failing checkout has a failed observation with no language rows
- **AND** the other checkout has its observation and the run is partial

### Requirement: Inaccessible and missing checkouts keep their last observation

The system SHALL NOT create or delete observations for a checkout that was not reached in the scan.

#### Scenario: Checkout not reached

- **GIVEN** a checkout with an observation that is missing in a later scan
- **WHEN** the scan completes
- **THEN** its observations are unchanged

### Requirement: Migration preserves the index

The system SHALL add the language tables in a migration that keeps every existing row, and a checkout with no observation SHALL read as never observed.

#### Scenario: Upgrade

- **GIVEN** an index at the previous version with projects
- **WHEN** it is opened for writing
- **THEN** it upgrades, the projects are unchanged, and no checkout has an observation

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
