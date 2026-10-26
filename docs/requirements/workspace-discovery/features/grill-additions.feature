@workspace-discovery @proposed
Feature: Workspace Discovery and Scan Reporting — scenarios from the grill
  Scenarios derived from grill recommendations. They are proposals until the
  recommendation they cite is confirmed.

  @Q8
  Scenario: Overlapping roots are normalized
    Given a configured root is nested inside another configured root
    When Vyasa loads the configuration
    Then the nested root is dropped with a warning
    And each repository is discovered once

  @Q7 @Q18
  Scenario: No usable root fails the run explicitly
    Given every configured root is missing or inaccessible
    When a scan is requested
    Then no filesystem location is scanned
    And a failed run with reason not_configured is recorded

  @Q6
  Scenario: A directory symlink is not followed by default
    Given a directory symlink inside a root points outside the configured roots
    When Vyasa scans the root
    Then the symlink target is not traversed
    And the candidate is reported as skipped_by_policy

  @Q6
  Scenario: Following symlinks still rejects targets outside the roots
    Given follow_symlinks is enabled
    And a symlink points to a directory outside every configured root
    When Vyasa scans the root
    Then the target is not traversed
    And the rejection is reported with a reason code

  @Q14
  Scenario: A hit limit is not reported as absence
    Given a repository holds more inventory entries than the configured limit
    When Vyasa inspects the repository
    Then the result names the limit that was hit
    And indicators not reached are reported as not assessed rather than not detected

  @Q15
  Scenario: Reports are ordered deterministically
    Given an unchanged workspace
    When it is scanned twice
    Then both reports list the same projects in the same order

  @Q4
  Scenario: A submodule is not a separate project
    Given a repository contains a Git submodule
    When Vyasa scans the repository
    Then the submodule is recorded as a component association of the parent
    And no separate project is created for it

  @Q13
  Scenario: Repository-defined commands are never executed
    Given a repository configuration names a command to run on file system events
    When Vyasa reads its Git metadata
    Then that command is not executed
