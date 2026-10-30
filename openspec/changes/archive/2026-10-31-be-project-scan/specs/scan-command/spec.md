## ADDED Requirements

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
