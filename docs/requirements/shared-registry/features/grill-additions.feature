@shared-registry @proposed
Feature: Shared Registry and Cross-Device Visibility — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q3
  Scenario: A human-edited scanner cell is a conflict, not overwritten
    Given a scanner-owned cell was edited by hand since the last sync
    When synchronization runs
    Then the cell is left untouched
    And a conflict is reported until a preference is chosen

  @Q6
  Scenario: A missing required column aborts before any write
    Given the workbook lacks a required column
    When synchronization starts
    Then a schema validation error is reported
    And nothing is written

  @Q5
  Scenario: Dry run writes nothing
    Given a project with changes to export
    When synchronization runs with dry-run
    Then the planned changes are listed
    And the workbook is unchanged

  @Q8
  Scenario: Re-running a failed sync converges
    Given a sync run failed after writing some rows
    When synchronization is run again
    Then every row ends with the correct values
    And no row is duplicated

  @Q10
  Scenario: Local-only fields never reach the payload
    Given a sentinel value in every local-only field
    When the export payload is built
    Then no sentinel appears anywhere in the payload

  @Q14
  Scenario: A provisional identity is not exported
    Given a project whose identity is provisional
    When synchronization runs
    Then the project is not exported
    And it is reported as skipped with the reason

  @Q15
  Scenario: A registry-only project hides any foreign path
    Given a shared record with no local checkout on this device
    When its details are requested
    Then local availability is unavailable_on_this_device
    And no path is shown

  @Q11
  Scenario: Quota exhaustion ends the run as partial
    Given the API rejects requests after five attempts
    When synchronization runs
    Then the run is recorded as partial
    And the local index is unaffected
