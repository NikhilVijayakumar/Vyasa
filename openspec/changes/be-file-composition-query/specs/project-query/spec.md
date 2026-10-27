# Specifications: be-file-composition-query (project-query)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-file-composition-query`
- **Purpose:** Filter search by documentation-only and show composition in project details.
- **Related proposal:** `proposal.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/checkout-walk-observation.md`

## 2. Capability: project-query

### Purpose

Let an agent find documentation-only projects and read a checkout's counts without any filesystem access.

### Scope

`search_projects` and `get_project`. Existing parameters and fields are unchanged.

## ADDED Requirements

### Requirement: Search filters by documentation_only

The system SHALL accept `documentation_only` as a boolean. With true it SHALL return the projects having an active checkout whose current observation is complete, has documentation files, and has no code files. With false it SHALL return the projects having an active checkout whose current observation is complete and is not documentation-only. A checkout whose indicator is unknown SHALL match neither value. The filter combines with the others by AND.

#### Scenario: Documentation-only projects

- **GIVEN** one project with only Markdown files and one with Python files
- **WHEN** an agent searches with documentation_only true
- **THEN** only the Markdown project is returned

#### Scenario: Projects with code

- **GIVEN** the same projects
- **WHEN** an agent searches with documentation_only false
- **THEN** only the Python project is returned

#### Scenario: Partial count matches neither

- **GIVEN** a checkout whose count stopped at the entry cap
- **WHEN** an agent searches with documentation_only true, and again with false
- **THEN** the project is returned for neither

#### Scenario: Not counted matches neither

- **GIVEN** a checkout observed before counts existed
- **WHEN** an agent searches with documentation_only true, and again with false
- **THEN** the project is returned for neither

#### Scenario: Any active checkout matches

- **GIVEN** a project with two active checkouts, one documentation-only and one with code
- **WHEN** an agent searches with documentation_only true, and again with false
- **THEN** the project is returned for both

#### Scenario: Missing checkout does not match

- **GIVEN** a project whose only documentation-only checkout is missing
- **WHEN** an agent searches with documentation_only true
- **THEN** the project is not returned

#### Scenario: Combined with a language filter

- **GIVEN** a documentation-only project and a Python project
- **WHEN** an agent searches with documentation_only false and language Python
- **THEN** only the Python project is returned

#### Scenario: Not a boolean

- **GIVEN** an indexed workspace
- **WHEN** an agent searches with documentation_only "yes"
- **THEN** the request fails with `INVALID_INPUT`

### Requirement: Details list composition per checkout

The system SHALL return, for each checkout in `get_project`, a `composition` object holding its status (`complete`, `partial` with its bound, or `not_counted`), the observed time, the code, documentation, other, and total counts, and the derived `documentation_only` indicator, and SHALL NOT sum counts across checkouts.

#### Scenario: Counts per checkout

- **GIVEN** a project with two checkouts of different composition
- **WHEN** the details are read
- **THEN** each checkout lists its own counts and no project total is given

#### Scenario: Counts agree

- **GIVEN** a counted checkout
- **WHEN** the details are read
- **THEN** total equals code plus documentation plus other

#### Scenario: Not counted is not zero

- **GIVEN** a checkout observed before counts existed, and a checkout whose detection failed
- **WHEN** the details are read
- **THEN** each reports status `not_counted`, no numbers, and `documentation_only` null

#### Scenario: Partial shows its bound

- **GIVEN** a checkout whose count stopped at the entry cap
- **WHEN** the details are read
- **THEN** its status is `partial` naming the bound, its counts are lower bounds, and `documentation_only` is null

#### Scenario: Indicator follows the counts

- **GIVEN** a complete observation of 0 code and 4 documentation files
- **WHEN** the details are read
- **THEN** `documentation_only` is true

#### Scenario: Missing checkout keeps its counts

- **GIVEN** a missing checkout with an earlier observation
- **WHEN** the details are read
- **THEN** its composition shows the last observation and the checkout state is `missing`

### Requirement: Queries do not touch the filesystem

The system SHALL answer the filter and the details from stored observations only.

#### Scenario: Files changed since the scan

- **GIVEN** an indexed project whose files changed after the scan
- **WHEN** an agent searches or reads details
- **THEN** the stored counts and their observed time are returned

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
