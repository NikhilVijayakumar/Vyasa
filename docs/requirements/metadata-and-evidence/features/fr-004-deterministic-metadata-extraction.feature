@FR-004 @P1 @metadata-and-evidence
Feature: Deterministic Metadata Extraction
  Vyasa MUST extract supported project metadata through documented, deterministic rules applied to recognized repository sources.

  @FR-004-S1
  Scenario: Project name
    Given a project has a recognized canonical name in an authoritative source
    When Vyasa extracts metadata
    Then it uses that name according to the documented source precedence rules

  @FR-004-S2
  Scenario: Explicit purpose
    Given a project purpose is explicitly documented in a recognized source
    When Vyasa extracts metadata
    Then it records the documented value with its source

  @FR-004-S3
  Scenario: Missing purpose
    Given no recognized source documents the project purpose
    When Vyasa extracts metadata
    Then it marks the purpose as unknown or not documented

  @FR-004-S4
  Scenario: Technology detection
    Given a project contains a recognized manifest declaring a supported dependency or framework
    When Vyasa scans it
    Then it records the technology according to the corresponding detection rule

  @FR-004-S5
  Scenario: Unsupported evidence
    Given a technology is mentioned only in an arbitrary text file that is not a recognized evidence source for that technology
    When Vyasa scans the project
    Then it does not automatically report the technology as a confirmed dependency

  @FR-004-S6
  Scenario: Conflicting sources
    Given multiple recognized sources provide conflicting values for a field
    When Vyasa extracts metadata
    Then it follows a documented precedence policy or reports the conflict rather than silently choosing an arbitrary value

  @FR-004-S7
  Scenario: Deterministic output
    Given repository files and configuration remain unchanged
    When equivalent scans run under the same detector version
    Then the extracted facts remain consistent

  @FR-004-S8
  Scenario: No LLM dependency
    Given the local indexing pipeline runs
    When metadata is extracted and search results are generated
    Then no LLM is required to infer or fabricate project metadata
