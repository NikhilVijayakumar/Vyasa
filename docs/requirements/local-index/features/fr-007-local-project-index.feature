@FR-007 @P1 @local-index
Feature: Local Project Index
  Vyasa MUST maintain a local index that supports project discovery and retrieval without requiring external services.

  @FR-007-S1
  Scenario: Persisted index
    Given a successful scan has populated the index
    When Vyasa restarts
    Then previously indexed project records remain available subject to their freshness status

  @FR-007-S2
  Scenario: New project
    Given a new eligible project is discovered
    When the index is updated
    Then the project becomes searchable

  @FR-007-S3
  Scenario: Changed project
    Given relevant project metadata changes
    When a rescan completes
    Then the index reflects the newly detected information and its evidence

  @FR-007-S4
  Scenario: Removed or inaccessible project
    Given a previously indexed project can no longer be found or accessed
    When a scan runs
    Then Vyasa applies a documented stale, missing, or inaccessible state instead of silently erasing all evidence of the record

  @FR-007-S5
  Scenario: Index migration
    Given the local schema version changes
    When Vyasa opens an existing database
    Then it applies supported migrations or reports a controlled recovery error

  @FR-007-S6
  Scenario: Offline operation
    Given external network access is unavailable
    When Phase 1 operations run against local workspaces and the local index
    Then they continue without requiring an external service
