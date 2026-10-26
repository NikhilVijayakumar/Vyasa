@FR-001 @P1 @workspace-discovery
Feature: Configuration and Workspace Roots
  Vyasa MUST allow users to configure the local filesystem locations that it scans.

  @FR-001-S1
  Scenario: Multiple workspace roots
    Given multiple workspace roots are configured
    When Vyasa scans the workspace
    Then it discovers eligible projects within each configured root

  @FR-001-S2
  Scenario: Excluded directories
    Given exclusion rules are configured
    When the scanner encounters an excluded directory
    Then it does not discover projects beneath that directory

  @FR-001-S3
  Scenario: Missing workspace root
    Given a configured root does not exist or is inaccessible
    When scanning starts
    Then Vyasa reports the problem
    And Vyasa continues scanning other accessible roots

  @FR-001-S4
  Scenario: Invalid configuration
    Given configuration contains an invalid value
    When Vyasa loads the configuration
    Then it reports a useful validation error instead of silently applying an unintended configuration

  @FR-001-S5
  Scenario: No workspace roots
    Given no valid workspace roots are configured
    When Vyasa starts
    Then it reports that workspace discovery is not configured
    And it does not scan unintended filesystem locations
