@FR-024 @P1 @project-markers
Feature: Project marker detection
  Markers are found from names and directories only, stored by the scan, and found through project search.

  @FR-024-S1
  Scenario: README at the root
    Given a checkout with a README.md at its root
    When Vyasa scans it
    Then the readme marker is detected with the path README.md

  @FR-024-S2
  Scenario: README below the root is not a root README
    Given a checkout whose only README is in a subdirectory
    When Vyasa scans it
    Then the readme marker is not detected

  @FR-024-S3
  Scenario: Documentation directory
    Given a checkout with a docs directory at its root
    When Vyasa scans it
    Then the docs marker is detected with the path docs

  @FR-024-S4
  Scenario: Agent instruction files with scope
    Given a checkout with AGENTS.md at the root and CLAUDE.md in a subdirectory
    When Vyasa scans it
    Then agent_instructions is detected with both paths
    And one has scope root and the other the nested directory

  @FR-024-S5
  Scenario: OpenSpec indicators stay separate
    Given a checkout with an openspec directory containing specs but no config file
    When Vyasa scans it
    Then openspec_directory and openspec_specs are detected
    And openspec_config and openspec_changes are not detected

  @FR-024-S6
  Scenario: Tests by directory and by name
    Given a checkout with a tests directory and a file service_test.go
    When Vyasa scans it
    Then the tests marker is detected with both matching rules recorded

  @FR-024-S7
  Scenario: Evidence paths are capped
    Given a checkout with 30 files named like tests
    When Vyasa scans it
    Then 20 paths are stored and the total 30 is reported

  @FR-024-S8
  Scenario: Complete assessment makes absence known
    Given a complete scan of a checkout with no markers
    When the project details are read
    Then every marker is not_detected

  @FR-024-S9
  Scenario: Partial assessment never reports absence
    Given a scan that stopped at the entry cap before finding a README
    When the project details are read
    Then the readme marker is unknown, not not_detected

  @FR-024-S10
  Scenario: Older observation is not assessed
    Given a checkout observed before marker detection existed
    When the project details are read
    Then its markers are not_assessed and none is reported not_detected

  @FR-024-S11
  Scenario: Search by marker
    Given indexed projects, one with tests and one without
    When an agent searches with marker tests
    Then only the project with tests is returned

  @FR-024-S12
  Scenario: Search for absence
    Given a complete observation without a README and a partial one without a README
    When an agent searches with marker readme and marker_state not_detected
    Then only the project with the complete observation is returned

  @FR-024-S13
  Scenario: Unknown marker name is rejected
    Given an indexed workspace
    When an agent searches with marker readmee
    Then the request fails with INVALID_INPUT listing the allowed markers

  @FR-024-S14
  Scenario: No absolute path is stored or returned
    Given any scanned checkout
    When the project details are read
    Then no marker path is absolute

  @FR-024-S15
  Scenario: Detection failure is isolated
    Given marker detection fails for one checkout
    When Vyasa scans the workspace
    Then that checkout records a failed observation
    And the other checkouts keep their markers
