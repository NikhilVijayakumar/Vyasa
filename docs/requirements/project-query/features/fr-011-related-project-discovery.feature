@FR-011 @P1 @project-query
Feature: Related-Project Discovery
  Vyasa MUST support deterministic discovery of potentially related projects.

  @FR-011-S1
  Scenario: Shared technologies
    Given projects share one or more recognized technologies
    When related-project discovery is requested
    Then Vyasa can identify them using the documented relation rules

  @FR-011-S2
  Scenario: Shared explicit dependency
    Given a project declares a dependency on another identifiable project
    When related projects are queried
    Then Vyasa can report that explicit relationship

  @FR-011-S3
  Scenario: No relationship evidence
    Given no configured relation rule establishes a relationship
    When related projects are queried
    Then Vyasa does not invent one

  @FR-011-S4
  Scenario: Explainable result
    Given a related project is returned
    When the result is examined
    Then it explains which supported criteria established the relationship

  @FR-011-S5
  Scenario: Ranking
    Given multiple projects satisfy relation rules
    When ranking is supported
    Then ordering is deterministic and based on documented criteria rather than an LLM-generated similarity judgment
