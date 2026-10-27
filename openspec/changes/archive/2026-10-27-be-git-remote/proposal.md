# Change Proposal: be-git-remote

## Why

Discovery says a project has Git but not where it is hosted. People and agents want to know which projects live on GitHub, Bitbucket, GitLab, or somewhere else, and the raw remote URL cannot be stored because it may carry credentials. This change reads each project's remote from its Git config as text and records a credential-free identity with a provider label.

## What Changes

- **git-remote**: parse `.git/config` without running Git, choose the origin remote, reduce its URL to a host and `host/org/repo` identity, label the provider (`github`, `bitbucket`, `gitlab`, `other`, `local`, `none`), and attach the result to each discovered project.

## 1. Problem and Motivation

### Current Situation
Discovery returns projects with their manifests and Git location but no remote information. The remote identity normalization is decided in knowledge but not implemented.

### Problem
Without the remote there is no way to group projects by platform, to recognize the same repository on two machines, or to prepare remote discovery.

### Evidence
- FR-004 lists "Git origin and repository URL" as supported metadata.
- Owner decision 2026-10-27: build it and keep unknown hosts as `other`.
- A predecessor tool stored raw Bitbucket URLs containing a user name (reviewed 2026-10-27).

## 2. Desired Outcome

### Goals
- [ ] Each Git project reports its remote provider and identity, or says why it cannot.
- [ ] No credential is ever kept.
- [ ] Unknown hosts are visible as `other` with the host.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in `specs/git-remote/spec.md` has a passing test.
- [ ] A table of URL forms, including ones with credentials, normalizes as the knowledge decision says.

## 3. Scope

### In Scope
- Parsing remote sections of `.git/config`; URL normalization; provider labels; remote selection and status.
- Reading `.git/config` of a `.git` directory, including a child folder's Git (Unreal `Source`).
- Attaching the result to discovered projects.

### Out of Scope
- Worktree and submodule pointers (remote reported unavailable).
- Any network call, provider API, or check that the remote exists.
- Storing results (local index) and exposing them (MCP).
- Fork and upstream relationships.

### Constraints
Standard library only. No branching on the operating system. `.git/config` is untrusted repository content.

## 4. Stakeholders and Impact

- **Primary stakeholders:** the identity, index, and query changes that will use the remote.
- **Affected components or capabilities:** new `vyasa.domain.git_remote`, a config reader adapter, `Candidate` gains two fields, the repository walk calls the reader.
- **Dependencies:** `be-discover-one-root`.
- **Compatibility considerations:** new fields default to `None`.

## 5. Proposed Direction

A pure domain module for parsing, normalizing, choosing, and labelling; a bounded reader adapter; the walk reads the config of each project's Git directory. Durable choices are in `knowledge/decisions/git-remote-provider-labels.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Parse remotes | Names and URLs from `.git/config` | Must |
| REQ-002 | Normalize | Credential-free host and identity | Must |
| REQ-003 | Provider labels | github, bitbucket, gitlab, other, local, none | Must |
| REQ-004 | Choose a remote | origin, only, ambiguous, none | Must |
| REQ-005 | Read safely | Text only, bounded, no links, no Git | Must |
| REQ-006 | Attach to projects | Including a child folder's Git | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Unusual URL forms | Wrong identity | Unrecognized forms degrade to `other` or `local`; a parametrized table pins every accepted form |
| A new popular host | Labelled `other` | One entry in a table of data |
| Credentials in a non-URL place | Leak | Only host, identity, and label are kept, built from parsed parts |

### Assumptions
- `.git/config` follows Git's section syntax.

### Open Questions
- [ ] Following worktree and submodule pointers to the shared config; unavailable for now (grill Q18).

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python scripts/verify_workflows.py` shows no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-git-remote`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-git-remote`
- **Requirement package:** `docs/requirements/metadata-and-evidence/requirement.md` (FR-004)
- **Knowledge references:** `knowledge/decisions/git-remote-provider-labels.md` — provider labels and reading; `knowledge/decisions/remote-identity-normalization.md` — the identity; `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — Git detector (§9.2)
- **Related issues or references:** None
- **Related existing specifications:** None
- **Related ADRs:** `knowledge/decisions/git-remote-provider-labels.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [ ] Significant ambiguities have been challenged and resolved (grill-me not yet run on this change).
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Draft
