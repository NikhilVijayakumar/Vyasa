@FR-003 @P1 @project-identity
Feature: Project Identity
  Vyasa MUST maintain stable project identity independently of a project's display name and local filesystem path wherever reliable identity evidence exists.

  @FR-003-S1
  Scenario: Repository with a remote
    Given a repository has a supported, identifiable remote origin
    When Vyasa registers the repository
    Then it derives identity using the documented repository identity rules

  @FR-003-S2
  Scenario: Repository without a remote
    Given a repository has no usable remote
    When Vyasa registers it
    Then it assigns a deterministic local fallback identity

  @FR-003-S3
  Scenario: Directory rename
    Given a registered repository is moved or renamed while its repository identity remains unchanged
    When the scanner rediscovers it
    Then Vyasa updates the local path mapping without creating an unnecessary duplicate

  @FR-003-S4
  Scenario: Duplicate remote identity
    Given two local directories resolve to the same remote identity
    When Vyasa scans them
    Then it detects the duplicate mapping
    And it applies the documented policy rather than silently treating them as unrelated projects

  @FR-003-S5
  Scenario: Ambiguous identity
    Given identity evidence is insufficient to determine whether two records represent the same project
    When Vyasa processes them
    Then it preserves the uncertainty
    And it flags the records for review

  @FR-003-S6
  Scenario: Logical project with multiple repositories
    Given a logical project may span multiple repositories
    When Vyasa discovers those repositories
    Then it does not automatically merge them unless the documented grouping rules establish the relationship
