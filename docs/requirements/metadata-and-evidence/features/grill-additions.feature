@metadata-and-evidence @proposed
Feature: Metadata Extraction and Evidence — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q5
  Scenario: README prose is not a purpose
    Given a repository has a README but no profile and no manifest description
    When Vyasa extracts metadata
    Then the purpose is reported as unknown
    And the README is recorded by presence and path only

  @Q6
  Scenario: An import statement is not technology evidence
    Given a source file imports a framework that no recognized manifest declares
    When Vyasa scans the project
    Then the framework is not reported as a technology

  @Q7
  Scenario: Equal-precedence disagreement is a conflict
    Given two recognized sources of equal precedence give different values for a field
    When Vyasa extracts metadata
    Then the field status is conflicting
    And both observations are kept
    And no resolved value is returned

  @Q10
  Scenario: Evidence omits the matched text
    Given a manifest line contains a value that looks like a credential
    When the detector records evidence
    Then the evidence holds the path, key, and fingerprint
    And it does not hold the line text

  @Q14
  Scenario: Output does not depend on directory order
    Given a fixture repository
    When it is scanned with directory entries presented in shuffled order
    Then the normalized output is identical to the unshuffled scan

  @Q11
  Scenario: An oversized YAML file is skipped, not parsed
    Given a YAML configuration larger than the size cap
    When the detector inspects it
    Then the file is reported as skipped by policy
    And no indicator is reported as absent

  @Q12
  Scenario: A detector version change invalidates results
    Given cached results produced by version 1 of a detector
    When version 2 of the detector is installed and a scan runs
    Then the affected observations are recomputed

  @Q16
  Scenario: An undeclared OKF bundle is not detected
    Given a directory of Markdown files with frontmatter but no index declaring okf_version
    When Vyasa scans the repository
    Then OKF is reported as not_detected
