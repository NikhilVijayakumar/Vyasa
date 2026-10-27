# Specifications: be-language-query (project-query)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-language-query`
- **Purpose:** Filter search by language and show languages in project details.
- **Related proposal:** `proposal.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/language-observations-in-index.md`

## 2. Capability: project-query

### Purpose

Let an agent find projects by language and read a project's languages without any filesystem access.

### Scope

`search_projects` and `get_project`. Existing parameters and fields are unchanged.

## ADDED Requirements

### Requirement: Search filters by language

The system SHALL accept `language` as a label or list of labels, compared case-insensitively against the shipped label set, and SHALL return the projects having a present checkout whose current observation lists any of them. Several labels combine with OR; the filter combines with the others by AND.

#### Scenario: Search by language

- **GIVEN** one project with Python files and one with only Rust files
- **WHEN** an agent searches with language Python
- **THEN** only the Python project is returned

#### Scenario: Several labels

- **GIVEN** projects using Python, Rust, and Go
- **WHEN** an agent searches with languages Python and Go
- **THEN** the Python and Go projects are returned

#### Scenario: Combined with another filter

- **GIVEN** an active Python project and a missing Python project
- **WHEN** an agent searches with language Python and state active
- **THEN** only the active project is returned

#### Scenario: Case-insensitive label

- **GIVEN** a project using Python
- **WHEN** an agent searches with language python
- **THEN** the project is returned

### Requirement: Search filters by language status

The system SHALL accept `language_status` as `files_detected` or `declared`, SHALL match only that status when given, and SHALL match either status when omitted. It SHALL report on each returned project which statuses matched.

#### Scenario: Declared only

- **GIVEN** a project with a `pyproject.toml` and no Python files
- **WHEN** an agent searches with language Python and status files_detected
- **THEN** the project is not returned

#### Scenario: Declared matches

- **GIVEN** the same project
- **WHEN** an agent searches with language Python and status declared
- **THEN** the project is returned with `declared` among its matched statuses

### Requirement: Unknown label or status is rejected

The system SHALL reject a language label not in the shipped set, or a status other than the two allowed, with `INVALID_INPUT` that lists the allowed values.

#### Scenario: Typo

- **GIVEN** an indexed workspace
- **WHEN** an agent searches with language Pyhton
- **THEN** the request fails with `INVALID_INPUT` listing the allowed labels

#### Scenario: Bad status

- **GIVEN** an indexed workspace
- **WHEN** an agent searches with language_status maybe
- **THEN** the request fails with `INVALID_INPUT` listing the allowed statuses

### Requirement: Any present checkout matches

The system SHALL match a project when any of its present checkouts matches and SHALL NOT match through a missing or inaccessible checkout.

#### Scenario: Two checkouts

- **GIVEN** a project with two active checkouts, only one containing Go files
- **WHEN** an agent searches with language Go
- **THEN** the project is returned

#### Scenario: Missing checkout

- **GIVEN** a project whose only Go checkout is missing
- **WHEN** an agent searches with language Go
- **THEN** the project is not returned

### Requirement: Partial observations match positives only

The system SHALL match on languages found in a partial current observation and SHALL NOT treat a language missing from it as absent.

#### Scenario: Partial observation

- **GIVEN** a partial current observation listing Rust
- **WHEN** an agent searches with language Rust
- **THEN** the project is returned

### Requirement: Details list languages per checkout

The system SHALL return, for each checkout in `get_project`, a `languages` object holding the observation status (`complete`, `partial` with its bound, `failed`, or `not_observed`), the observed time, and the languages with their statuses and file counts, and SHALL NOT sum counts across checkouts.

#### Scenario: Languages per checkout

- **GIVEN** a project with two checkouts with different languages
- **WHEN** the details are read
- **THEN** each checkout lists its own languages and no total is given

#### Scenario: Never observed

- **GIVEN** a checkout indexed before language detection existed
- **WHEN** the details are read
- **THEN** its `languages` has status `not_observed` and no language entries

#### Scenario: Missing checkout keeps its observation

- **GIVEN** a missing checkout with an earlier observation
- **WHEN** the details are read
- **THEN** its languages show the last observation and the checkout state `missing`

### Requirement: Languages stay separate from the profile

The system SHALL return detected languages in `languages` and SHALL leave `profile` and its `technologies` unchanged.

#### Scenario: Declared and detected differ

- **GIVEN** a profile declaring technologies Rust and a tree with only Python files
- **WHEN** the details are read
- **THEN** `profile` shows Rust and `languages` shows Python

### Requirement: Queries do not touch the filesystem

The system SHALL answer from stored observations only.

#### Scenario: Files changed since the scan

- **GIVEN** an indexed project whose files changed after the scan
- **WHEN** an agent searches or reads details
- **THEN** the stored observation and its time are returned

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
