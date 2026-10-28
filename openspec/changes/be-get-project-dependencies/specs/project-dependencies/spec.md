# Specifications: be-get-project-dependencies (project-dependencies)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-get-project-dependencies`
- **Purpose:** Let an agent read a project's direct dependencies and dependents from recorded evidence.
- **Related proposal:** `proposal.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/internal-dependencies-by-declared-package-name.md`, `knowledge/decisions/partial-results-never-imply-absence.md`

## 2. Capability: project-dependencies

### Purpose

Answer "what does this project depend on" and "what depends on it" without scanning, and say how complete the answer is.

### Scope

The read-only tool `get_project_dependencies`. Direct dependencies of active checkouts from root manifests only.

## ADDED Requirements

### Requirement: The tool lists direct dependencies with their evidence

The system SHALL provide `get_project_dependencies(project_id)` that returns, for the project's active checkouts' latest observation, every stored direct dependency with its name, ecosystem, constraint (or null), scope, and the manifest file name that declared it. Results SHALL be ordered by ecosystem, name, scope, and manifest. An unknown or malformed `project_id` SHALL be a structured error. The tool SHALL read only the index and SHALL NOT return a local path.

#### Scenario: Dependencies with scope and source

- **GIVEN** a project whose `pyproject.toml` declares a runtime and a dev dependency
- **WHEN** an agent asks for its dependencies
- **THEN** both are returned with ecosystem python, their constraints, their scopes, and source pyproject.toml

#### Scenario: Same name in two scopes

- **GIVEN** a package declared as runtime and as dev
- **WHEN** dependencies are requested
- **THEN** two entries are returned, one per scope

#### Scenario: Unknown project

- **GIVEN** an identifier no project has
- **WHEN** the tool is called
- **THEN** it returns PROJECT_NOT_FOUND

#### Scenario: Invalid identifier

- **GIVEN** an empty or non-text identifier
- **WHEN** the tool is called
- **THEN** it returns INVALID_INPUT

#### Scenario: No local path

- **GIVEN** any project
- **WHEN** the tool answers
- **THEN** no value contains a workspace root or an absolute path

### Requirement: A dependency is internal only by exact name in one ecosystem

The system SHALL mark a dependency `internal` when its normalized name equals the declared package name of exactly one other indexed project's active checkout in the same ecosystem, `ambiguous` when several other projects declare it (listing every one), and `external` otherwise. A project SHALL NOT be reported as depending on itself. Matching SHALL NOT use remote identity, path, display name, or another ecosystem. Each internal or ambiguous entry SHALL name the matched project's identifier and display name.

#### Scenario: Internal dependency

- **GIVEN** project A depends on ledger-core and project B's Cargo.toml declares package ledger-core
- **WHEN** A's dependencies are requested
- **THEN** the entry is internal and names B

#### Scenario: Same name in another ecosystem

- **GIVEN** A depends on a Python package named ui and B's package.json declares ui
- **WHEN** A's dependencies are requested
- **THEN** the entry is external

#### Scenario: Ambiguous

- **GIVEN** two projects declare the package ledger-core
- **WHEN** a dependent project's dependencies are requested
- **THEN** the entry is ambiguous and lists both projects

#### Scenario: Not indexed

- **GIVEN** a dependency no indexed project declares
- **WHEN** dependencies are requested
- **THEN** it is external and no project is invented

#### Scenario: Not itself

- **GIVEN** a project whose manifest depends on its own declared name
- **WHEN** dependencies are requested
- **THEN** the entry is external

#### Scenario: Name normalization

- **GIVEN** a dependency written Billing_API and a project declaring billing-api in Python
- **WHEN** dependencies are requested
- **THEN** the entry is internal

#### Scenario: Missing checkout is not a target

- **GIVEN** a project whose only checkout is missing
- **WHEN** another project depends on its package
- **THEN** the dependency is external

### Requirement: The tool lists dependents

The system SHALL return, as `dependents`, the other projects whose active checkouts declare a direct dependency that resolves to this project (internal, or ambiguous including it), with the project identifier, display name, ecosystem, dependency name, constraint, scope, resolution, and declaring manifest. At most 100 entries SHALL be returned, ordered by display name, identifier, ecosystem, scope, and manifest, with the total count and a flag when truncated.

#### Scenario: A dependent

- **GIVEN** B declares package ledger-core and A depends on it
- **WHEN** B's dependents are requested
- **THEN** A is listed with the dependency name, scope, and manifest

#### Scenario: Ambiguous dependent

- **GIVEN** two projects declare ledger-core and A depends on it
- **WHEN** either project's dependents are requested
- **THEN** A is listed and marked ambiguous

#### Scenario: No dependents

- **GIVEN** no other project depends on this one
- **WHEN** dependents are requested
- **THEN** the list is empty and the total is 0

#### Scenario: Truncation

- **GIVEN** 101 projects depend on this one
- **WHEN** dependents are requested
- **THEN** 100 are returned, the total is 101, and truncated is true

### Requirement: Every answer states its coverage

The system SHALL return a coverage object with the status of the observation (`complete`, `partial`, `not_assessed`), the root manifests with their parse status, the number of nested manifests not parsed, whether the declared names of the project's own manifests are recorded, and how many other projects could not be checked as targets or dependents because their observation is partial, not assessed, or lacks declared names. A project with no assessed active checkout SHALL return empty lists and status `not_assessed`. The system SHALL NOT present the result as an exhaustive dependency graph.

#### Scenario: Complete observation

- **GIVEN** a fully walked checkout with one parsed manifest
- **WHEN** dependencies are requested
- **THEN** coverage status is complete and lists the manifest as parsed

#### Scenario: Unparsed manifest

- **GIVEN** a checkout with a malformed package.json and a parsed pyproject.toml
- **WHEN** dependencies are requested
- **THEN** the dependencies of pyproject.toml are returned and coverage lists package.json as malformed

#### Scenario: Partial walk

- **GIVEN** a scan that stopped early
- **WHEN** dependencies are requested
- **THEN** coverage status is partial and an empty list is not read as no dependencies

#### Scenario: Not assessed

- **GIVEN** a project whose observation predates framework detection
- **WHEN** dependencies are requested
- **THEN** the lists are empty and coverage status is not_assessed

#### Scenario: Nested manifests

- **GIVEN** a monorepo with manifests below the root
- **WHEN** dependencies are requested
- **THEN** coverage counts the nested manifests as not parsed

#### Scenario: Names not recorded yet

- **GIVEN** an observation made before declared names were stored
- **WHEN** dependencies are requested
- **THEN** coverage says declared names are unknown for it, and other projects count it as unchecked

### Requirement: The tool is read-only and bounded

The system SHALL register the tool as read-only, SHALL take no path, and SHALL NOT scan, write, or read repository files. It SHALL appear in the committed MCP tool snapshot.

#### Scenario: Read-only

- **GIVEN** an index
- **WHEN** the tool is called
- **THEN** the index file is unchanged

#### Scenario: Declared in the snapshot

- **GIVEN** the committed tool snapshot
- **WHEN** the tools are listed
- **THEN** get_project_dependencies is present with read-only annotations and a single project_id parameter
