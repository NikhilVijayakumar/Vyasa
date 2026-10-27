@FR-023 @P1 @language-detection
Feature: Stored languages and the language filter
  Detected languages are stored by the scan and found through project search without touching the filesystem.

  @FR-023-Q1
  Scenario: Scan stores languages per checkout
    Given a workspace with a Python repository
    When Vyasa scans it
    Then the project details list Python as files_detected for that checkout

  @FR-023-Q2
  Scenario: Search by language
    Given indexed projects, one with Python files and one with only Rust files
    When an agent searches with language Python
    Then only the Python project is returned
    And the result says Python matched as files_detected

  @FR-023-Q3
  Scenario: Search by status
    Given a project with a pyproject.toml and no Python files
    When an agent searches with language Python and status files_detected
    Then the project is not returned
    When an agent searches with language Python and status declared
    Then the project is returned

  @FR-023-Q4
  Scenario: Unknown label is rejected
    Given an indexed workspace
    When an agent searches with language Pyhton
    Then the request fails with INVALID_INPUT
    And the error lists the allowed labels

  @FR-023-Q5
  Scenario: Any present checkout matches
    Given a project with two checkouts, only one containing Go files
    When an agent searches with language Go
    Then the project is returned
    And the details list languages per checkout without summing them

  @FR-023-Q6
  Scenario: Missing checkout is not a match
    Given a project whose only Go checkout is missing
    When an agent searches with language Go
    Then the project is not returned
    And its details still show the last observation marked with the checkout state

  @FR-023-Q7
  Scenario: Partial rescan keeps the language and flags it
    Given a complete observation listing Python
    When a rescan hits the entry cap and finds no Python
    Then the current observation is partial
    And the filter does not report Python as gone
    And the previous complete observation is kept

  @FR-023-Q8
  Scenario: Never-observed checkout is not empty
    Given a checkout indexed before language detection existed
    When the project details are read
    Then its languages are not_observed, not an empty list

  @FR-023-Q9
  Scenario: Detection failure is isolated
    Given detection fails for one checkout
    When Vyasa scans the workspace
    Then that checkout records a failed observation
    And the other checkouts are stored and the run is partial

  @FR-023-Q10
  Scenario: Declared technologies are not overridden
    Given a profile declaring technologies Rust and a tree with only Python files
    When the project details are read
    Then profile technologies shows Rust and languages shows Python as separate fields

  @FR-023-Q11
  Scenario: Query does not walk the filesystem
    Given an indexed project whose files have changed since the scan
    When an agent searches or reads details
    Then the stored observation is returned with its observed time
