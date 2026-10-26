@FR-008 @P1 @local-index
Feature: Incremental Scanning and Refresh
  Vyasa MUST support refreshing the local index while minimizing unnecessary work where practical.

  @FR-008-S1
  Scenario: Initial scan
    Given a new index has no project records
    When a scan is requested
    Then Vyasa discovers eligible projects and builds the index

  @FR-008-S2
  Scenario: Unchanged project
    Given a project has not changed in ways relevant to supported detectors
    When an incremental scan runs
    Then Vyasa may reuse valid prior results according to its invalidation rules

  @FR-008-S3
  Scenario: Changed manifest
    Given a recognized manifest changes
    When a scan runs
    Then affected metadata is recalculated

  @FR-008-S4
  Scenario: Deleted metadata file
    Given a previously recognized file has been deleted
    When a successful scan runs
    Then facts dependent on that file are updated or removed according to the field ownership and evidence rules

  @FR-008-S5
  Scenario: Interrupted scan
    Given a scan is interrupted
    When the index is accessed afterward
    Then previously committed valid records remain usable and incomplete updates are not falsely reported as a successful complete scan

  @FR-008-S6
  Scenario: Concurrent refresh requests
    Given overlapping refresh requests are submitted
    When the service processes them
    Then it follows a documented concurrency policy and avoids inconsistent index state

  @FR-008-S7
  Scenario: Refresh result
    Given a scan finishes
    When its outcome is reported
    Then the result identifies the relevant scope, counts, errors, and completion status
