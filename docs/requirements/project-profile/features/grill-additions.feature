@project-profile @proposed
Feature: Project Profile Lifecycle — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q6
  Scenario: A draft is excluded locally, not through a tracked file
    Given draft generation is requested for a repository without a profile
    When the draft is written
    Then the only file created is .vyasa/project-profile.draft.toml
    And a rule is added to .git/info/exclude
    And no tracked file is modified

  @Q6
  Scenario: An existing draft is not overwritten
    Given a draft file already exists
    When draft generation is requested without force
    Then the existing draft is left unchanged
    And the user is told why

  @Q3
  Scenario: An absolute path in a profile is rejected
    Given a profile whose documentation entry point is an absolute path
    When the profile is validated
    Then that field is reported invalid with its field path
    And other valid fields are still used

  @Q4
  Scenario: An unsupported schema version marks the profile unsupported
    Given a profile declaring a schema version Vyasa does not support
    When the repository is scanned
    Then the profile is reported as unsupported
    And unrelated metadata is still extracted

  @Q5
  Scenario: A declared technology no manifest confirms is visible
    Given a profile declares a technology that no manifest shows
    When the project context is requested
    Then the technology appears in the declared list
    And it is absent from the detected list with a note

  @Q11
  Scenario: A scan leaves the repository byte-identical
    Given a repository with and without a canonical profile
    When it is scanned
    Then a hash of the whole working tree is unchanged
