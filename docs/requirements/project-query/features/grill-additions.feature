@project-query @proposed
Feature: Project Search, Context, Relations and Dependencies — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q3
  Scenario: Exact name outranks prefix and technology matches
    Given projects named api, api-gateway, and tools that all match a query for api
    When the search runs
    Then the exact match is listed first
    And the remaining matches follow the documented ladder
    And ties are ordered by display name then project id

  @Q4
  Scenario: Empty index is distinguished from no match
    Given the index has never been scanned
    When a search runs
    Then the result is empty
    And the freshness is unknown
    And an INDEX_EMPTY hint is returned

  @Q2
  Scenario: Combined filters use AND
    Given projects with different technologies and documentation traits
    When a search combines a technology filter and a documentation filter
    Then every result satisfies both filters

  @Q7
  Scenario: A long list in a context is truncated explicitly
    Given a project with more technologies than the list cap
    When its context is requested
    Then the list holds the capped number of items
    And truncated is true and the total is reported

  @Q6
  Scenario: Dependents are found from the same table
    Given project A declares a dependency that maps to indexed project B
    When the dependents of B are requested
    Then A is listed with the supporting evidence

  @Q5
  Scenario: Ubiquitous technologies do not relate projects
    Given two projects share only git and markdown
    When related projects are requested for one of them
    Then the other is not returned

  @Q14
  Scenario: Dependency results state their coverage
    Given a project has a supported manifest and an unsupported one
    When its dependencies are requested
    Then the result lists the manifests parsed and the unsupported manifest seen

  @Q13
  Scenario: Repeated queries are byte-identical
    Given an unchanged index
    When the same search runs ten times
    Then every response is identical
