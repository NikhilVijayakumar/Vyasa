@NFR @P1 @quality-attributes
Feature: Operational qualities
  Cross-cutting qualities that can be checked as observable behaviour.

  @NFR-011
  Scenario: Phase 1 works offline
    Given no network connection is available
    When a scan, a query, and a status request run
    Then each completes

  @NFR-009
  Scenario: Startup does not scan
    Given a valid existing index
    When the MCP server starts
    Then it opens the index without scanning any workspace
    And it does not contact Google Sheets or a provider

  @NFR-014
  Scenario: Repeating a scan is idempotent
    Given an unchanged workspace that has been scanned once
    When it is scanned again
    Then the project set and values are unchanged
    And no duplicate records exist

  @NFR-012
  Scenario: One failing project does not stop the others
    Given one project whose detector raises an error
    When the workspace is scanned
    Then the other projects are indexed
    And the failure is reported for that project only

  @NFR-013
  Scenario: Recovery after an interrupted scan
    Given a scan was interrupted
    When Vyasa starts again
    Then previously committed projects are queryable
    And index freshness reports partial

  @NFR-032
  Scenario: Logs are structured and carry a run identifier
    Given a scan is running
    When it logs an event
    Then the entry is structured
    And it includes the run identifier and an event code

  @NFR-034
  Scenario: Freshness is visible in results
    Given an index last scanned longer ago than the freshness threshold
    When a client asks for index status
    Then the status reports stale and the time of the last completed run

  @NFR-031
  Scenario: A doctor command explains a broken setup
    Given a missing configuration file
    When the user runs the doctor command
    Then it names the problem and the fix
    And it makes no change

  @NFR-029
  Scenario Outline: Behaviour is the same on each supported platform
    Given the continuous integration job runs on <platform>
    When the test suite runs
    Then path handling and storage tests pass

    Examples:
      | platform |
      | linux    |
      | macos    |
      | windows  |
