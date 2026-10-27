# Specifications: be-scan-command

## 1. Specification Overview

- **OpenSpec Change ID:** `be-scan-command`
- **Purpose:** Let the owner build and refresh the local index from the configured workspace roots.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/concepts/explicit-operations.md`, `knowledge/decisions/index-lifecycle-and-single-writer.md`
- **Team focus:** Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: scan-command

### Purpose

Run discovery over the configured roots and store the results.

### Scope

The command, multi-root orchestration, the report, and exit codes. Detectors and profiles are not covered.

## ADDED Requirements

### Requirement: Only configured roots are scanned

The system SHALL scan exactly the roots the configuration lists, one after another, and SHALL NOT visit any other directory.

#### Scenario: Several roots

- **GIVEN** a configuration with two roots holding repositories, and a sibling directory outside both that also holds a repository
- **WHEN** the scan runs
- **THEN** the repositories of both roots are indexed and the outside repository is not

#### Scenario: Nested roots

- **GIVEN** a configuration where one root is inside another
- **WHEN** the scan runs
- **THEN** the inner root is dropped by configuration loading and its repositories are scanned once

### Requirement: The first run creates what it needs

The system SHALL create the data directory and the index on first use and then store the results, and SHALL report that the index was created.

#### Scenario: First scan

- **GIVEN** a configuration and no data directory
- **WHEN** the scan runs
- **THEN** the data directory and index exist, the projects are stored, and the report says the index was created

#### Scenario: Repeated scan

- **GIVEN** an index from an earlier scan of unchanged roots
- **WHEN** the scan runs again
- **THEN** no project is added, every project is reported unchanged, and the report does not say the index was created

### Requirement: Each root is reported

The system SHALL print, for each root, its status (`complete`, `partial`, or `failed`), the repositories found, what was added, updated, unchanged, attached, restored, or marked missing, and each skip reason with its advice, and SHALL finish with the total number of indexed projects.

#### Scenario: Complete root

- **GIVEN** a root with three repositories
- **WHEN** the scan runs
- **THEN** the report shows `complete`, three repositories, and three added

#### Scenario: Skipped directories

- **GIVEN** a root with a directory below the depth limit
- **WHEN** the scan runs
- **THEN** the report names the skip reason, a count, and the advice

#### Scenario: Missing root

- **GIVEN** a configured root that does not exist and another that does
- **WHEN** the scan runs
- **THEN** the missing root is reported `failed` with a reason, the other root is scanned, and nothing is marked missing for the failed root

### Requirement: The exit code tells the truth

The system SHALL exit 0 only when every root completed, 1 when any root was partial or failed, 2 when the configuration is missing or invalid (scanning nothing), and 3 when another scan holds the index.

#### Scenario: All complete

- **GIVEN** roots that all complete
- **WHEN** the scan runs
- **THEN** the exit code is 0

#### Scenario: Partial or failed root

- **GIVEN** a root that fails
- **WHEN** the scan runs
- **THEN** the exit code is 1

#### Scenario: No configuration

- **GIVEN** no configuration file
- **WHEN** the scan runs
- **THEN** it prints where it looked and how to configure roots, scans nothing, creates nothing, and exits 2

#### Scenario: Invalid configuration

- **GIVEN** a configuration with an unknown key
- **WHEN** the scan runs
- **THEN** every problem is printed, nothing is scanned or created, and the exit code is 2

#### Scenario: Concurrent scan

- **GIVEN** another process holds the index writer lock
- **WHEN** the scan runs
- **THEN** it reports that another scan is running and exits 3 without writing

### Requirement: Scanning does not change repositories

The system SHALL leave every scanned repository byte-identical.

#### Scenario: Before and after

- **GIVEN** a repository tree with a recorded content hash
- **WHEN** the scan runs
- **THEN** the hash is unchanged
