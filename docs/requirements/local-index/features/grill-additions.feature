@local-index @proposed
Feature: Local Index and Incremental Refresh — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q7
  Scenario: A second refresh is refused while one is running
    Given a scan is running
    When another refresh is requested
    Then the request fails with OPERATION_IN_PROGRESS
    And the running scan is unaffected

  @Q7
  Scenario: A dead lock is taken over and recorded
    Given the writer lock heartbeat is older than twice the heartbeat interval
    When a refresh is requested
    Then the lock is taken over
    And the takeover is recorded in the run

  @Q8
  Scenario: A crashed run becomes interrupted at startup
    Given a run is marked running and its lock owner no longer exists
    When Vyasa starts
    Then the run is marked interrupted
    And index freshness is partial until a run completes

  @Q9
  Scenario: A newer schema is refused
    Given the database schema version is newer than the code supports
    When Vyasa opens the database
    Then it reports a controlled error
    And it does not modify the database

  @Q9
  Scenario: A migration takes a backup first
    Given a database at an older supported schema version
    When Vyasa applies a migration
    Then a backup copy of the database exists before any change

  @Q6
  Scenario: A changed detector option invalidates reuse
    Given a project's previous results were produced with different detector options
    When an incremental scan runs
    Then the affected results are recomputed

  @Q4
  Scenario: A missing project keeps its history
    Given an indexed project whose directory was removed
    When a scan completes
    Then the project is marked missing
    And its observations and history are retained

  @Q16
  Scenario: The whole phase 1 flow works with sockets blocked
    Given all network connections are refused
    When a scan, a query, and a status request run
    Then each completes without error
