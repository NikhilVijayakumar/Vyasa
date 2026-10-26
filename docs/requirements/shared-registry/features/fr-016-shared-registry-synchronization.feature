@FR-016 @P2 @shared-registry
Feature: Shared Registry Synchronization
  Vyasa MUST synchronize an approved subset of project metadata with Google Sheets.

  @FR-016-S1
  Scenario: New project synchronization
    Given a new eligible project is indexed locally
    When synchronization runs
    Then Vyasa creates or updates its shared registry record using the stable project identity

  @FR-016-S2
  Scenario: Existing project synchronization
    Given a project already exists in the registry
    When its approved metadata changes
    Then Vyasa updates the fields it owns according to the synchronization policy

  @FR-016-S3
  Scenario: Human-managed fields
    Given the registry contains human-managed values such as tracking level or notes
    When synchronization runs
    Then those values are preserved unless an explicitly authorized operation changes them

  @FR-016-S4
  Scenario: Export allowlist
    Given a local project record contains local paths or machine-specific data
    When metadata is synchronized
    Then those fields are excluded from export

  @FR-016-S5
  Scenario: Synchronization failure
    Given Google Sheets is unavailable or authentication fails
    When synchronization is attempted
    Then Vyasa reports the failure
    And Vyasa preserves the usable local index

  @FR-016-S6
  Scenario: Conflicting values
    Given a shared field has changed locally and remotely
    When synchronization detects the conflict
    Then it applies the documented ownership and conflict policy rather than silently overwriting an owned value

  @FR-016-S7
  Scenario: Scan history
    Given synchronization runs
    When the operation finishes
    Then the corresponding outcome is recorded with counts and relevant errors

  @FR-016-S8
  Scenario: Registry schema
    Given the shared workbook is missing required tabs or columns
    When synchronization starts
    Then Vyasa reports a schema validation error rather than writing values into unrelated columns
