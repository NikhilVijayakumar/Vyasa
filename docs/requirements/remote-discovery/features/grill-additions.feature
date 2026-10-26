@remote-discovery @proposed
Feature: Remote Repository Discovery and Inspection — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q7
  Scenario: Authentication failure is not an empty success
    Given the configured credential has expired
    When discovery runs
    Then the run reports an access failure
    And previously discovered repositories are kept

  @Q6
  Scenario: A failed page leaves the scope incomplete
    Given the second page of results fails
    When discovery runs
    Then repositories from the first page are retained
    And the scope is marked incomplete

  @Q5
  Scenario: Rate limiting ends the run as partial
    Given the provider keeps rate-limiting requests
    When discovery retries the allowed number of times
    Then the run is recorded as partial
    And the retry bound was not exceeded

  @Q8
  Scenario: A repository is not declared gone after one missed listing
    Given a known repository is absent from one complete listing
    When discovery completes
    Then the repository is still reported as present
    And its status becomes missing only after a second complete listing omits it

  @Q13
  Scenario: Discovery never clones
    Given a discovery run over several repositories
    When it completes
    Then no Git process was started

  @Q2
  Scenario: Archived repositories are listed but not inspected
    Given an archived repository inside a configured scope
    When discovery and inspection run with default settings
    Then the repository is recorded as archived
    And none of its files are fetched

  @Q10
  Scenario: Private repositories are not exported by default
    Given a private repository discovered in a scope without share_to_registry
    When synchronization runs
    Then the repository is not exported

  @Q12
  Scenario: An oversized response is rejected safely
    Given the provider returns a body larger than the size cap
    When the adapter reads it
    Then the body is rejected
    And the item is reported as skipped by policy
