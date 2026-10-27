# Specifications: be-git-remote

## 1. Specification Overview

- **OpenSpec Change ID:** `be-git-remote`
- **Purpose:** Report where each project's Git remote points, without keeping credentials.
- **Related proposal:** `proposal.md`
- **Related design:** `design.md`
- **Api and data contract:** `api-contract.md`
- **Knowledge references:** `knowledge/decisions/git-remote-provider-labels.md`, `knowledge/decisions/remote-identity-normalization.md`
- **Team focus:** Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

## 2. Capability: git-remote

### Purpose

Turn a project's `.git/config` into a provider label and a credential-free identity.

### Scope

Parsing, normalizing, labelling, choosing, safe reading, and attaching to discovered projects.

## ADDED Requirements

### Requirement: Remotes are read from the config text

The system SHALL read each `[remote "<name>"]` section of a Git config as text and take its first `url` value, ignoring comments, other sections, and other keys, and SHALL NOT run Git.

#### Scenario: Several remotes

- **GIVEN** a config with remotes `origin` and `upstream`, each with a `url` and `fetch` lines
- **WHEN** it is parsed
- **THEN** both names are returned with their URLs in file order

#### Scenario: Other sections and comments

- **GIVEN** a config with `[core]`, `[branch "main"]`, comment lines, and a remote
- **WHEN** it is parsed
- **THEN** only the remote is returned

#### Scenario: Quoted value

- **GIVEN** `url = "https://github.com/org/repo.git"`
- **WHEN** it is parsed
- **THEN** the URL has no quotes

### Requirement: URLs are reduced to a credential-free identity

The system SHALL drop the scheme, user information, default port, query, fragment, trailing slash, and trailing `.git` from a remote URL, SHALL rewrite scp-style `user@host:org/repo` to `host/org/repo`, SHALL lower-case the host, SHALL lower-case the whole identity for GitHub and Bitbucket and keep path case elsewhere, and SHALL keep only the host, the identity, and the provider.

#### Scenario: Equivalent forms

- **GIVEN** `https://github.com/Org/Repo.git`, `git@github.com:Org/Repo.git`, `ssh://git@github.com:22/Org/Repo`, and `https://user:token@github.com/Org/Repo/`
- **WHEN** they are normalized
- **THEN** all give host `github.com` and identity `github.com/org/repo`

#### Scenario: Credentials are dropped

- **GIVEN** `https://alice:s3cret@bitbucket.org/team/repo.git`
- **WHEN** it is normalized
- **THEN** neither `alice` nor `s3cret` appears in any returned value

#### Scenario: Non-default port is kept

- **GIVEN** `https://git.example.com:8443/Team/Repo.git`
- **WHEN** it is normalized
- **THEN** the identity is `git.example.com:8443/Team/Repo`

#### Scenario: Case is kept on other hosts

- **GIVEN** `https://git.example.com/Team/Repo.git` and `https://GitHub.com/Team/Repo`
- **WHEN** they are normalized
- **THEN** the first keeps `Team/Repo` and the second gives `github.com/team/repo`

### Requirement: The provider comes from the host

The system SHALL label the provider `github` for `github.com` and `ssh.github.com`, `bitbucket` for `bitbucket.org`, `gitlab` for `gitlab.com`, `other` with the host kept for any other host, `local` with no identity for a path or `file:` URL, and `none` when there is no usable remote.

#### Scenario: Known providers

- **GIVEN** remotes on `github.com`, `bitbucket.org`, and `gitlab.com`
- **WHEN** they are labelled
- **THEN** the providers are `github`, `bitbucket`, and `gitlab`

#### Scenario: GitHub over the ssh port

- **GIVEN** `ssh://git@ssh.github.com:443/Org/Repo.git`
- **WHEN** it is normalized
- **THEN** the host is `github.com` and the identity is `github.com/org/repo`

#### Scenario: Unknown host

- **GIVEN** a remote on `git.example.com`
- **WHEN** it is labelled
- **THEN** the provider is `other` and the host is `git.example.com`

#### Scenario: Local forms

- **GIVEN** remotes `/srv/repos/x.git`, `../x`, `C:\repos\x`, `C:/repos/x`, and `file:///srv/x.git`
- **WHEN** they are labelled
- **THEN** each is `local` with no identity

### Requirement: One remote is chosen

The system SHALL choose the remote named `origin`; otherwise the only remote; otherwise none, with status `ambiguous`; and SHALL report status `none` when there is no remote or its URL is empty.

#### Scenario: Origin preferred

- **GIVEN** remotes `upstream` and `origin`
- **WHEN** one is chosen
- **THEN** `origin` is chosen with status `origin`

#### Scenario: Only remote

- **GIVEN** a single remote named `backup`
- **WHEN** one is chosen
- **THEN** `backup` is chosen with status `only`

#### Scenario: Ambiguous

- **GIVEN** two remotes and none named `origin`
- **WHEN** one is chosen
- **THEN** no remote is chosen and the status is `ambiguous`

#### Scenario: No remote

- **GIVEN** a config with no remote section
- **WHEN** one is chosen
- **THEN** no remote is chosen and the status is `none`

### Requirement: The config is read safely

The system SHALL read at most 64 KiB of `<project>/.git/config`, only when `.git` is a directory and neither it nor the config is a link, and SHALL report status `unavailable` for a `.git` pointer file, a link, an unreadable file, or a file over the limit.

#### Scenario: Config is read

- **GIVEN** a project whose `.git/config` names an origin on GitHub
- **WHEN** discovery runs
- **THEN** the project reports provider `github`

#### Scenario: Pointer file

- **GIVEN** a linked worktree or submodule whose `.git` is a file
- **WHEN** discovery runs
- **THEN** the remote status is `unavailable`

#### Scenario: Oversized config

- **GIVEN** a config larger than 64 KiB
- **WHEN** discovery runs
- **THEN** the remote status is `unavailable`

#### Scenario: Linked config

- **GIVEN** `.git/config` is a symbolic link
- **WHEN** discovery runs
- **THEN** the remote status is `unavailable`

### Requirement: Discovery attaches the remote

The system SHALL attach the chosen remote and its status to each discovered project that has Git, reading the config of the project's own Git directory or, for a manifest project, of the child folder that holds its Git, and SHALL leave both unset for a project without Git.

#### Scenario: Repository

- **GIVEN** a Git repository with an origin on Bitbucket
- **WHEN** discovery runs
- **THEN** the candidate carries provider `bitbucket`, the identity, and status `origin`

#### Scenario: Git in a child folder

- **GIVEN** an Unreal project with its Git in `Source`
- **WHEN** discovery runs
- **THEN** the remote is read from `Source/.git/config`

#### Scenario: Project without Git

- **GIVEN** a manifest project with no Git
- **WHEN** discovery runs
- **THEN** the remote and its status are unset

#### Scenario: Only listed files are opened

- **GIVEN** projects with Git
- **WHEN** discovery runs
- **THEN** the only files opened are `.git` pointer files, `.git/config` files, and ignore files when nested repositories are enabled

---

## 5. Specification Review

- [x] Every in-scope behavior is described by a requirement.
- [x] Every requirement sits inside a delta section heading.
- [x] Scenarios cover normal, boundary, and failure behavior.
- [x] Assumptions and unresolved questions are identified in the proposal.

**Status:** Draft
