@FR-002 @P1 @workspace-discovery
Feature: Project and Repository Discovery
  Vyasa MUST discover eligible local projects and Git repositories according to documented discovery rules.

  @FR-002-S1
  Scenario: Git repository
    Given a workspace contains a valid Git repository
    When the scanner processes it
    Then Vyasa identifies the repository
    And Vyasa records its available metadata

  @FR-002-S2
  Scenario: Project without Git
    Given a workspace contains an eligible project directory without a Git repository
    When the scanner processes it
    Then Vyasa may register it as a local project if it satisfies the documented discovery criteria

  @FR-002-S3
  Scenario: Nested repositories
    Given a repository contains another Git repository
    When the scanner processes the directory tree
    Then it follows documented nested-repository rules
    And it does not accidentally merge their metadata

  @FR-002-S4
  Scenario: Irrelevant directories
    Given a directory does not satisfy the project discovery criteria
    When scanning completes
    Then it is not registered as a project solely because it exists

  @FR-002-S5
  Scenario: Malformed repository
    Given a directory contains incomplete or malformed Git metadata
    When scanning encounters it
    Then Vyasa reports the issue
    And Vyasa continues processing other eligible projects

  @FR-002-S6
  Scenario: Repeated discovery
    Given the same workspace is scanned repeatedly without relevant changes
    When each scan completes
    Then Vyasa does not create duplicate project records
