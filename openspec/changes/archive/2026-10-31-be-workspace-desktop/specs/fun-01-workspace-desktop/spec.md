## ADDED Requirements

### Requirement: List configured workspace roots
The CLI SHALL report the configured roots without modifying the index or starting a scan.

#### Scenario: List roots
- **WHEN** configured roots are requested
- **THEN** the CLI returns those roots and their accessibility status

### Requirement: Search within a configured workspace
The CLI SHALL allow search results to be restricted to a configured root before pagination.

#### Scenario: Filter projects
- **WHEN** a configured root is selected
- **THEN** only projects with a checkout in that root are returned

#### Scenario: Reject unconfigured root
- **WHEN** an unconfigured root is requested
- **THEN** the CLI returns an error and does not scan or modify the index

### Requirement: Scan a configured workspace
The CLI SHALL allow the user to scan a single configured root without changing the state of projects belonging only to other roots.

#### Scenario: Scan one root
- **WHEN** a configured root is explicitly selected for scanning
- **THEN** only that root is scanned and the result reports its outcome
