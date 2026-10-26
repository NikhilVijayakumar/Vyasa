@FR-017 @P2 @shared-registry
Feature: Cross-Device Project Visibility
  Vyasa MUST allow a device to retrieve shared project metadata even when the corresponding repository is not cloned locally.

  @FR-017-S1
  Scenario: Registry-only project
    Given a project exists in Google Sheets but is absent from the current device's workspace roots
    When the registry is loaded
    Then Vyasa makes the project discoverable as a shared record

  @FR-017-S2
  Scenario: Local and shared match
    Given a local project matches a shared registry record
    When records are reconciled
    Then Vyasa associates them according to the documented identity rules

  @FR-017-S3
  Scenario: No local repository
    Given a shared project has no local repository mapping
    When its details are requested
    Then Vyasa reports that local source files are unavailable on the current device

  @FR-017-S4
  Scenario: Local path isolation
    Given two devices use different local paths for the same project
    When shared metadata is synchronized
    Then the shared record does not require either device's local path to identify the project

  @FR-017-S5
  Scenario: Stale shared record
    Given a shared record has not been recently verified
    When returned to a client
    Then its verification status and last-known scan information are represented accurately. ---
