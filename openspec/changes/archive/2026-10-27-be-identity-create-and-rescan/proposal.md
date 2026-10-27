# Change Proposal: be-identity-create-and-rescan

## Why

The index matches a project only by its folder path, so a renamed or moved repository becomes a second project, and a repository's remote is not what identifies it. Projects need a stored identity created once from the strongest evidence, with later evidence recorded as aliases, so rescans stay idempotent and renames harmless.

## What Changes

- **project-identity**: a new capability. Each project gets an identity status and source; remote identities are stored as aliases; rediscovery finds a project by alias, then by checkout path; a project may hold several checkouts; every identity change is an event.

## 1. Problem and Motivation

### Current Situation

`be-local-index` stores projects and checkouts and matches by `path_key` only. `be-git-remote` already produces a normalized, credential-free `host/org/repo` identity per candidate.

### Problem

Moving or renaming a repository creates a new project and marks the old one missing. Two clones of one remote are unrelated rows. There is no record of how settled an identity is (NFR-004, FR-003 S1 to S3).

### Evidence

- Verified: `checkouts.path_key` is the only match key; `Candidate.remote.identity` exists and normalization is done; no alias or event table exists.
- Verified: owner confirmed identity Q2, Q4, Q5 and Q14 on 2026-10-27.
- Assumption: a remote identity is a sound alias for "same project" until the ambiguity change adds review.

## 2. Desired Outcome

### Goals

- [ ] A repository with a usable remote gets a `resolved` identity whose alias is its remote identity.
- [ ] A repository without one gets a `provisional` identity matched by path.
- [ ] A rename or move keeps the project and records the new location.
- [ ] Every identity change leaves an event.

### Team Focus

Judged on the data model and invariants, failure modes (conflicting evidence), migration impact on existing indexes, and persistence-layer tests.

### Success Criteria

- [ ] Moving a repository with a remote keeps its `project_id` and adds a checkout; the old one becomes missing.
- [ ] Rescanning never creates a second project for the same remote.
- [ ] Migrating an existing index gives remote-bearing projects an alias and `resolved` status without losing data.
- [ ] Conflicting evidence changes nothing except an event.

## 3. Scope

### In Scope

- Migration `0002` (identity columns, `project_aliases`, `identity_events`) with backfill.
- Create and rescan matching: alias, then checkout path.
- Several checkouts per project; project state derived from its checkouts.
- Remote appearing, changing, or disappearing for a known checkout.

### Out of Scope

- Root-commit identity for repositories without a remote. The decision calls for one sanitized Git call; that is a separate security-sensitive change (`be-root-commit-identity`). Until then such a repository is `provisional` and a move creates a new project.
- Duplicate checkouts flagged for review, ambiguity status, review candidates, provider ids, forks (`be-identity-ambiguity`, `be-review-candidates`).
- MCP and CLI surface.

### Constraints

Standard library; no Git execution; the original remote URL is never stored; identifiers never recomputed.

## 4. Stakeholders and Impact

- **Primary stakeholders:** the owner; later query and sync work that keys on identity.
- **Affected components or capabilities:** `vyasa.adapters.sqlite` (migration, `projects`), `vyasa.application.indexing`, `vyasa.domain.index`.
- **Dependencies:** `be-local-index`, `be-git-remote` (merged).
- **Compatibility considerations:** additive migration of schema 1 to 2 with backup; `store_run` signature unchanged.

## 5. Proposed Direction

Keep `project_id` opaque and stored. Look up the candidate's remote identity in `project_aliases`, then its path in `checkouts`. Alias hit with no path hit attaches a new checkout to that project. Path hit with a new remote adds an alias and moves a provisional project to resolved. If alias and path point to different projects, change nothing and record a conflict event. Considered: deriving the ID from the remote (breaks on rename) and moving the old checkout's path in place (loses the history of the old location).

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Create identity from the strongest evidence | resolved or provisional | Must |
| REQ-002 | Rediscover by alias then path | no duplicates, renames survive | Must |
| REQ-003 | Record identity events | audit trail | Must |
| REQ-004 | Conflicts are preserved | nothing merged or moved | Must |
| REQ-005 | Migrate existing indexes | aliases backfilled | Must |

## 7. Risks and Open Questions

### Risks

| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Two clones share one project before review exists | Reviewer cannot see them as duplicates yet | They are visible as two checkouts of one project; the next change flags them |
| Existing index has two projects with the same remote | Backfill cannot give both the alias | First by checkout id wins; the other stays provisional; conflict handled by the ambiguity change |
| Remote-less moves still duplicate | Known gap | Provisional status says so; root-commit change follows |

### Assumptions

- A normalized remote identity names one project.

### Open Questions

- [ ] Whether root-commit identity should run before or after the ambiguity change.

## 8. Acceptance Summary

- [ ] Every spec scenario has a test against a real database file.
- [ ] Phase 1 criterion 8 holds for remote-bearing repositories.
- [ ] `pytest`, `verify_workflows.py`, `verify_knowledge.py`, `openspec validate` pass.

## 9. Traceability

- **OpenSpec Change ID:** `be-identity-create-and-rescan`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-identity-create-and-rescan`
- **Requirement package:** `docs/requirements/project-identity/requirement.md`
- **Knowledge references:**
  - `knowledge/concepts/project-identity.md` — evidence order, status, rules
  - `knowledge/decisions/stored-identity-with-aliases.md` — created once, aliases, lookup order (updated with conflict handling)
  - `knowledge/decisions/remote-identity-normalization.md` — the identity being stored
  - `knowledge/decisions/index-lifecycle-and-single-writer.md` — states and the lock
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/local-index`, `openspec/specs/git-remote`
- **Related ADRs:** `knowledge/decisions/stored-identity-with-aliases.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved, or explicitly recorded.
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
