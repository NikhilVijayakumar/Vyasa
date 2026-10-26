@FR-018 @P3 @remote-discovery
Feature: Remote Repository Discovery
  Vyasa MUST support discovering eligible repositories through configured GitHub and Bitbucket Cloud APIs.

  @FR-018-S1
  Scenario: GitHub public repositories
    Given the configured GitHub discovery scope includes accessible public repositories
    When discovery runs
    Then Vyasa retrieves the repositories permitted by that scope

  @FR-018-S2
  Scenario: Authenticated repository access
    Given valid credentials and appropriate permissions are configured
    When discovery runs
    Then Vyasa retrieves repositories accessible to the configured account or organization scope

  @FR-018-S3
  Scenario: Bitbucket Cloud repositories
    Given valid Bitbucket Cloud credentials and repository permissions are configured
    When discovery runs
    Then Vyasa retrieves accessible repositories within the configured scope

  @FR-018-S4
  Scenario: Pagination
    Given a provider returns results across multiple pages
    When discovery runs
    Then Vyasa processes all pages required by the configured scope, subject to provider limits and failures

  @FR-018-S5
  Scenario: API rate limits
    Given a provider rate limit is reached
    When discovery continues
    Then Vyasa follows the documented retry or stop policy
    And Vyasa records the incomplete outcome

  @FR-018-S6
  Scenario: Authentication failure
    Given credentials are missing, expired, or unauthorized
    When discovery runs
    Then Vyasa reports an access failure rather than returning an empty successful result

  @FR-018-S7
  Scenario: No cloning
    Given remote discovery is requested
    When repositories are enumerated
    Then Vyasa does not clone or check out repositories solely to perform discovery
