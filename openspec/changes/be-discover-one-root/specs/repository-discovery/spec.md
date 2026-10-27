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

The system SHALL treat a directory that contains a `.git` directory with a `HEAD` file, or a `.git` file whose first line starts with `gitdir:`, as a repository candidate, and SHALL classify a `.git` file as a linked worktree when the target ends in `<git directory>/worktrees/<name>`, as a submodule when the target contains `.git/modules`, and otherwise as a repository.

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

#### Scenario: Look-alike paths are repositories

- **GIVEN** a `.git` file pointing at `/home/me/modules/repo.git`, and another at `/home/me/worktrees/repo.git`
- **WHEN** discovery runs
- **THEN** both are reported eligible with kind repository

#### Scenario: Bare-repository worktree and nested submodule

- **GIVEN** a `.git` file pointing at `/srv/bare.git/worktrees/feature`, and another at `../.git/modules/outer/modules/inner`
- **WHEN** discovery runs
- **THEN** the first is a linked worktree and the second a submodule

#### Scenario: Root is a symlink

- **GIVEN** the root path is itself a symlink to a directory containing a repository
- **WHEN** discovery runs
- **THEN** the repository is found and the status is complete

#### Scenario: Ordinary directories are not candidates

- **GIVEN** directories without a `.git` entry
- **WHEN** discovery runs
- **THEN** none of them appears in the repositories or the issues

### Requirement: Recognize projects by manifest

The system SHALL treat a directory without a `.git` entry that contains `pyproject.toml`, `requirements.txt`, `setup.py`, `package.json`, `Cargo.toml`, `go.mod`, or a file ending in `.uproject` (compared without regard to case) as an eligible project of kind project, SHALL record the manifests found, and SHALL look for a valid `.git` in its immediate child directories, recording the child's name or none.

#### Scenario: Manifest without Git

- **GIVEN** a directory with `package.json` and no Git
- **WHEN** discovery runs
- **THEN** it is eligible with kind project, the manifest recorded, and no Git location

#### Scenario: Each manifest is recognized

- **GIVEN** directories holding `pyproject.toml`, `requirements.txt`, `setup.py`, `Cargo.toml`, `go.mod`, `Tantra.uproject`, and `X.UPROJECT`
- **WHEN** discovery runs
- **THEN** each is an eligible project

#### Scenario: Git in a child folder

- **GIVEN** an Unreal project with a `.uproject` at its root and a valid `.git` inside its `Source` folder
- **WHEN** discovery runs
- **THEN** it is one project, with Git location `Source`

#### Scenario: Broken Git in a child folder

- **GIVEN** a manifest project whose child folder has a `.git` directory without `HEAD`
- **WHEN** discovery runs
- **THEN** the project has no Git location

#### Scenario: Source files and a README alone

- **GIVEN** folders holding only `.py` or `.ts` files, or a README without a docs folder
- **WHEN** discovery runs
- **THEN** none is a project

#### Scenario: Git repository records its manifests

- **GIVEN** a Git repository holding `package.json` and `pyproject.toml`
- **WHEN** discovery runs
- **THEN** it is eligible with kind repository, Git location `.`, and both manifests recorded

### Requirement: Recognize projects that have not started

The system SHALL treat a directory that has a README (a file whose name starts with `readme`) and a directory named `docs`, `doc`, or `documentation`, and that has neither a `.git` entry nor a manifest, as an eligible project of kind documentation, SHALL look for Git in its child directories as for a manifest project, and SHALL NOT report it when another project lies below it.

#### Scenario: README and docs

- **GIVEN** a folder with `README.md` and a `docs` folder
- **WHEN** discovery runs
- **THEN** it is eligible with kind documentation

#### Scenario: Documentation folder names

- **GIVEN** folders with a README and a folder named `docs`, `doc`, or `Documentation`
- **WHEN** discovery runs
- **THEN** each is a project of kind documentation

#### Scenario: README without docs

- **GIVEN** a folder with a README and a folder named `notes`
- **WHEN** discovery runs
- **THEN** it is not a project

#### Scenario: Not started project with Git

- **GIVEN** a folder with a README and docs that has a valid `.git`
- **WHEN** discovery runs
- **THEN** it is an ordinary repository, not kind documentation

#### Scenario: Container is not a project

- **GIVEN** a folder with a README and docs that holds a project in a subfolder
- **WHEN** discovery runs
- **THEN** only the inner project is reported

#### Scenario: Git in a child folder

