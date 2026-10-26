@FR-019 @P3 @remote-discovery
Feature: Remote Metadata Inspection
  Vyasa MUST inspect supported remote repository metadata through provider APIs when access and provider capabilities permit.

  @FR-019-S1
  Scenario: Repository metadata
    Given an accessible remote repository
    When its metadata is retrieved
    Then Vyasa records supported repository identity and metadata fields

  @FR-019-S2
  Scenario: README inspection
    Given the provider API exposes a recognized README
    When remote inspection runs
    Then Vyasa extracts only supported metadata using the documented rules

  @FR-019-S3
  Scenario: Manifest inspection
    Given a recognized manifest is available through the provider API
    When remote inspection runs
    Then Vyasa extracts supported dependencies or technology indicators without requiring a checkout

  @FR-019-S4
  Scenario: Unavailable file
    Given a file cannot be retrieved due to permissions, provider limitations, or absence
    When inspection runs
    Then Vyasa distinguishes the known outcome from an unverified assumption wherever possible

  @FR-019-S5
  Scenario: Remote evidence
    Given a fact is extracted remotely
    When returned
    Then the evidence identifies the repository and the relevant path or provider reference where practical

  @FR-019-S6
  Scenario: Consistent metadata model
    Given the same supported fact is extracted from a local repository and a remote provider
    When results are reconciled
    Then both use the shared domain representation while retaining their source provenance
