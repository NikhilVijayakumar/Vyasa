# Specifications: be-project-query-basics

## 1. Specification Overview

- **OpenSpec Change ID:** `be-project-query-basics`
- **Purpose:** Let a caller search, read, and check the local index without writing or scanning.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/architecture/mcp-interface.md`, `knowledge/decisions/mcp-local-paths-omitted-by-default.md`
- **Team focus:** Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: project-query

### Purpose

Answer portfolio questions from the index alone.

### Scope

Search, project details, and index status. Context, relations, and dependencies are not covered.

## ADDED Requirements

### Requirement: Search is deterministic and bounded

The system SHALL return projects ordered by lower-case display name then project id, in pages of at most 100 (default 20) with an opaque cursor, and SHALL return identical output for identical queries on an unchanged index.

#### Scenario: Stable order across pages

- **GIVEN** 45 indexed projects
- **WHEN** they are read in pages of 20 using each `next_cursor`
- **THEN** every project appears once, in name order, and the last page has no cursor

#### Scenario: Page size limits

- **GIVEN** any index
- **WHEN** a limit of 0, 101, or a non-integer is given
- **THEN** `INVALID_INPUT` is returned and nothing else happens

#### Scenario: Bad cursor

- **GIVEN** a cursor not issued by the system
- **WHEN** it is used
- **THEN** `INVALID_CURSOR` is returned

#### Scenario: Repeatable

- **GIVEN** an unchanged index
- **WHEN** the same search runs twice
- **THEN** the results are identical

### Requirement: Search matches text and filters

The system SHALL match `query` case-insensitively as a substring of a project's display name or of any checkout's remote identity, report which field matched, combine filters (`state`, `provider`, `identity_status`) with AND between filters and OR within one, and reject unknown filter values.

#### Scenario: Name match

- **GIVEN** projects `billing-api` and `web`
- **WHEN** the query is `BILL`
- **THEN** only `billing-api` returns, with `matched` listing `display_name`

#### Scenario: Remote match

- **GIVEN** a project whose remote identity is `github.com/acme/tool`
- **WHEN** the query is `acme/tool`
- **THEN** it returns, with `matched` listing `remote_identity`

#### Scenario: Wildcards are literal

- **GIVEN** projects whose names lack `%` or `_`
- **WHEN** the query is `%` or `_`
- **THEN** no project returns

#### Scenario: Combined filters

- **GIVEN** active and missing projects on github and bitbucket
- **WHEN** state `active` and provider `github` are given
- **THEN** only active projects with a github checkout return

#### Scenario: Several values in one filter

- **GIVEN** the same projects
- **WHEN** provider is `github` or `bitbucket`
- **THEN** projects with either return

#### Scenario: Unknown filter value

- **GIVEN** any index
- **WHEN** state `retired` is given
- **THEN** `INVALID_INPUT` names the filter and its allowed values

#### Scenario: No match

- **GIVEN** any index
- **WHEN** nothing matches
- **THEN** an empty list returns with no error

### Requirement: Project details carry identity and review state

The system SHALL return one project's identifier, display name, state, identity status and source, aliases, checkouts (state, kind, markers, remote provider, host, identity, and status, times), open review candidates, and timestamps, SHALL mark an absent remote as such rather than omitting it, and SHALL return `PROJECT_NOT_FOUND` for an unknown id.

#### Scenario: Resolved project

- **GIVEN** a resolved project with two checkouts
- **WHEN** it is read
- **THEN** both checkouts, its aliases, and identity status `resolved` are returned

#### Scenario: Local project

- **GIVEN** a project without a remote
- **WHEN** it is read
- **THEN** its remote shows provider `none` and status as stored, and identity status `provisional`

#### Scenario: Review candidates

- **GIVEN** a project with an open duplicate candidate
- **WHEN** it is read
- **THEN** the candidate's rule, confidence, and review status appear

#### Scenario: Unknown project

- **GIVEN** an id that does not exist
- **WHEN** it is read
- **THEN** `PROJECT_NOT_FOUND` is returned

### Requirement: Index status reports reliability

The system SHALL report the index freshness, schema version, the latest run's status and finish time and counts, project counts by state, and the number of open review candidates, without scanning.

#### Scenario: Empty index

- **GIVEN** an index with no runs
- **WHEN** status is read
- **THEN** freshness is `unknown` and the counts are zero

#### Scenario: After a run

- **GIVEN** a completed run
- **WHEN** status is read within the freshness window
- **THEN** freshness is `current` and the latest run is `completed`

### Requirement: Queries are read-only and omit local paths

The system SHALL perform every query through a read-only connection, SHALL NOT include an absolute path or scanned root in any result unless the caller asks for paths, and SHALL wrap every result in `schema_version`, `data`, and `meta` with `generated_at`, `index_version`, and `freshness`.

#### Scenario: Write attempt

- **GIVEN** a connection opened read-only
- **WHEN** any query runs
- **THEN** the index file and its rows are unchanged

#### Scenario: Paths omitted

- **GIVEN** indexed projects
- **WHEN** a search, a project, and the status are read without asking for paths
- **THEN** no result contains a checkout path or a scanned root

#### Scenario: Paths on request

- **GIVEN** the same projects
- **WHEN** a project is read with paths enabled
- **THEN** each checkout shows its path

#### Scenario: Envelope

- **GIVEN** any successful query
- **WHEN** it returns
- **THEN** it carries `schema_version`, `data`, and `meta` with the three meta fields
