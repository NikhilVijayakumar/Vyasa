## ADDED Requirements

### Requirement: Name configured workspaces
The CLI SHALL allow a person to assign a bounded, nonempty local display name to a configured root without changing the root configuration or starting a scan.

#### Scenario: Set and retrieve a name
- **WHEN** a person names a configured root
- **THEN** the workspace list includes that name until it is explicitly changed

#### Scenario: Reject unconfigured root
- **WHEN** a name is assigned to an unconfigured root
- **THEN** the operation fails without creating or changing metadata

#### Scenario: Unnamed root
- **WHEN** a configured root has no assigned name
- **THEN** the workspace list reports no name and the root remains available
