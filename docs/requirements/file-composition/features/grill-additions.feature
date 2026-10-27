@file-composition @proposed
Feature: File Composition — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q4
  Scenario: Count walk has its own entry cap
    Given a checkout with 20,000 files outside excluded directories
    When Vyasa scans it
    Then the count is complete
    And the inventory used by the other detectors is still bounded by its own cap

  @Q5
  Scenario: Classification data is versioned
    Given the classification data changes version
    When Vyasa scans an unchanged checkout
    Then the previous observation is marked stale
    And the new observation records the new data version

  @Q6
  Scenario: One walk for languages and counts
    Given a checkout with files of a recognized code extension
    When Vyasa scans it
    Then the code count equals the sum of the language histogram

  @Q7
  Scenario: Extension case is ignored
    Given a checkout with files named a.MD and b.md
    When Vyasa scans it
    Then both are counted as documentation

  @Q8
  Scenario: Counts are not exported
    Given counts exist for a project
    When the shared registry is synchronized
    Then the counts are not written to the registry
