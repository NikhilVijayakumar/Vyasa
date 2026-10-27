# Specifications: be-file-composition-query (file-composition)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-file-composition-query`
- **Purpose:** Obtain counts and languages from one walk and store the counts.
- **Related proposal:** `proposal.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/checkout-walk-observation.md`

## 2. Capability: file-composition

### Purpose

Keep the counts the scan made, honestly, next to the languages from the same walk.

### Scope

The scan and storage. Reading is specified in the `project-query` capability.

## ADDED Requirements

### Requirement: One walk feeds counts and languages

The system SHALL walk a checkout once per scan and derive both the counts and the language results from that file list, and SHALL keep `compose` and `detect_languages` returning the same results as before.

#### Scenario: Languages sum to the code count

- **GIVEN** a checkout with files of recognized code extensions, documentation, and other types
- **WHEN** it is scanned once
- **THEN** the language counts sum to the code count of the same scan

#### Scenario: Walk happens once

- **GIVEN** a scan of one checkout
- **WHEN** the scan runs
- **THEN** the checkout is walked exactly once

#### Scenario: Public functions unchanged

- **GIVEN** any tree
- **WHEN** `compose` and `detect_languages` are called
- **THEN** each returns what it returned before this change

### Requirement: Counts are stored on the observation

The system SHALL store the code, documentation, and other counts on the same observation as the languages of that walk, so that they share its time, completeness, and retention of the current and previous observation.

#### Scenario: Counts stored

- **GIVEN** a repository with 3 Python files and 2 Markdown files
- **WHEN** a scan completes
- **THEN** the observation holds 3 code, 2 documentation, and 0 other files

#### Scenario: Partial walk stores lower bounds

- **GIVEN** a checkout larger than the entry cap
- **WHEN** a scan completes
- **THEN** the observation is partial naming the cap and holds the counts gathered so far

#### Scenario: Retention

- **GIVEN** a checkout scanned three times
- **WHEN** the third scan completes
- **THEN** only the second and third observations, with their counts, exist

### Requirement: Failed and older observations have no counts

The system SHALL leave the counts empty on a failed observation and on an observation made before counts existed, and SHALL NOT store zeros for them.

#### Scenario: Failed observation

- **GIVEN** detection fails for a checkout
- **WHEN** the scan stores it
- **THEN** the observation is failed and its counts are empty

#### Scenario: Upgrade keeps old observations

- **GIVEN** an index at the previous version with language observations
- **WHEN** it is opened for writing
- **THEN** the observations are unchanged and their counts are empty

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
