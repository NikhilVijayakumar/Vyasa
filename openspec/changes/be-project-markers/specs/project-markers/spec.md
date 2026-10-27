# Specifications: be-project-markers (project-markers)

## 1. Specification Overview

- **OpenSpec Change ID:** `be-project-markers`
- **Purpose:** Detect README, documentation, agent instruction, OpenSpec, and test markers from names and store them.
- **Related proposal:** `proposal.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/project-marker-observations.md`

## 2. Capability: project-markers

### Purpose

Say which standard project markers a checkout has, how that was established, and when it is not known.

### Scope

Detection from the walk and storage on the observation. Reading is specified in the `project-query` capability.

## ADDED Requirements

### Requirement: Markers come from names and directories

The system SHALL detect the markers `readme`, `docs`, `agent_instructions`, `openspec_directory`, `openspec_config`, `openspec_specs`, `openspec_changes`, and `tests` from file and directory names against versioned rules, and SHALL NOT open any file.

#### Scenario: README at the root

- **GIVEN** a checkout with `README.md` at its root
- **WHEN** it is scanned
- **THEN** `readme` is detected with the path `README.md`

#### Scenario: README name case

- **GIVEN** a root file named `readme.RST`
- **WHEN** it is scanned
- **THEN** `readme` is detected

#### Scenario: Documentation directory

- **GIVEN** a root directory named `docs`
- **WHEN** it is scanned
- **THEN** `docs` is detected with the path `docs`

#### Scenario: Content is not read

- **GIVEN** a file named `notes.txt` whose content is a README
- **WHEN** it is scanned
- **THEN** `readme` is not detected and no file is opened

### Requirement: Location rules per marker

The system SHALL look for `readme`, `docs`, and the OpenSpec markers only at the checkout root, and for `agent_instructions` and `tests` at any depth.

#### Scenario: README below the root

- **GIVEN** a checkout whose only README is in a subdirectory
- **WHEN** it is scanned
- **THEN** `readme` is not detected

#### Scenario: Nested agent instruction file

- **GIVEN** `AGENTS.md` at the root and `CLAUDE.md` in `packages/app`
- **WHEN** it is scanned
- **THEN** `agent_instructions` is detected with both paths
- **AND** one has scope `root` and the other scope `packages/app`

#### Scenario: Nested tests

- **GIVEN** a directory `packages/app/tests`
- **WHEN** it is scanned
- **THEN** `tests` is detected with that path

### Requirement: Tests are detected by directory and file name

The system SHALL detect `tests` from a directory named `tests`, `test`, `__tests__`, or `spec`, or a file whose name matches `test_*.py`, `*_test.py`, `*_test.go`, `*.test.js`, `*.test.ts`, `*.test.jsx`, `*.test.tsx`, `*.spec.js`, `*.spec.ts`, or `*Test.java`, and SHALL record the matching rules.

#### Scenario: Directory and name

- **GIVEN** a `tests` directory and a file `service_test.go`
- **WHEN** it is scanned
- **THEN** `tests` is detected with both rules recorded

#### Scenario: Not a test name

- **GIVEN** a file named `latest.java`
- **WHEN** it is scanned
- **THEN** `tests` is not detected

### Requirement: OpenSpec indicators stay separate

The system SHALL report `openspec_directory`, `openspec_config` (`config.yaml` or `config.yml` inside it), `openspec_specs` (a `specs` entry inside it), and `openspec_changes` (a `changes` entry inside it) as separate markers.

#### Scenario: Directory without config

- **GIVEN** an `openspec` directory containing `specs` but no config file
- **WHEN** it is scanned
- **THEN** `openspec_directory` and `openspec_specs` are detected
- **AND** `openspec_config` and `openspec_changes` are not detected

### Requirement: Three states and unknown on partial walks

The system SHALL report each marker as `detected`, `not_detected` only when the walk was complete, or `unknown` when the walk stopped early and the marker was not found.

#### Scenario: Complete assessment

- **GIVEN** a complete scan of a checkout with no markers
- **WHEN** the markers are read
- **THEN** every marker is `not_detected`

#### Scenario: Partial assessment

- **GIVEN** a scan that stopped at the entry cap before finding a README
- **WHEN** the markers are read
- **THEN** `readme` is `unknown`

#### Scenario: Found despite a partial walk

- **GIVEN** a partial scan that found `tests` before stopping
- **WHEN** the markers are read
- **THEN** `tests` is `detected`

### Requirement: Evidence is relative and capped

The system SHALL store, for each detected marker, the rules version, the matching rules, the total number of matches, and at most 20 repository-relative paths in a stable order, and SHALL NOT store or return an absolute path.

#### Scenario: Cap

- **GIVEN** 30 files named like tests
- **WHEN** it is scanned
- **THEN** 20 paths are stored and the total is 30

#### Scenario: Relative only

- **GIVEN** any scanned checkout
- **WHEN** the markers are read
- **THEN** no path starts with a separator or a drive letter and none contains `..`

#### Scenario: Stable order

- **GIVEN** the same tree created in two orders
- **WHEN** it is scanned each time
- **THEN** the stored paths are equal

### Requirement: Markers are stored on the observation

The system SHALL store markers with the observation of the same walk, so that they share its time, completeness, and retention of the current and previous observation.

#### Scenario: Stored with the observation

- **GIVEN** a repository with a README and tests
- **WHEN** a scan completes
- **THEN** the observation has `readme` and `tests` rows

#### Scenario: Retention

- **GIVEN** a checkout scanned three times
- **WHEN** the third scan completes
- **THEN** only the second and third observations, with their markers, exist

### Requirement: Older and failed observations are not assessed

The system SHALL record the rules version on every assessed observation, and SHALL treat an observation without one, whether made before this change or failed, as not assessed and never as not detected.

#### Scenario: Upgrade

- **GIVEN** an index at the previous version with observations
- **WHEN** it is opened for writing
- **THEN** the observations are unchanged and have no rules version

#### Scenario: Failed observation

- **GIVEN** detection fails for a checkout
- **WHEN** the scan stores it
- **THEN** the observation is failed and has no rules version and no marker rows

### Requirement: Marker rules are validated data

The system SHALL load the marker rules from versioned data and SHALL reject data with a missing or non-integer version, a rule of the wrong shape, an empty name, or a name containing a path separator.

#### Scenario: Valid rules

- **GIVEN** rules with a version and every rule group
- **WHEN** they are loaded
- **THEN** the loaded rules carry the version and lower-cased names

#### Scenario: Malformed rules

- **GIVEN** rules with a missing version or a name with a separator
- **WHEN** they are loaded
- **THEN** loading fails naming the field

### Requirement: Walk reports relative paths and directories

The system SHALL have the checkout walk report relative file paths and directories in a stable order, without changing the names, the stopping bound, or the exclusions it already applies.

#### Scenario: Paths and directories

- **GIVEN** a tree with nested files
- **WHEN** it is walked
- **THEN** the relative paths use forward slashes and list every file and directory entered or found

#### Scenario: Counts unchanged

- **GIVEN** any tree
- **WHEN** it is scanned
- **THEN** the counts and languages equal what they were before this change

### Requirement: Detection failure is isolated

The system SHALL store a failed observation for a checkout whose detection raises, SHALL continue with the other checkouts, and SHALL mark the run partial.

#### Scenario: One checkout fails

- **GIVEN** detection raises for one of two checkouts
- **WHEN** the scan runs
- **THEN** the failing checkout has a failed observation
- **AND** the other checkout keeps its markers and the run is partial

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
