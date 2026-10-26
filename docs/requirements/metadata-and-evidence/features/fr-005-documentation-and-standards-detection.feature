@FR-005 @P1 @metadata-and-evidence
Feature: Documentation and Standards Detection
  Vyasa MUST identify supported documentation, engineering configuration, and agent instruction artifacts.

  @FR-005-S1
  Scenario: README presence
    Given a repository contains a README matching a supported naming rule
    When scanned
    Then Vyasa records its presence and path

  @FR-005-S2
  Scenario: No README
    Given no supported README is found
    When scanned
    Then Vyasa records that the README was not detected

  @FR-005-S3
  Scenario: OpenSpec directory only
    Given a repository contains an OpenSpec-related directory but no valid recognized configuration
    When scanned
    Then Vyasa distinguishes directory presence from valid OpenSpec configuration

  @FR-005-S4
  Scenario: OpenSpec configuration
    Given a repository contains a recognized, valid OpenSpec configuration
    When scanned
    Then Vyasa records the configuration status separately from the presence of specification or change files

  @FR-005-S5
  Scenario: Agent instructions
    Given a repository contains recognized agent instruction files
    When scanned
    Then Vyasa records their supported names and locations

  @FR-005-S6
  Scenario: Test indicators
    Given a repository contains recognized test directories, test files, or test configuration
    When scanned
    Then Vyasa records the detected indicators and the evidence supporting them

  @FR-005-S7
  Scenario: README quality
    Given README quality assessment has not been implemented or assessed
    When a project is queried
    Then Vyasa reports the status as not assessed rather than claiming a subjective quality rating

  @FR-005-S8
  Scenario: Undefined convention
    Given a convention has not been defined well enough to detect reliably
    When the scanner processes a project
    Then Vyasa does not claim that the convention is enabled or disabled
