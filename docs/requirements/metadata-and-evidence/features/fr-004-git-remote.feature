@FR-004 @P1 @metadata-and-evidence
Feature: Git Remote and Provider
  Vyasa MUST report where a project's Git remote points, without running Git and without keeping credentials.

  @FR-004-S9
  Scenario: Known providers
    Given projects whose origin points at github.com, bitbucket.org, and gitlab.com
    When Vyasa scans them
    Then their providers are github, bitbucket, and gitlab

  @FR-004-S10
  Scenario: Unknown host
    Given a project whose origin points at a self-hosted server
    When Vyasa scans it
    Then its provider is other
    And the host is kept

  @FR-004-S11
  Scenario: Equivalent forms give one identity
    Given the same repository written as an https URL, an ssh URL, and a scp-style address
    When Vyasa scans them
    Then all three report the same host and identity

  @FR-004-S12
  Scenario: Credentials are never kept
    Given an origin URL that embeds a user name and a token
    When Vyasa scans the project
    Then neither appears in anything Vyasa keeps

  @FR-004-S13
  Scenario: Origin is preferred
    Given a project with remotes named origin and upstream
    When Vyasa scans it
    Then the origin remote is reported

  @FR-004-S14
  Scenario: Several remotes and no origin
    Given a project with two remotes and none named origin
    When Vyasa scans it
    Then no remote is chosen
    And the status says ambiguous

  @FR-004-S15
  Scenario: No remote
    Given a project with Git and no remote
    When Vyasa scans it
    Then its provider is none

  @FR-004-S16
  Scenario: Local remote
    Given a project whose remote is a local path
    When Vyasa scans it
    Then its provider is local
    And it has no identity

  @FR-004-S17
  Scenario: Worktree and submodule
    Given a project whose Git entry is a pointer file
    When Vyasa scans it
    Then its remote is unavailable

  @FR-004-S18
  Scenario: Git in a child folder
    Given an Unreal project whose Git lives in its Source folder
    When Vyasa scans it
    Then the remote is read from that folder
