# Specifications: be-project-report (workspace-configuration)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-project-report`
- **Purpose:** Let the report size limits be configured.
- **Related proposal:** `proposal.md`

## 2. Capability: workspace-configuration

### Purpose

Keep Vyasa's tunable settings explicit, validated, and bounded.

## ADDED Requirements

### Requirement: Report limits are configurable inside bounds

The system SHALL accept an optional `report` table in the configuration with `max_file_kib` (integer, default 256, from 16 to 4096) and `max_section_kib` (integer, default 16, from 1 to 1024 and not above `max_file_kib`), SHALL use the defaults for any setting not given, and SHALL reject the whole configuration, naming the setting, when a value is not an integer, is outside its bounds, or when a key in the table is unknown.

#### Scenario: Defaults

- **GIVEN** a configuration with no `report` table
- **WHEN** it is loaded
- **THEN** the file limit is 256 KiB and the section limit is 16 KiB

#### Scenario: Configured values

- **GIVEN** `report.max_file_kib = 512` and `report.max_section_kib = 32`
- **WHEN** it is loaded
- **THEN** the limits are 512 KiB and 32 KiB

#### Scenario: Out of bounds

- **GIVEN** `report.max_file_kib = 100000`
- **WHEN** it is loaded
- **THEN** loading fails naming `report.max_file_kib` and nothing is applied

#### Scenario: Section above file

- **GIVEN** `report.max_file_kib = 16` and `report.max_section_kib = 32`
- **WHEN** it is loaded
- **THEN** loading fails naming `report.max_section_kib`

#### Scenario: Wrong type or unknown key

- **GIVEN** `report.max_file_kib = "big"` or an unrecognized key under `report`
- **WHEN** it is loaded
- **THEN** loading fails naming the setting