- **GIVEN** a README-and-docs folder whose `Source` child has a valid `.git`
- **WHEN** discovery runs
- **THEN** it is one project of kind documentation with Git location `Source`

### Requirement: A project is a boundary

The system SHALL NOT enter a directory it recognized as a project, other than to look for Git in its immediate children, unless nested repositories are enabled; SHALL search folders that are not projects down to the depth limit; and, when nested repositories are enabled, SHALL report projects inside projects as separate candidates without merging them.

#### Scenario: Projects are not entered

- **GIVEN** a project holding a nested manifest and a nested repository
- **WHEN** discovery runs
- **THEN** only the outer project is reported
- **AND** nothing inside it is skipped or warned about

#### Scenario: Plain folders are searched down to the project

- **GIVEN** a project four folders below a root that are not projects
- **WHEN** discovery runs
- **THEN** it is found

#### Scenario: Nested projects when enabled

- **GIVEN** nested repositories are enabled and a project holds another project
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

The system SHALL descend at most the configured depth below the root (default 8), SHALL NOT enter directories whose names match the exclusions (compared case-insensitively), SHALL count them as excluded, and SHALL NOT follow directory symlinks or junctions. A directory not entered because of the depth limit or because it is a link SHALL be reported in a warning, not as a failure.

#### Scenario: Depth limit

- **GIVEN** a repository deeper than the depth limit
- **WHEN** discovery runs
- **THEN** it is not found
- **AND** a `max_depth` warning counts the directory that was not entered

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
- **AND** a `symlink` warning counts the link

#### Scenario: Linked Git entry

- **GIVEN** a `.git` entry that is a symbolic link
- **WHEN** discovery runs
- **THEN** the candidate is not a repository
- **AND** a `git_link` warning counts it

### Requirement: Run status

The system SHALL set the run status to failed when the root is missing, not a directory, or unreadable; to partial when any candidate is inaccessible or malformed; and otherwise to complete. A directory skipped by policy SHALL NOT change the status.

#### Scenario: Complete run

- **GIVEN** a root with repositories and ordinary directories only
- **WHEN** discovery runs
- **THEN** the status is complete

#### Scenario: Partial run

- **GIVEN** a root with one malformed candidate and one repository
- **WHEN** discovery runs
- **THEN** the status is partial
- **AND** the repository is still reported

#### Scenario: Skips do not make a run partial

- **GIVEN** a root where some directories were skipped by the depth limit and nothing failed
- **WHEN** discovery runs
- **THEN** the status is complete
- **AND** a warning reports the skips

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

The system SHALL return a record with a run identifier, the root, start and end times, the status, the tool version, the options used, a count for each outcome, the eligible repositories in sorted order, at most a fixed number of failures (inaccessible and malformed candidates) together with how many were omitted, and one warning for each reason directories were skipped by policy, giving the number skipped, up to five examples, and advice on what to do.

#### Scenario: Record contents

- **GIVEN** any completed discovery
- **WHEN** the record is read
- **THEN** it carries the identifier, root, both times, status, tool version, options, and all five counts

#### Scenario: Failures are bounded but counted

- **GIVEN** more malformed candidates than the issue limit
- **WHEN** discovery runs
- **THEN** only the limit are listed, the omitted number is reported, and the malformed count covers all of them

#### Scenario: Skips are summarized

- **GIVEN** eight directories skipped by the depth limit
- **WHEN** discovery runs
- **THEN** there is one `max_depth` warning with count 8 and five examples
- **AND** its advice names the repository's `.vyasaignore` and the depth limit

#### Scenario: A failure is never hidden by skips

- **GIVEN** many skipped directories and one malformed candidate
- **WHEN** discovery runs
- **THEN** the malformed candidate is listed as an issue and the status is partial

#### Scenario: Repeatable result

- **GIVEN** an unchanged tree
- **WHEN** discovery runs twice
- **THEN** both runs report the same repositories, issues, warnings, and counts

#### Scenario: Independent of listing order

- **GIVEN** the same tree listed in a different directory order
- **WHEN** discovery runs
- **THEN** the repositories, issues, and counts are equal

### Requirement: Nothing is executed or read beyond pointers

The system SHALL NOT run any program and SHALL NOT open any file other than a `.git` pointer file of at most one kilobyte.

#### Scenario: Only pointer files are opened

- **GIVEN** a tree with repositories, manifest projects, a submodule, and other files
- **WHEN** discovery runs
- **THEN** the only files opened are `.git` pointer files

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
