@data-ownership @proposed
Feature: Data Ownership and Source of Truth — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q11 @Q3
  Scenario: A scanner cannot write a portfolio-owned field
    Given tracking level is owned by the portfolio maintainer
    When the scanner tries to write it through the ownership policy
    Then authorize_write refuses the write

  @Q10
  Scenario: Provider description never becomes the purpose
    Given a provider returns a repository description
    And the project has no profile purpose
    When the project context is requested
    Then the purpose is unknown
    And the description appears as a provider observation

  @Q5
  Scenario: Name falls back to the directory name as provisional
    Given a project with no profile and no manifest name
    When metadata is resolved
    Then the name is the directory name
    And it is marked provisional

  @Q2
  Scenario: A field without an owner fails the completeness test
    Given a new persisted field with no registry entry
    When the ownership completeness test runs
    Then the test fails and names the field

  @Q4
  Scenario: A declared obsolete lifecycle does not change portfolio status
    Given a profile declaring lifecycle archived
    When the project is reviewed
    Then a review candidate is raised
    And the portfolio status is unchanged

  @Q6
  Scenario: Conflicts are counted in index status
    Given three fields in conflict across the index
    When index status is requested
    Then it reports three open conflicts
