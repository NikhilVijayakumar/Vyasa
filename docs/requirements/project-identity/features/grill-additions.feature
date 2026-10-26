@project-identity @proposed
Feature: Project Identity and Review Candidates — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q2
  Scenario Outline: Remote URL forms normalize to one identity
    Given a repository whose remote origin is <url>
    When Vyasa derives its identity
    Then the normalized remote identity is <identity>

    Examples:
      | url | identity |
      | git@github.com:Acme/Tool.git | github.com/acme/tool |
      | https://github.com/acme/tool | github.com/acme/tool |
      | https://user:token@github.com/acme/tool.git | github.com/acme/tool |
      | ssh://git@bitbucket.org/Acme/Tool.git | bitbucket.org/acme/tool |

  @Q12
  Scenario: A local path is not a remote identity
    Given a repository whose remote origin is a local filesystem path
    When Vyasa derives its identity
    Then the repository is treated as having no remote

  @Q4 @Q6
  Scenario: A renamed remote keeps the project
    Given a registered repository whose remote is renamed on its host
    When the scanner rediscovers it at the same path
    Then the project identifier is unchanged
    And the new remote identity is stored as an alias
    And a remote_changed event is recorded

  @Q3
  Scenario: A fork is a different repository
    Given a repository whose origin differs from its upstream remote
    When Vyasa derives its identity
    Then the upstream is recorded as a related identity
    And the two are not merged

  @Q7 @Q13
  Scenario: Two checkouts of one repository are flagged
    Given two directories have the same normalized remote
    When Vyasa scans both
    Then one repository with two checkouts exists
    And a duplicate-checkout candidate is flagged with its rule and evidence

  @Q8
  Scenario: Conflicting evidence stays unresolved
    Given a path matches one known project and its remote matches another
    When Vyasa processes the repository
    Then no project is created or merged silently
    And the candidate is reported as identity_unresolved with both pieces of evidence

  @Q14
  Scenario: Inaccessible projects are never declared obsolete
    Given a project whose repository cannot be read
    When the portfolio is reviewed
    Then the project is not flagged as obsolete for that reason
