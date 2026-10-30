# scan-command Specification

## Purpose
TBD - created by archiving change be-scan-command. Update Purpose after archive.

## Requirements

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

### Requirement: Project-scoped scans inspect eligible checkouts

The system SHALL select the requested indexed project by its identifier and inspect only its indexed checkouts within currently configured roots. A project may have multiple eligible checkouts, and the system SHALL report an outcome for each. This scope follows `knowledge/architecture/data-model/relationships-and-runs.md`.

#### Scenario: Multiple eligible checkouts

- **GIVEN** an indexed project has two checkouts within configured roots and another project is indexed
- **WHEN** a project-scoped scan is requested for the first project
- **THEN** both eligible checkouts have individually reported outcomes
- **AND** the unrelated project's checkout is not scanned

#### Scenario: Checkout outside configured roots

- **GIVEN** an indexed checkout of the requested project is outside all currently configured roots
- **WHEN** a project-scoped scan is requested
- **THEN** that checkout is not scanned

### Requirement: Incomplete observations are reported honestly

The system SHALL report explicit failure or partial outcomes when a requested checkout is missing, inaccessible, moved, or conflicts with its indexed identity; it SHALL NOT present such an observation as a successful complete scan. This follows `knowledge/architecture/scanning-and-evidence/incremental-and-partial.md`.

#### Scenario: One checkout fails

- **GIVEN** an indexed project has two eligible checkouts and one is inaccessible
- **WHEN** the project-scoped scan runs
- **THEN** the outcome identifies the inaccessible checkout
- **AND** the run is not reported as successfully complete

### Requirement: Project scans preserve unrelated data and repository content

The system SHALL NOT mark unrelated checkouts missing during a project-scoped scan, execute repository content, or overwrite fields owned by another source. Field ownership follows `knowledge/concepts/field-ownership.md`.

#### Scenario: Unrelated checkout remains unchanged

- **GIVEN** another indexed project has a checkout within a configured root
- **WHEN** a project-scoped scan is run for a different project
- **THEN** the unrelated checkout is not marked missing by that scan

#### Scenario: Repository content is untrusted

- **GIVEN** an eligible checkout contains executable repository content
- **WHEN** a project-scoped scan inspects it
- **THEN** the repository content is not executed

### Requirement: Project scan scope is retained in history

The system SHALL persist the scope of project-scoped scan runs and their outcomes. Existing scan history SHALL remain available after migration and old runs SHALL be interpreted as workspace-scoped. Scope and item outcomes follow `knowledge/architecture/data-model/relationships-and-runs.md`.

#### Scenario: Existing scan history is migrated

- **GIVEN** an index containing scan runs created before scope was recorded
- **WHEN** the index is migrated
- **THEN** those runs remain available and are interpreted as workspace-scoped

#### Scenario: Project run is recorded

- **GIVEN** a project-scoped scan has completed or failed
- **WHEN** its history is read
- **THEN** its project scope and outcomes are available

### Requirement: Project scans do not refresh index-wide freshness

The system SHALL NOT change the index-wide freshness indicator as a result of a project-scoped scan.

#### Scenario: Project scan after an older workspace scan

- **GIVEN** the index-wide freshness is based on a previous workspace-scoped run
- **WHEN** a project-scoped scan finishes
- **THEN** the index-wide freshness is unchanged by the project-scoped run

### Requirement: Invalid project requests do not scan

The system SHALL report an explicit failure for an unknown project identifier and SHALL NOT scan any checkout for that request.

#### Scenario: Unknown project

- **GIVEN** an identifier that does not belong to an indexed project
- **WHEN** a project-scoped scan is requested for that identifier
- **THEN** the request fails explicitly and no checkout is scanned

### Requirement: Each unavailable or conflicting checkout is identified

The system SHALL report each missing, inaccessible, moved, identity-conflicting or out-of-root checkout individually and SHALL NOT treat it as a successful complete observation. This follows `knowledge/architecture/scanning-and-evidence/incremental-and-partial.md`.

#### Scenario: Missing checkout

- **GIVEN** an indexed checkout no longer exists at its recorded location
- **WHEN** its project is scanned
- **THEN** that checkout is reported missing and not as successfully observed

#### Scenario: Moved checkout

- **GIVEN** an indexed checkout has moved from its recorded location
- **WHEN** its project is scanned
- **THEN** the checkout is not reported as successfully observed at the recorded location

#### Scenario: Identity conflict

- **GIVEN** the checkout at an indexed location conflicts with the recorded project identity
- **WHEN** its project is scanned
- **THEN** the conflict is reported and the checkout is not treated as a successful observation of that project

#### Scenario: Checkout outside configured roots is reported

- **GIVEN** an indexed checkout is outside the currently configured roots
- **WHEN** its project is scanned
- **THEN** the checkout is reported as outside the configured roots and is not inspected
