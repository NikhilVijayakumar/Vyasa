@mcp-server @proposed
Feature: MCP Server and Tool Contracts — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q4 @Q5
  Scenario: Invalid input returns a structured error
    Given a tool receives a limit of 1000
    When the request is processed
    Then the result is an error with code INVALID_ARGUMENT
    And no protocol-level failure occurs

  @Q5
  Scenario: Unknown arguments are rejected
    Given a tool receives an argument it does not define
    When the request is processed
    Then the request is rejected with INVALID_ARGUMENT

  @Q5
  Scenario: No tool accepts a filesystem path
    Given a client supplies a path-like value for a project argument
    When the request is processed
    Then the request is rejected
    And no filesystem location is read

  @Q6
  Scenario: A large result is truncated explicitly
    Given a result larger than the response size cap
    When the response is produced
    Then it is truncated at the cap
    And truncated is true and the total count is reported

  @Q11
  Scenario: Tools use a read-only database connection
    Given any query tool
    When it attempts to write to the database
    Then the write fails and no data changes

  @Q7
  Scenario: Local paths are omitted by default
    Given the default configuration
    When project details are requested
    Then the response contains no local filesystem path
    And it states whether a local checkout is available

  @Q7
  Scenario: Local paths can be enabled
    Given expose_local_paths is true
    When project details are requested for a locally available project
    Then the response contains the local path

  @Q12
  Scenario: The tool list matches the committed snapshot
    Given the committed tool-list snapshot
    When the server lists its tools
    Then names, descriptions, and input schemas equal the snapshot

  @Q13
  Scenario: Repository text cannot inject control characters
    Given a project purpose containing control and bidirectional characters
    When context is requested
    Then those characters are removed from the returned value
