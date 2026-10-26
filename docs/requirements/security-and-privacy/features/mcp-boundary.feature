@SEC @P1 @security-and-privacy
Feature: MCP boundary
  Clients receive only requested, bounded data and cannot widen Vyasa's access.

  @SEC-026
  Scenario: No network listener is opened
    Given Vyasa is started for MCP use
    When its open sockets are listed
    Then it listens on no network port

  @SEC-030
  Scenario: Arguments are validated against a schema
    Given a tool argument of the wrong type or beyond its bounds
    When the request is processed
    Then it is rejected with a structured validation error

  @SEC-031
  Scenario: A tool argument cannot select a path or override a root
    Given a tool call that supplies a filesystem path or a workspace root
    When the request is processed
    Then the request is rejected
    And configured roots and exclusions are unchanged

  @SEC-032
  Scenario: Only requested fields are returned
    Given a project with many stored fields
    When a client requests a narrow view
    Then the response contains only the requested fields and necessary evidence

  @SEC-033
  Scenario: Errors do not leak internals
    Given a storage error occurs while handling a request
    When the error is returned
    Then it contains no credential, stack trace, or unnecessary absolute path

  @SEC-034
  Scenario: Ordinary queries cause no external effect
    Given synchronization and remote discovery are configured
    When a client runs search and detail tools
    Then no Google Sheets or provider request is made

  @NFR-020
  Scenario: Repository text is returned as inert data
    Given a project purpose that contains instruction-like text
    When context is requested
    Then the text is returned as a typed value
    And nothing in the text is executed or merged into tool descriptions
