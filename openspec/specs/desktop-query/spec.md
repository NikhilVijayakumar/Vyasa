# desktop-query Specification

## Purpose
TBD - created by archiving change be-desktop-cli-query. Update Purpose after archive.

## Requirements

### Requirement: Machine-readable indexed queries
The CLI SHALL provide read-only JSON queries for index status, project search, project details, dependencies, profile context and project reports using the existing query services.

#### Scenario: Search indexed projects
- **WHEN** a client requests a valid project search
- **THEN** the CLI returns the query service's JSON envelope without scanning or modifying the index

#### Scenario: Index unavailable
- **WHEN** the configured index does not exist or cannot be opened
- **THEN** the CLI returns a structured unavailable error and a nonzero exit code without creating an index

#### Scenario: Invalid query
- **WHEN** a client supplies an invalid query or project identifier
- **THEN** the CLI returns a structured error and a nonzero exit code

### Requirement: Report the backend version
The CLI SHALL return its installed backend version as machine-readable JSON without opening the index.

#### Scenario: Query the version
- **WHEN** a client requests the CLI version
- **THEN** the response identifies the installed backend package version
