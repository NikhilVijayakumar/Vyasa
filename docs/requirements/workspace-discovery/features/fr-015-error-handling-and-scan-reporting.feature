@FR-015 @P1 @workspace-discovery
Feature: Error Handling and Scan Reporting
  Vyasa MUST report scan and indexing outcomes in a way that makes failures and partial results distinguishable from successful complete operations.

  @FR-015-S1
  Scenario: Partial scan
    Given some repositories can be scanned while others fail
    When the scan finishes
    Then Vyasa reports partial completion
    And Vyasa identifies failed or skipped items

  @FR-015-S2
  Scenario: File access failure
    Given a recognized file cannot be read
    When the scanner processes it
    Then the failure is recorded without terminating unrelated project scans

  @FR-015-S3
  Scenario: Unsupported file format
    Given a manifest or configuration format is unsupported
    When the scanner encounters it
    Then Vyasa reports the limitation where relevant
    And Vyasa does not fabricate extracted facts

  @FR-015-S4
  Scenario: Scan history
    Given a scan completes or fails
    When its outcome is recorded
    Then the index retains an appropriate run status, timestamp, scope, and summary

  @FR-015-S5
  Scenario: Safe diagnostics
    Given an error contains sensitive local configuration or credential information
    When the error is reported or logged
    Then sensitive values are redacted or excluded. ---
