@DOR @P1 @data-ownership
Feature: Ownership enforcement
  Every mutable field has one authoritative owner, and no process changes a field it does not own.

  @DOR-001
  Scenario: Every persisted field has an owner category
    Given the set of fields that scanning, synchronization, or human editing can change
    When the ownership registry is checked
    Then every such field has an ownership category

  @DOR-002
  Scenario: Values retain their origin
    Given a value extracted by a detector and a value imported from the registry
    When both are stored
    Then each keeps its source type, source reference, actor or detector, and observation time

  @DOR-003
  Scenario: A process cannot overwrite a field another source owns
    Given a field owned by the portfolio maintainer
    When a scanner attempts to write that field
    Then the write is refused
    And the attempt is reported

  @DOR-004
  Scenario: Machine-local data never enters a shared export
    Given machine-local fields hold distinctive values
    When a shared export payload is built
    Then none of those values appear in the payload

  @DOR-005
  Scenario: A draft profile stays separate from the canonical profile
    Given a generated draft profile and a canonical profile for one project
    When the project is scanned
    Then declared values come only from the canonical profile

  @DOR-006
  Scenario: Promotion needs a human decision
    Given a generated draft profile
    When no person has adopted it
    Then Vyasa never treats it as canonical

  @DOR-007
  Scenario: Unresolved conflicts are visible
    Given two owners disagree about a field and no rule resolves it
    When the project is queried
    Then the field status is conflicting
    And both values and their sources are available

  @DOR-008
  Scenario: Derived data is reproducible
    Given the same owned and observed inputs
    When a derived field is computed twice
    Then both results are identical
    And the field is labelled derived

  @DOR-009
  Scenario: A failed operation never destroys valid data
    Given a project with valid indexed values
    When a scan or synchronization fails part way
    Then the previously valid values remain available

  @DOR-010
  Scenario: Invalid external records are rejected before use
    Given a canonical profile or registry record that fails schema validation
    When it is loaded
    Then invalid fields are not accepted into the internal model
    And the validation failures are reported

  @DOR-011
  Scenario: Export uses an allowlist, not the whole record
    Given a project record with a field that is not on the export allowlist
    When the registry export is built
    Then the field is not exported

  @DOR-012
  Scenario: Each adapter is checked against the ownership matrix
    Given the scanner, registry, profile, and provider adapters
    When the ownership conformance tests run
    Then every adapter respects field ownership and conflict policy
