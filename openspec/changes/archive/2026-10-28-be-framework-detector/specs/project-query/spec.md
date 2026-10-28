# Specifications: be-framework-detector (project-query)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-framework-detector`
- **Purpose:** Filter search by technology and show frameworks in project details.
- **Related proposal:** `proposal.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/framework-detection-from-manifests.md`

## 2. Capability: project-query

### Purpose

Let an agent find projects by technology and read what a checkout declares without any filesystem access.

### Scope

`search_projects` and `get_project`. Existing parameters and fields are unchanged.

## ADDED Requirements

### Requirement: Search filters by technology

The system SHALL accept `technology` as a registry key or list of keys, compared case-insensitively, and SHALL return the projects having an active checkout whose current observation declares any of them. Several keys combine with OR; the filter combines with the others by AND.

#### Scenario: One technology

- **GIVEN** one project declaring FastAPI and one declaring React
- **WHEN** an agent searches with technology fastapi
- **THEN** only the FastAPI project is returned

#### Scenario: Several keys

- **GIVEN** projects declaring FastAPI, React, and Tokio
- **WHEN** an agent searches with technologies fastapi and tokio
- **THEN** the FastAPI and Tokio projects are returned

#### Scenario: Case-insensitive key

- **GIVEN** a project declaring FastAPI
- **WHEN** an agent searches with technology FastAPI
- **THEN** the project is returned

#### Scenario: Dev declaration counts

- **GIVEN** a project declaring pytest only as a dev dependency
- **WHEN** an agent searches with technology pytest
- **THEN** the project is returned and its details show scope `dev`

#### Scenario: Any active checkout

- **GIVEN** a project with two active checkouts, only one declaring Django
- **WHEN** an agent searches with technology django
- **THEN** the project is returned

#### Scenario: Missing checkout does not match

- **GIVEN** a project whose only checkout declaring Django is missing
- **WHEN** an agent searches with technology django
- **THEN** the project is not returned

#### Scenario: Malformed or not assessed does not match

- **GIVEN** a checkout with a malformed manifest and a checkout observed before this detector
- **WHEN** an agent searches with any technology
- **THEN** neither project is returned

#### Scenario: Combined with another filter

- **GIVEN** a Python project and a Rust project that both declare a test framework
- **WHEN** an agent searches with that technology and language Python
- **THEN** only the Python project is returned

#### Scenario: Unknown key

- **GIVEN** an indexed workspace
- **WHEN** an agent searches with technology fastapii
- **THEN** the request fails with `INVALID_INPUT` listing the allowed keys

### Requirement: Details list frameworks per checkout

The system SHALL return, for each checkout in `get_project`, a `frameworks` object holding its assessment status (`complete`, `partial` with its bound, or `not_assessed`), the registry version, the observed time, for each ecosystem its state, its manifests with status, reason, dependency total, skipped count, workspace flag, and capped dependencies with constraint and scope, and the nested manifests not parsed, and the technologies with key, scopes, and the manifests that declared them, and SHALL NOT combine checkouts.

#### Scenario: Frameworks per checkout

- **GIVEN** a project with two checkouts declaring different technologies
- **WHEN** the details are read
- **THEN** each checkout lists its own technologies

#### Scenario: Ecosystem states

- **GIVEN** a complete observation with a parsed `pyproject.toml` and nothing else
- **WHEN** the details are read
- **THEN** Python is `detected` and the other ecosystems are `not_detected`

#### Scenario: Partial observation

- **GIVEN** a partial observation that found no root manifest
- **WHEN** the details are read
- **THEN** each ecosystem is `unknown` and none is `not_detected`

#### Scenario: Not assessed

- **GIVEN** a checkout observed before this detector, and a checkout whose detection failed
- **WHEN** the details are read
- **THEN** each reports `not_assessed` and no ecosystems or technologies

#### Scenario: Evidence shown

- **GIVEN** a parsed manifest with a skipped count and a workspace flag
- **WHEN** the details are read
- **THEN** its status, reason, total, skipped count, workspace flag, and dependencies with scopes are given

#### Scenario: No text and no absolute path

- **GIVEN** a malformed manifest
- **WHEN** the details are read
- **THEN** only a fixed reason code is given and no file text and no absolute path appear

#### Scenario: Missing checkout keeps its frameworks

- **GIVEN** a missing checkout with an earlier observation
- **WHEN** the details are read
- **THEN** its frameworks show the last observation and the checkout state is `missing`

### Requirement: Framework queries do not touch the filesystem

The system SHALL answer the technology filter and the details from stored observations only.

#### Scenario: Files changed since the scan

- **GIVEN** an indexed project whose manifests changed after the scan
- **WHEN** an agent searches or reads details
- **THEN** the stored frameworks and their observed time are returned and no file is opened

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
