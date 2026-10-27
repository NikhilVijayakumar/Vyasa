@FR-026 @FR-027 @P1 @project-profile
Feature: Comprehensive profile and agent context
  A version 2 profile declares the project in depth; a context bundle gives an agent the observed facts to write it.

  @FR-026-S1
  Scenario: Version 2 profile is read
    Given a profile of schema version 2 with project, business, scope, and architecture tables
    When Vyasa scans the repository
    Then the declared values are stored under dotted names such as project.summary

  @FR-026-S2
  Scenario: Version 1 profile still works
    Given a profile of schema version 1
    When Vyasa scans the repository
    Then it is read exactly as before

  @FR-026-S3
  Scenario: Unsupported version
    Given a profile of schema version 3
    When Vyasa scans the repository
    Then the profile is reported unsupported and unrelated extraction continues

  @FR-026-S4
  Scenario: One bad field does not hide the others
    Given a version 2 profile with an invalid lifecycle status and a valid summary
    When Vyasa scans the repository
    Then the summary is kept and the lifecycle problem is reported

  @FR-026-S5
  Scenario: Unknown field
    Given a version 2 profile with a field that is not in the schema
    When Vyasa scans the repository
    Then the field is reported as unknown and dropped

  @FR-026-S6
  Scenario: Declared ids never drive identity
    Given a version 2 profile whose project.id equals another project's declared id
    When Vyasa scans both repositories
    Then they remain separate projects
    And each declared id is shown only as a declared label

  @FR-026-S7
  Scenario: Credentials in a URL are rejected
    Given a version 2 profile with a description containing a URL with a password
    When Vyasa scans the repository
    Then the description is dropped and reported

  @FR-026-S8
  Scenario: Contact reference is not an email
    Given a version 2 profile whose owner contact reference is an email address
    When Vyasa scans the repository
    Then the contact reference is dropped and reported

  @FR-026-S9
  Scenario: Paths must be repository-relative
    Given a version 2 profile whose architecture document is an absolute path
    When Vyasa scans the repository
    Then that field is dropped and reported

  @FR-026-S10
  Scenario: Lists and tables are bounded
    Given a version 2 profile with 40 capabilities
    When Vyasa scans the repository
    Then the capabilities field is dropped and reported as too long

  @FR-026-S11
  Scenario: Guide describes version 2
    Given an agent calls the profile guide
    When the guide is returned
    Then it lists every version 2 field with its limits and allowed values and states that version 1 is still read

  @FR-027-S1
  Scenario: Context from the stored observation
    Given an indexed project with observations and a profile
    When an agent asks for the profile context over MCP
    Then it receives the checkout facts, the profile as read, the differences, and the writer workflow
    And the source is stored with its observed time

  @FR-027-S2
  Scenario: Context from a live scan
    Given a repository that has not been indexed
    When an agent runs the profile-context command in it
    Then the command prints the same bundle from a live read-only scan
    And the source is live_scan
    And nothing is written to the real index or the repository

  @FR-027-S3
  Scenario: Not a project
    Given a directory that is not a recognized project
    When an agent runs the profile-context command in it
    Then the command reports that nothing was recognized and exits with a usage error

  @FR-027-S4
  Scenario: No absolute path and no file text
    Given any profile context
    When it is read
    Then it contains no absolute path and no file text

  @FR-027-S5
  Scenario: Declared language not detected
    Given a profile declaring Rust and a complete observation with only Python
    When the differences are computed
    Then a finding says the declared language was not detected

  @FR-027-S6
  Scenario: Partial observation makes no absence claim
    Given a profile declaring Rust and a partial observation that found no Rust
    When the differences are computed
    Then no finding says Rust was not detected

  @FR-027-S7
  Scenario: Detected but undeclared technology
    Given a profile declaring frameworks and a complete observation that detects another registry technology
    When the differences are computed
    Then a finding says the technology is detected but not declared

  @FR-027-S8
  Scenario: Unmatched declared names are not compared
    Given a profile declaring a framework that is not in the registry
    When the differences are computed
    Then the name is listed as not comparable and no absence is claimed

  @FR-027-S9
  Scenario: Declared OpenSpec not found
    Given a profile declaring OpenSpec enabled and a complete observation without an openspec directory
    When the differences are computed
    Then a finding says OpenSpec is declared but not detected

  @FR-027-S10
  Scenario: Profile is never changed
    Given a profile with differences
    When the context is produced
    Then the profile file is unchanged and no agent is started

  @FR-027-S11
  Scenario: No profile is an ordinary state
    Given a project without a profile
    When the context is produced
    Then the profile is reported absent and the workflow explains how to write one
