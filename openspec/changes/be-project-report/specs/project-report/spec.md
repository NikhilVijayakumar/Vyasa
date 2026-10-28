# Specifications: be-project-report

## 1. Specification Overview

- **OpenSpec Change ID:** `be-project-report`
- **Purpose:** Store an agent-written project report by section and serve it.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/project-report-in-the-repository.md`
- **Team focus:** Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: project-report

### Purpose

Keep an agent's detailed reading of a repository durable and queryable.

### Scope

The report file, its sections, the scan read, and storage.

## ADDED Requirements

### Requirement: The report is read safely

The system SHALL read `.vyasa/project-report.md` at the root of each eligible project as text, at most the file limit (default 256 KiB), only when `.vyasa` is a real directory and the file a real file, SHALL NOT run anything from it, and SHALL NOT let a failure stop the scan.

#### Scenario: Missing report

- **GIVEN** a checkout with no report
- **WHEN** it is scanned
- **THEN** the report status is `not_present` and no problem is recorded

#### Scenario: Link in place of the file

- **GIVEN** `.vyasa/project-report.md` is a symbolic link
- **WHEN** the checkout is scanned
- **THEN** the report status is `unreadable` and the link target is not read

#### Scenario: Oversize file

- **GIVEN** a report larger than the file limit
- **WHEN** the checkout is scanned
- **THEN** the report status is `invalid` with a size reason naming the limit and the scan continues

### Requirement: Sections are kept by name and bounded

The system SHALL split the report on second-level headings, SHALL keep each section whose heading matches a template section (case-insensitive, trimmed), up to the section limit (default 16 KiB) of text each, SHALL drop and report each unknown heading, each duplicate, and each section over its limit with a reason, and SHALL strip control characters and reject a section containing a URL that carries credentials.

#### Scenario: Known sections kept

- **GIVEN** a report with the template headings
- **WHEN** it is scanned
- **THEN** each section is stored with its text

#### Scenario: Unknown heading dropped

- **GIVEN** a report with a heading not in the template
- **WHEN** it is scanned
- **THEN** that section is not stored and the heading is reported with a reason

#### Scenario: Section over the configured limit

- **GIVEN** a section limit of 1 KiB in the configuration and a 2 KiB section
- **WHEN** it is scanned
- **THEN** that section is dropped with a reason naming 1 KiB and the other sections are kept

#### Scenario: Credential URL rejected

- **GIVEN** a section containing `https://user:secret@host/path`
- **WHEN** it is scanned
- **THEN** that section is dropped with a reason and the others are kept

#### Scenario: Control characters stripped

- **GIVEN** a section containing control characters
- **WHEN** it is scanned
- **THEN** the stored text has none

### Requirement: Stored reports keep their provenance

The system SHALL store, per checkout, the report status, the limits that were applied, the content hash, the scan time, the sections with their sizes, and the dropped headings with reasons, and SHALL keep the previous stored report when a later read fails.

#### Scenario: Applied limits recorded

- **GIVEN** a configured file limit
- **WHEN** a checkout is scanned
- **THEN** the stored observation holds the file and section limits that were applied

#### Scenario: Hash and time

- **GIVEN** a valid report
- **WHEN** it is scanned
- **THEN** the stored record holds the content hash and the scan time

#### Scenario: Failed read keeps earlier data

- **GIVEN** a stored report and a later scan where the file is unreadable
- **WHEN** the scan finishes
- **THEN** other stored data is unchanged and the status shows the failure

### Requirement: The template is generated from the section definition

The system SHALL produce a template containing the report path, the format, the maximum file and section sizes (the limits applied by the latest scan when an index exists, otherwise the defaults, with their source), every section with its purpose, a complete example that validates, and rules for the writer, all derived from the same definition the reader uses.

#### Scenario: Example is valid

- **GIVEN** the template
- **WHEN** its example is read by the scan reader
- **THEN** every section is kept and nothing is dropped

#### Scenario: Limits follow the definition

- **GIVEN** the template
- **WHEN** a limit is read
- **THEN** it equals the reader's constant

#### Scenario: Rules forbid guessing and secrets

- **GIVEN** the template
- **WHEN** the rules are read
- **THEN** they tell the writer to omit unknown items, to take facts from the repository, and to include no credentials

### Requirement: Vyasa writes no report and starts no agent

The system SHALL NOT write the report, SHALL NOT start an agent, and SHALL leave every file in the repository unchanged by a scan.

#### Scenario: Repository unchanged

- **GIVEN** a repository with a report
- **WHEN** it is scanned
- **THEN** the repository hash is the same before and after
