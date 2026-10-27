@FR-022 @P1 @workspace-discovery
Feature: Repository-Provided Ignore File
  Vyasa MUST skip the directories a repository lists in its own ignore file, and MUST NOT let that file widen what is scanned.

  @FR-022-S1
  Scenario: Ignored directory is not scanned
    Given a repository whose ignore file lists a data directory
    When Vyasa scans the repository
    Then it does not enter the data directory
    And the directory is counted as excluded
    And the directory is not reported as a skip

  @FR-022-S2
  Scenario: Bare name matches at any depth
    Given an ignore file listing the name "fixtures"
    When Vyasa scans a repository with fixtures directories at several depths
    Then none of them is entered

  @FR-022-S3
  Scenario: Path from the repository root
    Given an ignore file listing "data/novel/output"
    When Vyasa scans the repository
    Then only that directory is not entered
    And a directory with the same name elsewhere is entered

  @FR-022-S4
  Scenario: Glob characters
    Given an ignore file listing "data/*/cache" and "build-?"
    When Vyasa scans the repository
    Then matching directories are not entered
    And a name with extra characters is entered

  @FR-022-S5
  Scenario: Case is ignored
    Given an ignore file listing "Fixtures"
    When Vyasa scans a repository with a directory named "fixtures"
    Then it is not entered

  @FR-022-S6
  Scenario: Comments and blank lines
    Given an ignore file with comments, blank lines, and one pattern
    When Vyasa reads it
    Then only the pattern applies

  @FR-022-S7
  Scenario: The file cannot widen the scan
    Given an ignore file with a negation, a drive letter, and a path containing ".."
    When Vyasa reads it
    Then each of those lines is reported in a warning and skipped
    And no directory outside the repository is affected

  @FR-022-S8
  Scenario: Valid lines still apply
    Given an ignore file with one invalid line and one valid pattern
    When Vyasa scans the repository
    Then the valid pattern applies
    And the warning names the file and the invalid line

  @FR-022-S9
  Scenario: Oversized file
    Given an ignore file larger than 64 KiB
    When Vyasa reads it
    Then none of its patterns apply
    And a warning says the file was too large

  @FR-022-S10
  Scenario: Only below its own repository
    Given two sibling repositories and an ignore file in the first listing "data"
    When Vyasa scans both
    Then "data" is skipped in the first and entered in the second

  @FR-022-S11
  Scenario: Nested repositories keep enclosing rules
    Given a repository with an ignore file listing "vendor-data", and a nested repository with its own ignore file listing "cache"
    When Vyasa scans the nested repository
    Then both "vendor-data" and "cache" are skipped inside it

  @FR-022-S12
  Scenario: File counts honor the ignore file
    Given a checkout whose ignore file lists a directory holding many files
    When Vyasa counts its files
    Then files in that directory are not counted
    And the evidence records that an ignore file was used, its pattern count, and a digest of its patterns
