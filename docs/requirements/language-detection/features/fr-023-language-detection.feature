@FR-023 @P1 @language-detection
Feature: Programming language detection
  A language is reported with a status that says how it was found.

  Scenario: Extensions give files_detected counts
    Given a checkout with 3 .py files and 2 .rs files
    When Vyasa scans it
    Then Python is files_detected with 3 files
    And Rust is files_detected with 2 files

  Scenario: Manifest gives declared without reading content
    Given a checkout with a Cargo.toml and no .rs files
    When Vyasa scans it
    Then Rust is declared
    And Rust is not files_detected

  Scenario: A language found both ways has two evidence rows
    Given a checkout with a pyproject.toml and 2 .py files
    When Vyasa scans it
    Then Python has a declared result and a files_detected result

  Scenario: Histogram agrees with the code count
    Given a checkout with files of recognized code extensions
    When Vyasa scans it
    Then the files_detected counts sum to the code count

  Scenario: Unknown types are ignored
    Given a checkout with a file named data.xyz
    When Vyasa scans it
    Then no language is reported for it

  Scenario: Shared extension maps to one label
    Given a checkout with 2 .h files
    When Vyasa scans it
    Then both are counted under the C/C++ header label

  Scenario: A bound makes absence unknown
    Given a checkout that exceeds the entry cap
    When Vyasa scans it
    Then the result is marked partial
    And a language not found is reported as unknown, not absent
