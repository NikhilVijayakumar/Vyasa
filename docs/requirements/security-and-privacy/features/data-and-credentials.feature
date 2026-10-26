@SEC @P1 @security-and-privacy
Feature: Data minimization, credentials, and logging
  Vyasa keeps only what it needs, keeps secrets out of every store, and says so in tests.

  @SEC-002 @SEC-003
  Scenario: Document bodies are not stored
    Given a README with distinctive text
    When the project is indexed
    Then the database does not contain that text
    And only the extracted values and evidence references are stored

  @SEC-005 @SEC-010
  Scenario: A secret-like value is never persisted
    Given a configuration file containing a value that looks like a credential
    When the project is scanned
    Then the value appears in no observation, evidence, scan result, or error
    And a generic sensitive-value finding may be reported

  @SEC-007
  Scenario: Evidence uses repository-relative paths
    Given an observation from a file in a repository
    When its evidence is stored
    Then the evidence path is relative to the repository root

  @SEC-008 @SEC-009
  Scenario: A new field is not exported until classified
    Given a field added to the project record without an export classification
    When the registry export is built
    Then the field is not exported

  @SEC-019
  Scenario: Local files are restricted to the current user
    Given a new data directory on a POSIX system
    When Vyasa creates its database and logs
    Then the directory mode is 0700
    And the files are readable only by the current user

  @SEC-020
  Scenario: Credentials are not in the database
    Given configured provider and registry credentials
    When the database is inspected
    Then no credential value is present

  @SEC-039
  Scenario: Secrets are redacted from logs and errors
    Given a remote URL containing a token
    When an error mentioning the URL is logged
    Then the token is redacted

  @SEC-048
  Scenario: A missing security setting does not broaden access
    Given a configuration with an absent or malformed security setting
    When Vyasa loads it
    Then the stricter default applies
    And a validation message is reported

  @SEC-051
  Scenario: Later-phase integrations are off until configured
    Given a fresh installation
    When Vyasa starts
    Then Google Sheets and provider integrations are disabled
