# Specifications: be-project-markers (project-query)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-project-markers`
- **Purpose:** Filter search by marker and show markers in project details.
- **Related proposal:** `proposal.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/project-marker-observations.md`

## 2. Capability: project-query

### Purpose

Let an agent find projects by marker and read a checkout's markers without any filesystem access.

### Scope

`search_projects` and `get_project`. Existing parameters and fields are unchanged.

## ADDED Requirements

### Requirement: Search filters by marker

The system SHALL accept `marker` as a name or list of names from the eight marker names, and `marker_state` as `detected` (the default) or `not_detected`. With `detected` it SHALL return the projects having an active checkout whose current observation has any requested marker detected. With `not_detected` it SHALL return the projects having an active checkout whose current observation is complete, was assessed, and lacks any requested marker. Several names combine with OR; the filter combines with the others by AND.

#### Scenario: Detected

- **GIVEN** one project with tests and one without
- **WHEN** an agent searches with marker tests
- **THEN** only the project with tests is returned

#### Scenario: Not detected after a complete assessment

- **GIVEN** a complete observation without a README
- **WHEN** an agent searches with marker readme and marker_state not_detected
- **THEN** the project is returned

#### Scenario: Partial observation is not absence

- **GIVEN** a partial observation without a README
- **WHEN** an agent searches with marker readme and marker_state not_detected, and again with marker_state detected
- **THEN** the project is returned for neither

#### Scenario: Not assessed matches neither state

- **GIVEN** a checkout observed before marker detection existed
- **WHEN** an agent searches with marker readme in either state
- **THEN** the project is returned for neither

#### Scenario: Several names

- **GIVEN** projects with docs, with tests, and with neither
- **WHEN** an agent searches with markers docs and tests
- **THEN** the projects with docs or tests are returned

#### Scenario: Any active checkout

- **GIVEN** a project with two active checkouts, only one having tests
- **WHEN** an agent searches with marker tests
- **THEN** the project is returned

#### Scenario: Missing checkout does not match

- **GIVEN** a project whose only checkout with tests is missing
- **WHEN** an agent searches with marker tests
- **THEN** the project is not returned

#### Scenario: Combined with another filter

- **GIVEN** a Python project with tests and a Rust project with tests
- **WHEN** an agent searches with marker tests and language Python
- **THEN** only the Python project is returned

#### Scenario: Unknown name or state

- **GIVEN** an indexed workspace
- **WHEN** an agent searches with marker readmee, and again with marker_state maybe
- **THEN** each request fails with `INVALID_INPUT` listing the allowed values

### Requirement: Details list markers per checkout

The system SHALL return, for each checkout in `get_project`, a `markers` object holding its assessment status (`complete`, `partial` with its bound, or `not_assessed`), the rules version, the observed time, and for each marker its state (`detected`, `not_detected`, `unknown`) with, when detected, the total, the rules matched, and the capped repository-relative paths with their scope where it applies, and SHALL NOT combine checkouts.

#### Scenario: Markers per checkout

- **GIVEN** a project with two checkouts with different markers
- **WHEN** the details are read
- **THEN** each checkout lists its own markers

#### Scenario: Not assessed

- **GIVEN** a checkout observed before marker detection existed, and a checkout whose detection failed
- **WHEN** the details are read
- **THEN** each reports status `not_assessed` and no marker states

#### Scenario: Partial shows unknown

- **GIVEN** a partial observation that found `tests` only
- **WHEN** the details are read
- **THEN** `tests` is detected and every other marker is `unknown`

#### Scenario: Evidence shown

- **GIVEN** a detected `agent_instructions` marker with a nested file
- **WHEN** the details are read
- **THEN** the paths and their scopes, the total, and the matching rules are given

#### Scenario: Missing checkout keeps its markers

- **GIVEN** a missing checkout with an earlier observation
- **WHEN** the details are read
- **THEN** its markers show the last observation and the checkout state is `missing`

### Requirement: Marker queries do not touch the filesystem

The system SHALL answer the marker filter and details from stored observations only.

#### Scenario: Files changed since the scan

- **GIVEN** an indexed project whose files changed after the scan
- **WHEN** an agent searches or reads details
- **THEN** the stored markers and their observed time are returned

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
