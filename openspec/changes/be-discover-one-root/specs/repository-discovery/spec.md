# Specifications: be-discover-one-root

## 1. Specification Overview

- **OpenSpec Change ID:** `be-discover-one-root`
- **Purpose:** Find the Git repositories under one root and record what happened.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/repository-recognition-and-run-status.md`, `knowledge/architecture/scanning-and-evidence/discovery-and-inspection.md`
- **Team focus:** Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: repository-discovery

### Purpose

Return the repositories under a root, with an outcome for everything that is not one, and a run record.

### Scope

One root per call. No persistence, no identity, no metadata.

## ADDED Requirements

### Requirement: Recognize Git repositories

The system SHALL treat a directory that contains a `.git` directory with a `HEAD` file, or a `.git` file whose first line starts with `gitdir:`, as a repository candidate, and SHALL classify a `.git` file whose target path has a `worktrees` segment as a linked worktree, one with a `modules` segment as a submodule, and any other as a repository.

#### Scenario: Repository with a Git directory

- **GIVEN** a directory containing `.git/HEAD`
- **WHEN** discovery runs
- **THEN** it is reported eligible with kind repository

#### Scenario: Repository at the root

- **GIVEN** the root itself contains `.git/HEAD`
- **WHEN** discovery runs
- **THEN** the root is reported eligible

#### Scenario: Submodule

- **GIVEN** a directory whose `.git` file reads `gitdir: ../.git/modules/lib`
- **WHEN** discovery runs
- **THEN** it is reported eligible with kind submodule

#### Scenario: Linked worktree

- **GIVEN** a directory whose `.git` file points into a `worktrees` directory
- **WHEN** discovery runs
- **THEN** it is reported eligible with kind linked worktree

#### Scenario: Git directory elsewhere

- **GIVEN** a `.git` file that points to a path with neither segment
- **WHEN** discovery runs
- **THEN** it is reported eligible with kind repository

#### Scenario: Ordinary directories are not candidates

- **GIVEN** directories without a `.git` entry
- **WHEN** discovery runs
- **THEN** none of them appears in the repositories or the issues

### Requirement: Nested repositories stay separate

The system SHALL report a repository found inside another repository as its own candidate and SHALL NOT merge them.

#### Scenario: Repository inside a repository

- **GIVEN** a repository containing another repository below it
- **WHEN** discovery runs
- **THEN** both are reported, each with its own path

### Requirement: Every candidate has one closed outcome

The system SHALL give each candidate exactly one outcome from eligible, excluded, inaccessible, malformed, and skipped by policy, with a reason code for every outcome other than eligible, and SHALL NOT report as eligible a candidate it could not assess.

#### Scenario: Git directory without HEAD

- **GIVEN** a `.git` directory with no `HEAD`
- **WHEN** discovery runs
- **THEN** the candidate is malformed with reason `missing_head`
- **AND** other repositories are still found

#### Scenario: Malformed Git file

- **GIVEN** a `.git` file whose first line does not start with `gitdir:`
- **WHEN** discovery runs
- **THEN** the candidate is malformed with reason `invalid_git_file`

#### Scenario: Unreadable Git file

- **GIVEN** a `.git` file that cannot be read
- **WHEN** discovery runs
- **THEN** the candidate is inaccessible with reason `unreadable_git_file`

#### Scenario: Unreadable directory

- **GIVEN** a directory that cannot be listed
- **WHEN** discovery runs
- **THEN** it is reported inaccessible with reason `unreadable_directory`
- **AND** the rest of the root is still searched

### Requirement: Traversal boundaries

The system SHALL descend at most the configured depth below the root (default 6), SHALL NOT enter directories whose names match the exclusions (compared case-insensitively), SHALL count them as excluded, and SHALL NOT follow directory symlinks or junctions.

#### Scenario: Depth limit

- **GIVEN** a repository deeper than the depth limit
- **WHEN** discovery runs
- **THEN** it is not found
- **AND** the directory that was not entered is reported skipped by policy with reason `max_depth`

#### Scenario: Repository at the depth limit

- **GIVEN** a repository exactly at the depth limit
- **WHEN** discovery runs
- **THEN** it is found

#### Scenario: Excluded directory

- **GIVEN** a repository inside `node_modules`
- **WHEN** discovery runs
- **THEN** it is not found
- **AND** the excluded count includes the directory
- **AND** the directory is not listed

#### Scenario: Git directory is not counted as excluded

- **GIVEN** a repository
- **WHEN** discovery runs
- **THEN** its `.git` directory does not increase the excluded count

#### Scenario: Directory link not followed

- **GIVEN** a directory symlink or junction pointing at a repository outside the root
- **WHEN** discovery runs
- **THEN** that repository is not found
- **AND** the link is reported skipped by policy with reason `symlink`

#### Scenario: Linked Git entry

- **GIVEN** a `.git` entry that is a symbolic link
- **WHEN** discovery runs
- **THEN** the candidate is skipped by policy with reason `git_link`

### Requirement: Run status

The system SHALL set the run status to failed when the root is missing, not a directory, or unreadable; to partial when any candidate is inaccessible, malformed, or skipped by policy; and otherwise to complete.

#### Scenario: Complete run

- **GIVEN** a root with repositories and ordinary directories only
- **WHEN** discovery runs
- **THEN** the status is complete

#### Scenario: Partial run

- **GIVEN** a root with one malformed candidate and one repository
- **WHEN** discovery runs
- **THEN** the status is partial
- **AND** the repository is still reported

#### Scenario: Failed run

- **GIVEN** a root that does not exist
- **WHEN** discovery runs
- **THEN** the status is failed
- **AND** one issue has reason `root_not_found`

#### Scenario: Root is not a directory

- **GIVEN** a root that is a file
- **WHEN** discovery runs
- **THEN** the status is failed with reason `root_not_a_directory`

#### Scenario: Unreadable root

- **GIVEN** a root that cannot be listed
- **WHEN** discovery runs
- **THEN** the status is failed with reason `root_unreadable`

### Requirement: Run record

The system SHALL return a record with a run identifier, the root, start and end times, the status, the tool version, the options used, a count for each outcome, the eligible repositories in sorted order, and at most a fixed number of issues together with how many were omitted.

#### Scenario: Record contents

- **GIVEN** any completed discovery
- **WHEN** the record is read
- **THEN** it carries the identifier, root, both times, status, tool version, options, and all five counts

#### Scenario: Issues are bounded but counted

- **GIVEN** more malformed candidates than the issue limit
- **WHEN** discovery runs
- **THEN** only the limit are listed, the omitted number is reported, and the malformed count covers all of them

#### Scenario: Repeatable result

- **GIVEN** an unchanged tree
- **WHEN** discovery runs twice
- **THEN** both runs report the same repositories, issues, and counts

#### Scenario: Independent of listing order

- **GIVEN** the same tree listed in a different directory order
- **WHEN** discovery runs
- **THEN** the repositories, issues, and counts are equal

### Requirement: Nothing is executed or read beyond pointers

The system SHALL NOT run any program and SHALL NOT open any file other than a `.git` pointer file of at most one kilobyte.

#### Scenario: Only pointer files are opened

- **GIVEN** a tree with repositories, a submodule, and other files
- **WHEN** discovery runs
- **THEN** the only files opened are `.git` pointer files

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
