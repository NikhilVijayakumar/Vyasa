# profile-context Specification

## Purpose
TBD - created by archiving change be-profile-context. Update Purpose after archive.

## Requirements

### Requirement: The context bundle contains facts, profile, differences, and workflow

The system SHALL return, for one project, a bundle holding its source and observation time, its identity and checkouts with the observed languages, composition, markers, and frameworks exactly as project details show them, the profile as read with its problems, for each checkout the differences between the profile and the observations, and the writer workflow.

#### Scenario: Complete bundle

- **GIVEN** an indexed project with observations and a profile
- **WHEN** its context is requested
- **THEN** the bundle has the source, the checkouts with their observations, the profile, the differences, and the workflow

#### Scenario: No profile is an ordinary state

- **GIVEN** a project without a profile
- **WHEN** its context is requested
- **THEN** the profile is reported absent, the differences are empty of profile-based findings, and the workflow explains how to write one

#### Scenario: Never-assessed observations

- **GIVEN** a checkout observed before the detectors existed
- **WHEN** its context is requested
- **THEN** its observations are reported as not assessed and no difference claims absence

### Requirement: The MCP tool serves the stored observation

The system SHALL provide a read-only MCP tool `get_profile_context` that takes a project identifier, serves the bundle from the stored observation with source `index` and the observation time, and reports an unknown project as `PROJECT_NOT_FOUND`.

#### Scenario: Stored context

- **GIVEN** an indexed project
- **WHEN** an agent calls the tool with its identifier
- **THEN** the bundle's source is `index` and each checkout carries its observed time

#### Scenario: Unknown project

- **GIVEN** an identifier that no project has
- **WHEN** an agent calls the tool
- **THEN** the call fails with `PROJECT_NOT_FOUND`

#### Scenario: Tool is read-only and pinned

- **GIVEN** the tool list
- **WHEN** it is compared with the committed snapshot
- **THEN** the new tool appears with read-only annotations and the snapshot matches

### Requirement: The command scans one checkout live and writes nothing

The system SHALL provide a command `vyasa profile-context [path]` that runs the normal read-only scan of the one repository at the path into a temporary in-memory index, prints the same bundle with source `live_scan`, and writes nothing to the repository, to the real index, or to the configuration.

#### Scenario: Unindexed repository

- **GIVEN** a repository that has never been indexed
- **WHEN** the command is run in it
- **THEN** it prints a bundle with source `live_scan` and the repository's observations

#### Scenario: Nothing is written

- **GIVEN** a repository and a data directory
- **WHEN** the command is run
- **THEN** the repository's files and the data directory are unchanged

#### Scenario: Same shape as the tool

- **GIVEN** a repository that is also indexed
- **WHEN** the command is run and the tool is called
- **THEN** both bundles have the same structure and the same observed facts

#### Scenario: Not a project

- **GIVEN** a directory that is not a recognized project root
- **WHEN** the command is run
- **THEN** it reports that nothing was recognized on standard error and exits with the usage code

#### Scenario: Missing path

- **GIVEN** a path that does not exist
- **WHEN** the command is run
- **THEN** it reports the problem on standard error and exits with the usage code

### Requirement: The bundle holds no absolute path and no file text

The system SHALL omit absolute paths and the text of any repository file from the bundle, other than the validated declared profile values.

#### Scenario: No absolute path

- **GIVEN** a bundle for a repository under an absolute path
- **WHEN** it is serialized
- **THEN** the absolute path of the repository does not appear

#### Scenario: Malformed manifest text

- **GIVEN** a repository with a malformed manifest
- **WHEN** the bundle is produced
- **THEN** only the fixed status and reason code appear

### Requirement: Differences compare only where the observation supports it

The system SHALL compare the declared profile with the observations of each checkout, SHALL report something declared as not detected only when the relevant assessment is complete, SHALL report declared names it cannot match as not comparable, SHALL report detected items as undeclared only when the profile declares that category, and SHALL label every entry as a finding for review.

#### Scenario: Declared language not detected

- **GIVEN** a profile declaring Rust and a complete observation with only Python
- **WHEN** the differences are computed
- **THEN** a finding says the declared language was not detected

#### Scenario: Partial observation makes no claim

- **GIVEN** a profile declaring Rust and a partial observation that found no Rust
- **WHEN** the differences are computed
- **THEN** no finding says Rust was not detected

#### Scenario: Detected language not declared

- **GIVEN** a profile declaring only Python and a complete observation with Python and Go files
- **WHEN** the differences are computed
- **THEN** a finding says Go is detected but not declared

#### Scenario: Nothing declared in the category

- **GIVEN** a profile that declares no languages and a complete observation with Python files
- **WHEN** the differences are computed
- **THEN** no language is reported as undeclared

#### Scenario: Declared framework not detected

- **GIVEN** a profile declaring FastAPI and a complete frameworks assessment without it
- **WHEN** the differences are computed
- **THEN** a finding says the framework was not detected

#### Scenario: Detected technology not declared

- **GIVEN** a profile declaring frameworks and a complete assessment detecting another registry technology that is not ubiquitous
- **WHEN** the differences are computed
- **THEN** a finding says the technology is detected but not declared

#### Scenario: Unmatched declared names

- **GIVEN** a profile declaring PostgreSQL, which the registry and the language labels do not know
- **WHEN** the differences are computed
- **THEN** the name is listed as not comparable and no absence is claimed

#### Scenario: Version 1 technologies

- **GIVEN** a version 1 profile declaring Python, FastAPI, and PostgreSQL
- **WHEN** the differences are computed
- **THEN** Python is compared with the languages, FastAPI with the technologies, and PostgreSQL is not comparable

#### Scenario: Declared OpenSpec not found

- **GIVEN** a profile declaring OpenSpec enabled and a complete marker assessment without an openspec directory
- **WHEN** the differences are computed
- **THEN** a finding says OpenSpec is declared but not detected

#### Scenario: Declared OpenSpec disabled but found

- **GIVEN** a profile declaring OpenSpec disabled and an openspec directory detected
- **WHEN** the differences are computed
- **THEN** a finding says OpenSpec is detected although declared disabled

#### Scenario: Declared agent instruction not found

- **GIVEN** a profile listing `AGENTS.md` as an agent instruction file and a complete marker assessment that did not detect it
- **WHEN** the differences are computed
- **THEN** a finding says the declared file was not detected

#### Scenario: Each entry is a finding for review

- **GIVEN** any difference
- **WHEN** it is returned
- **THEN** it has a fixed code, a severity of `review` or `info`, and a subject, and the profile is not changed

### Requirement: Vyasa starts no agent and writes no profile

The system SHALL NOT launch, configure, or message an agent and SHALL NOT create or change any profile file.

#### Scenario: Profile untouched

- **GIVEN** a repository with a profile and differences
- **WHEN** the command is run
- **THEN** the profile file is byte-identical afterwards and no process other than the scan is started

### Requirement: The workflow tells the agent what to do with the facts

The system SHALL include in every bundle a fixed workflow that tells the agent to read the guide, use observations as evidence and not as declarations, omit what it cannot support, leave observed counts and activity out of the profile, keep secrets out, and ask the maintainer to review.

#### Scenario: Workflow present and fixed

- **GIVEN** any bundle
- **WHEN** it is read
- **THEN** the workflow is the same fixed list of steps and contains no repository text

---
