# project-query Specification

## Purpose
TBD - created by archiving change be-project-query-basics. Update Purpose after archive.

## Requirements

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

### Requirement: Composition queries do not touch the filesystem

The system SHALL answer the filter and the details from stored observations only.

#### Scenario: Files changed since the scan

- **GIVEN** an indexed project whose files changed after the scan
- **WHEN** an agent searches or reads details
- **THEN** the stored counts and their observed time are returned

---
