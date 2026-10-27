@FR-021 @P1 @file-composition
Feature: File Composition
  Vyasa MUST report how many files of a checkout are code, documentation, and other, using file names only.

  @FR-021-S1
  Scenario: Counts agree
    Given a checkout with 3 files of a recognized code extension, 2 documentation files, and 4 files of other types
    When Vyasa scans it
    Then the counts are 3 code, 2 documentation, 4 other, and 9 total

  @FR-021-S2
  Scenario: Unknown type is other
    Given a checkout containing only files with an unrecognized extension
    When Vyasa scans it
    Then every file is counted as other
    And no file is counted as code

  @FR-021-S3
  Scenario: Documentation only
    Given a complete count with documentation files and no code files
    When Vyasa derives the indicator
    Then documentation_only is true

  @FR-021-S4
  Scenario: Documentation and code
    Given a complete count with both documentation files and code files
    When Vyasa derives the indicator
    Then documentation_only is false

  @FR-021-S5
  Scenario: Empty checkout
    Given a checkout with no files
    When Vyasa scans it
    Then all counts are zero and the count is complete
    And documentation_only is false

  @FR-021-S6
  Scenario: Bound reached
    Given a checkout with more files than the count walk may visit
    When Vyasa scans it
    Then the counts are marked partial and name the limit that stopped the walk
    And documentation_only is unknown

  @FR-021-S7
  Scenario: Unreadable directory
    Given a directory inside the checkout cannot be read
    When Vyasa scans it
    Then the count is marked partial
    And the scan of other projects continues

  @FR-021-S8
  Scenario: Symlinks are not followed
    Given a directory symlink inside the checkout points outside the configured roots
    When Vyasa scans it
    Then no file behind the symlink is counted

  @FR-021-S9
  Scenario: Excluded directories
    Given a checkout with a vendored dependency directory named in the exclusion rules
    When Vyasa scans it
    Then files in that directory are not counted
    And the exclusion rules are recorded as evidence

  @FR-021-S10
  Scenario: Same project in two roots
    Given the same project is checked out under two workspace roots
    When Vyasa scans both
    Then each checkout has its own counts
    And the counts are never summed

  @FR-021-S11
  Scenario: Content is not read
    Given a file named like documentation whose content is source code
    When Vyasa scans it
    Then it is counted as documentation
    And no file content is read
