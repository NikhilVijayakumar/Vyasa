@security-and-privacy @proposed
Feature: Security and Privacy — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q4
  Scenario: Control and bidirectional characters are stripped from returned text
    Given repository-derived text containing control and bidirectional characters
    When it is returned through MCP
    Then those characters are removed

  @Q5
  Scenario: Known token shapes are redacted in logs
    Given a log message containing a GitHub token and an Authorization header
    When the message is written
    Then both are replaced by a redaction marker

  @Q6
  Scenario: Non-public hosts stay local by default
    Given a project whose remote is on an internal host
    When synchronization runs
    Then the remote URL is not exported

  @Q10
  Scenario: The phase 1 suite passes with sockets blocked
    Given all outbound connections fail
    When the phase 1 test suite runs
    Then every test passes

  @Q7
  Scenario: Retention limits are applied
    Given more than 50 scan runs older than 90 days
    When retention runs
    Then the oldest runs beyond both limits are removed
    And durable identity events are kept

  @Q12
  Scenario: The security gate fails on a single leak
    Given a sentinel value that appears in an export
    When the security gate command runs
    Then the gate fails and names the leak
