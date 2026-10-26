@FR-010 @P1 @project-query
Feature: Project Details and Context
  Vyasa MUST provide detailed metadata and a concise, structured context view for a selected project.

  @FR-010-S1
  Scenario: Project details
    Given a valid project identifier is provided
    When its details are requested
    Then Vyasa returns available metadata, local availability information, and freshness status

  @FR-010-S2
  Scenario: Unknown project identifier
    Given an identifier does not resolve to a known project
    When details are requested
    Then Vyasa returns a clear not-found result

  @FR-010-S3
  Scenario: Context retrieval
    Given a project is indexed
    When its context is requested
    Then Vyasa returns a structured summary of available identity, purpose, technologies, documentation, conventions, tests, and repository information

  @FR-010-S4
  Scenario: Limited information
    Given only partial metadata is available
    When context is requested
    Then Vyasa returns the known fields and explicitly marks missing fields rather than failing the entire request

  @FR-010-S5
  Scenario: Agent consumption
    Given an MCP client requests project context
    When the response is produced
    Then the structure is suitable for programmatic consumption
    And the structure does not require parsing a free-form narrative to recover individual facts

  @FR-010-S6
  Scenario: Local accessibility
    Given a project is registered but its repository is not available on the current device
    When context is requested
    Then Vyasa distinguishes known shared metadata from locally accessible repository content
