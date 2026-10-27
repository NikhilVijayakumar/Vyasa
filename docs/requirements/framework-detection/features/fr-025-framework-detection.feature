@FR-025 @P1 @framework-detection
Feature: Framework and technology detection
  Technologies are read from root manifests safely, stored by the scan, and found through project search.

  @FR-025-S1
  Scenario: Python project
    Given a checkout whose pyproject.toml declares fastapi as a dependency and pytest as a dev dependency
    When Vyasa scans it
    Then FastAPI is declared with scope runtime
    And pytest is declared with scope dev

  @FR-025-S2
  Scenario: JavaScript project
    Given a checkout whose package.json lists react in dependencies and jest in devDependencies
    When Vyasa scans it
    Then React is declared with scope runtime and Jest with scope dev

  @FR-025-S3
  Scenario: Rust project
    Given a checkout whose Cargo.toml lists tokio in dependencies and criterion in dev-dependencies
    When Vyasa scans it
    Then Tokio is declared with scope runtime and Criterion with scope dev

  @FR-025-S4
  Scenario: Go project
    Given a checkout whose go.mod requires github.com/gin-gonic/gin directly and another module as indirect
    When Vyasa scans it
    Then Gin is declared with scope runtime
    And the indirect requirement is counted as skipped

  @FR-025-S5
  Scenario: Requirements file scope
    Given a checkout with requirements.txt and requirements-dev.txt
    When Vyasa scans it
    Then dependencies from the first have scope runtime and from the second scope dev

  @FR-025-S6
  Scenario: Scopes are not merged
    Given a package declared in dependencies and again in devDependencies
    When Vyasa scans it
    Then its technology carries both scopes

  @FR-025-S7
  Scenario: Unknown dependency
    Given a manifest listing a dependency that is not in the registry
    When Vyasa scans it
    Then the dependency is recorded
    And no technology is created for it

  @FR-025-S8
  Scenario: Declared constraint is kept
    Given a dependency declared as requests>=2.28,<3
    When Vyasa scans it
    Then its constraint is recorded as written

  @FR-025-S9
  Scenario: Dependency list is capped
    Given a manifest with 300 dependencies
    When Vyasa scans it
    Then 200 are stored and the total 300 is reported

  @FR-025-S10
  Scenario: Oversized manifest
    Given a package.json larger than 1 MiB
    When Vyasa scans it
    Then its status is too_large and it is not parsed

  @FR-025-S11
  Scenario: Symlinked manifest
    Given a package.json that is a symbolic link
    When Vyasa scans it
    Then its status is unreadable and its target is not read

  @FR-025-S12
  Scenario: Binary or non-UTF-8 file
    Given a Cargo.toml that is not valid UTF-8
    When Vyasa scans it
    Then its status is malformed with reason encoding

  @FR-025-S13
  Scenario: Malformed content
    Given a truncated pyproject.toml and a package.json nested a thousand levels deep
    When Vyasa scans it
    Then each is malformed with a fixed reason and no file text is stored

  @FR-025-S14
  Scenario: One bad manifest does not hide another
    Given a malformed package.json and a valid Cargo.toml
    When Vyasa scans it
    Then Rust technologies are declared and the JavaScript manifest is malformed

  @FR-025-S15
  Scenario: Nested manifests are counted, not parsed
    Given a monorepo with package.json files in three subdirectories and none at the root
    When Vyasa scans it
    Then JavaScript has three nested manifests not parsed
    And no JavaScript technology is declared

  @FR-025-S16
  Scenario: Workspace flag
    Given a root package.json that declares workspaces
    When Vyasa scans it
    Then the manifest carries a workspace flag and its members are not expanded

  @FR-025-S17
  Scenario: Complete assessment makes absence known
    Given a complete scan of a checkout with no supported manifests
    When the project details are read
    Then every ecosystem is not_detected

  @FR-025-S18
  Scenario: Partial assessment never reports absence
    Given a scan that stopped at the entry cap before a root manifest was seen
    When the project details are read
    Then the ecosystem is unknown, not not_detected

  @FR-025-S19
  Scenario: Older observation is not assessed
    Given a checkout observed before framework detection existed
    When the project details are read
    Then its frameworks are not_assessed

  @FR-025-S20
  Scenario: Search by technology
    Given indexed projects, one using FastAPI and one using React
    When an agent searches with technology fastapi
    Then only the FastAPI project is returned

  @FR-025-S21
  Scenario: Unknown technology key
    Given an indexed workspace
    When an agent searches with technology fastapii
    Then the request fails with INVALID_INPUT listing the allowed keys

  @FR-025-S22
  Scenario: Nothing is executed
    Given a repository whose setup.py and manifests contain code
    When Vyasa scans it
    Then no repository code is executed or imported and setup.py is not read

  @FR-025-S23
  Scenario: Detection failure is isolated
    Given framework detection raises for one checkout
    When Vyasa scans the workspace
    Then that checkout records a failed observation
    And the other checkouts keep their technologies
