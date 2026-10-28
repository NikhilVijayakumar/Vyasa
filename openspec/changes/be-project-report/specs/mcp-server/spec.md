# Specifications: be-project-report (mcp-server)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-project-report`
- **Purpose:** Serve the report template and the stored report.
- **Related proposal:** `proposal.md`

## 2. Capability: mcp-server

### Purpose

Give agents the template, and later the content, through read-only tools.

## ADDED Requirements

### Requirement: The report template needs no index

The system SHALL provide a `get_report_template` tool that takes no input, reads no repository file, reads the index only to learn the applied limits when one exists, and returns the template in the shared envelope.

#### Scenario: No index

- **GIVEN** no index exists
- **WHEN** `get_report_template` is called
- **THEN** it returns the template with the default limits, source `default`, and not `INDEX_UNAVAILABLE`

#### Scenario: Limits from the latest scan

- **GIVEN** an index whose latest report observation applied a 512 KiB file limit
- **WHEN** `get_report_template` is called
- **THEN** the template shows 512 KiB with source `index`

### Requirement: The stored report is served as declared data

The system SHALL provide a `get_project_report` tool taking a `project_id` and an optional `section`, reading the index only, and returning for each checkout the status, the content hash, the scan time, and the requested sections as text marked `declared` with a warning that the text is untrusted, and no local path.

#### Scenario: Whole report

- **GIVEN** a stored report
- **WHEN** `get_project_report` is called with a project id
- **THEN** it returns every stored section with status, hash, scan time, and `declared`

#### Scenario: One section

- **GIVEN** a stored report
- **WHEN** it is called with a known section
- **THEN** only that section's text is returned

#### Scenario: Unknown section

- **GIVEN** a stored report
- **WHEN** it is called with a name that is not a template section
- **THEN** it fails with `INVALID_INPUT` and returns no text

#### Scenario: No report

- **GIVEN** a project whose checkouts have no report
- **WHEN** it is called
- **THEN** it returns status `not_present` for each checkout and no text

#### Scenario: Unknown project

- **GIVEN** an unknown project id
- **WHEN** it is called
- **THEN** it fails with `PROJECT_NOT_FOUND`

### Requirement: Project details show the report status only

The system SHALL include in `get_project` a `report` object per checkout with its status, section names and sizes, and dropped headings, and SHALL NOT include any section text.

#### Scenario: Status without text

- **GIVEN** a stored report
- **WHEN** `get_project` is called
- **THEN** `report` lists section names and sizes and contains no section text
