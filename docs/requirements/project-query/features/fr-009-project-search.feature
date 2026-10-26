@FR-009 @P1 @project-query
Feature: Project Search
  Vyasa MUST support searching the indexed project portfolio using supported metadata fields.

  @FR-009-S1
  Scenario: Name search
    Given the index contains projects
    When a user searches by project name
    Then Vyasa returns matching projects according to documented matching rules

  @FR-009-S2
  Scenario: Technology search
    Given multiple projects declare or detect a supported technology
    When a user searches for that technology
    Then Vyasa returns the matching projects and indicates the evidence for the match

  @FR-009-S3
  Scenario: Combined filters
    Given the search interface supports multiple filters
    When a query combines technology and documentation criteria
    Then results satisfy all specified filter conditions according to the documented semantics

  @FR-009-S4
  Scenario: Empty result
    Given no project matches the search
    When the query is executed
    Then Vyasa returns an empty result set with an understandable response

  @FR-009-S5
  Scenario: Match provenance
    Given a project matches because of a particular field
    When the search result is returned
    Then the response identifies the matching metadata and its evidence where practical

  @FR-009-S6
  Scenario: Stable ordering
    Given the same indexed data and query are used
    When equivalent searches run
    Then results follow a documented, deterministic ordering policy
