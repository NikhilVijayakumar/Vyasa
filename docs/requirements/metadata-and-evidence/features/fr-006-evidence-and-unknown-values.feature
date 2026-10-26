@FR-006 @P1 @metadata-and-evidence
Feature: Evidence and Unknown Values
  Vyasa MUST make the origin and certainty of extracted metadata understandable to users and calling agents.

  @FR-006-S1
  Scenario: Evidence-backed fact
    Given a metadata field is derived from a repository file
    When the fact is returned
    Then the response includes an evidence reference identifying the relevant source wherever practical

  @FR-006-S2
  Scenario: Declared fact
    Given a field is explicitly declared in a recognized project profile
    When returned
    Then Vyasa distinguishes the declared value from independently detected facts

  @FR-006-S3
  Scenario: Unknown value
    Given a field cannot be established
    When returned
    Then Vyasa uses a defined unknown or not-documented state instead of inventing a value

  @FR-006-S4
  Scenario: Missing versus false
    Given a test configuration was not found
    When Vyasa reports test status
    Then it distinguishes “not detected” from a confirmed assertion that the project has no tests

  @FR-006-S5
  Scenario: Stale evidence
    Given a source file has changed since a previous scan
    When its previously extracted facts are queried before a successful refresh
    Then Vyasa exposes their freshness limitations according to the documented freshness policy

  @FR-006-S6
  Scenario: Evidence unavailable
    Given a previous evidence source is no longer accessible
    When the corresponding metadata is queried
    Then Vyasa does not present stale evidence as if it were freshly verified
