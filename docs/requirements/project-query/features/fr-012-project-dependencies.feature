@FR-012 @P1 @project-query
Feature: Project Dependencies
  Vyasa MUST expose dependency information only where it can be established from recognized evidence.

  @FR-012-S1
  Scenario: Manifest dependency
    Given a supported manifest declares dependencies
    When dependency information is requested
    Then Vyasa returns the recognized dependency names and available version constraints

  @FR-012-S2
  Scenario: Unsupported format
    Given dependency information exists only in an unsupported format
    When dependencies are requested
    Then Vyasa reports that the information is unavailable or partially supported

  @FR-012-S3
  Scenario: Internal project dependency
    Given a recognized dependency can be mapped to another indexed project
    When project dependencies are queried
    Then Vyasa reports the relationship and the supporting evidence

  @FR-012-S4
  Scenario: External dependency
    Given a dependency does not map to an indexed project
    When dependencies are queried
    Then Vyasa may report it as an external dependency without creating a fictional local project

  @FR-012-S5
  Scenario: Incomplete dependency information
    Given dependency metadata is incomplete
    When results are returned
    Then Vyasa identifies the available coverage
    And Vyasa does not claim an exhaustive dependency graph
