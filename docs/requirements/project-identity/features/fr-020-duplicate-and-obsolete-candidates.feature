@FR-020 @P1 @project-identity
Feature: Duplicate and Obsolete Candidates
  Vyasa MUST help users identify potentially duplicate or obsolete projects without automatically performing destructive actions.

  @FR-020-S1
  Scenario: Potential duplicate
    Given two project records share identity or metadata indicators that satisfy documented duplicate rules
    When the portfolio is reviewed
    Then Vyasa flags the candidates for human review

  @FR-020-S2
  Scenario: Possible obsolete project
    Given a project has explicit lifecycle metadata or defined review indicators suggesting it may be obsolete
    When the portfolio is reviewed
    Then Vyasa identifies it as a candidate for review

  @FR-020-S3
  Scenario: Insufficient evidence
    Given a project has not been scanned recently or its repository is inaccessible
    When the portfolio is reviewed
    Then Vyasa does not declare the project obsolete solely because its current state could not be verified

  @FR-020-S4
  Scenario: Human decision
    Given a candidate has been flagged
    When a user reviews it
    Then Vyasa does not automatically delete, archive, or modify the project

  @FR-020-S5
  Scenario: Explainable flag
    Given a project is flagged for review
    When the result is retrieved
    Then Vyasa exposes the deterministic criteria and evidence supporting the flag. ---
