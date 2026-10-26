@quality-attributes @proposed
Feature: Quality Attributes — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q3
  Scenario: Every scenario tag is cited by a test
    Given the set of scenario tags in the feature files
    When the traceability check runs
    Then every tag is cited by at least one test
    And any uncited tag is listed

  @Q11
  Scenario: Dependency direction is enforced
    Given the dependency rules between adapters, application, and domain
    When the architecture test runs
    Then no domain module imports an application or adapter module

  @Q5 @Q4
  Scenario: Startup meets the proposed target on the benchmark corpus
    Given a 500-project benchmark index
    When the MCP server starts
    Then it is ready within the proposed startup target
    And the measurement is recorded

  @Q7
  Scenario: A deprecated option warns for one minor version
    Given a configuration option marked deprecated
    When Vyasa loads a configuration that uses it
    Then a deprecation warning is logged

  @Q10
  Scenario: An optional extra is not required for phase 1
    Given an installation without the sheets and remote extras
    When the phase 1 commands run
    Then they work without importing the Google or provider libraries

  @Q14
  Scenario: README commands run
    Given the commands shown in the README
    When the documentation smoke test runs
    Then each command exits successfully
