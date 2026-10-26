@SEC @P1 @security-and-privacy
Feature: Filesystem and repository boundaries
  Vyasa reads only inside configured roots and never changes a repository during an ordinary scan.

  @SEC-011 @SEC-012
  Scenario: A path that escapes the root is rejected
    Given a candidate path that resolves outside every configured root
    When the scanner validates it
    Then the path is rejected and reported

  @SEC-013
  Scenario: Directory symlinks are not followed by default
    Given a directory symlink inside a configured root
    When the scanner traverses the root
    Then the symlink is not followed

  @SEC-015
  Scenario: Limits are enforced and reported
    Given a file larger than the configured size limit
    When a detector needs to read it
    Then the file is skipped
    And the result says it was skipped rather than absent

  @SEC-017
  Scenario: Paths are revalidated when accessed
    Given a path that was valid at discovery
    And it is replaced by a symlink to outside the roots before it is read
    When the scanner reads it
    Then the read is refused

  @SEC-016
  Scenario: Paths found inside repository content grant no access
    Given a manifest that names a path outside the configured roots
    When the scanner processes the manifest
    Then that path is not read

  @SEC-014
  Scenario Outline: Excluded locations are never inspected
    Given the default exclusions
    When the scanner meets a directory named <directory>
    Then it does not inspect that directory

    Examples:
      | directory    |
      | node_modules |
      | .venv        |
      | __pycache__  |
      | dist         |

  @NFR-016
  Scenario: An ordinary scan leaves repositories unchanged
    Given a fixture repository tree
    When it is scanned
    Then a hash of the whole tree is unchanged
