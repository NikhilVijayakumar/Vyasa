@FR-013 @P1 @mcp-server
Feature: MCP Interface
  Vyasa MUST expose its supported Phase 1 capabilities through a documented MCP interface.

  @FR-013-S1
  Scenario: Tool discovery
    Given an MCP client connects successfully
    When it lists the available tools
    Then it can discover the supported tool names, descriptions, and input schemas

  @FR-013-S2
  Scenario: Valid request
    Given a tool receives valid input
    When the request is processed
    Then the response conforms to its documented output contract

  @FR-013-S3
  Scenario: Invalid input
    Given a tool receives invalid input
    When the request is processed
    Then Vyasa returns a structured validation error

  @FR-013-S4
  Scenario: Unknown project
    Given a project-specific tool receives an unknown project identifier
    When the request is processed
    Then Vyasa reports a not-found outcome rather than returning another project's details

  @FR-013-S5
  Scenario: Operational failure
    Given a storage or scanning error prevents a request from completing
    When the error is returned
    Then the response communicates the failure without exposing secrets or sensitive local configuration

  @FR-013-S6
  Scenario: Read-only behaviour
    Given an agent uses ordinary project query tools
    When the tools execute
    Then they do not modify project source files or maintained project metadata

  @FR-013-S7
  Scenario: Refresh isolation
    Given an authorized client invokes the optional refresh operation
    When the index is refreshed
    Then only generated index and scan state are updated according to the defined policy
