@FR-021 @P1 @file-composition
Feature: Stored composition counts and the documentation_only filter
  Counts are stored by the scan from the same walk as the languages and found through project search.

  @FR-021-Q1
  Scenario: Scan stores counts with the languages
    Given a workspace with a repository of 3 Python files and 2 Markdown files
    When Vyasa scans it
    Then the project details show 3 code, 2 documentation, and 0 other files for that checkout
    And the language counts sum to the code count

  @FR-021-Q2
  Scenario: Documentation-only project is found
    Given indexed projects, one with only Markdown files and one with Python files
    When an agent searches with documentation_only true
    Then only the Markdown project is returned

  @FR-021-Q3
  Scenario: Code project is found by false
    Given the same indexed projects
    When an agent searches with documentation_only false
    Then only the Python project is returned

  @FR-021-Q4
  Scenario: Partial count matches neither value
    Given a checkout whose count stopped at the entry cap
    When an agent searches with documentation_only true or false
    Then the project is returned for neither
    And its details show the indicator as unknown with the bound

  @FR-021-Q5
  Scenario: Any active checkout matches
    Given a project with two active checkouts, one documentation-only and one with code
    When an agent searches with documentation_only true
    Then the project is returned
    And the details give counts per checkout without a total

  @FR-021-Q6
  Scenario: Not counted is not zero
    Given a checkout observed before counts existed
    When the project details are read
    Then its composition is not_counted with no numbers

  @FR-021-Q7
  Scenario: Failed observation has no counts
    Given a checkout whose detection failed
    When the project details are read
    Then its composition is not_counted and the indicator is null

  @FR-021-Q8
  Scenario: Indicator follows the counts
    Given stored counts of 0 code and 4 documentation in a complete observation
    When the project details are read
    Then documentation_only is true

  @FR-021-Q9
  Scenario: Query does not walk the filesystem
    Given an indexed project whose files changed after the scan
    When an agent searches or reads details
    Then the stored counts and their observed time are returned
