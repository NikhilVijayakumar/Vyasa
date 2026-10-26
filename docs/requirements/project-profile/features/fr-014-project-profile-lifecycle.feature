@FR-014 @P1 @project-profile
Feature: Project Profile Lifecycle
  Vyasa MUST distinguish machine-generated draft information from project-maintained canonical information.

  @FR-014-S1
  Scenario: No canonical profile
    Given a repository has no recognized canonical project profile
    When scanned
    Then Vyasa extracts available metadata without pretending that a canonical profile exists

  @FR-014-S2
  Scenario: Optional draft generation
    Given draft generation is enabled and a repository lacks a profile
    When draft generation runs
    Then it creates a draft containing only supported extracted facts and clearly identifies missing information

  @FR-014-S3
  Scenario: Ignored draft
    Given the agreed draft policy uses a git-ignored file
    When a draft is generated
    Then the draft follows that policy
    And the draft does not unintentionally become a committed project artifact

  @FR-014-S4
  Scenario: Existing canonical profile
    Given a repository contains a recognized canonical profile
    When Vyasa scans it
    Then it reads supported fields without overwriting the file

  @FR-014-S5
  Scenario: Conflicting canonical and detected values
    Given canonical profile values differ from detected facts
    When metadata is returned
    Then Vyasa preserves source provenance
    And Vyasa follows documented field precedence rules

  @FR-014-S6
  Scenario: Human edits
    Given a maintainer edits canonical project metadata
    When the project is rescanned
    Then the maintained values are read according to the documented schema and no automatic replacement occurs
