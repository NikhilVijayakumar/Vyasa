# Change Proposal: be-profile-context

## Why

A coding agent asked to write a project's profile has to rediscover what Vyasa already observed: languages, file counts, markers, frameworks, and repository identity. It also cannot see where the declared profile disagrees with those observations. FR-027 gives the agent one read-only bundle of the deterministic facts, the profile as read, and the differences, through an MCP tool and a command-line command, without Vyasa launching an agent or writing the profile.

## What Changes

- **profile-context**: a deterministic differences list comparing the declared profile with stored observations; a context bundle built from project details; an MCP tool `get_profile_context`; a CLI command `vyasa profile-context` that runs a live read-only scan of one checkout into a temporary in-memory index; a writer workflow in every bundle.

## 1. Problem and Motivation

### Current Situation
`get_project` returns identity, checkouts with observed languages, composition, markers, and frameworks, and the profile as read. `get_profile_guide` explains how to write a profile. Nothing compares declared with observed, nothing tells an agent how to use the facts, and the only way to get facts for an unindexed repository is to configure roots and scan. The requirement package `docs/requirements/project-profile/` records Q18–Q22; the owner decided Q18–Q20 on 2026-10-28.

### Problem
Agents writing profiles lack the evidence and the comparison; an unindexed repository cannot be described without changing configuration and the index.

### Evidence
- `src/vyasa/application/query.py` `get_project` has no differences or workflow (verified 2026-10-28).
- `src/vyasa/adapters/cli/main.py` has only `scan`, which needs configured roots and writes the real index.
- `discover_repositories(path)` finds the repository at `path` when `path` is itself the root (checked 2026-10-28).

## 2. Desired Outcome

### Goals
- [ ] One tool call returns the evidence, the profile, the differences, and the workflow for a stored project.
- [ ] One command returns the same bundle for any repository from a live read-only scan, writing nothing.
- [ ] Differences claim absence only where the observation is complete.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in the spec has a passing test.
- [ ] The command leaves the repository and the real index byte-identical.
- [ ] The MCP tool snapshot test passes with the new tool.

## 3. Scope

### In Scope
- `differences(...)` as a pure function; `get_profile_context` in the query layer; the MCP tool.
- `open_memory_index`, a public enrichment function for a discovery run, and the `profile-context` command.
- The writer workflow text.

### Out of Scope
- Launching or configuring an agent; writing or correcting a profile; drafts.
- Comparisons that need file access at query time (declared paths against the file system).
- Portfolio comparison across projects.

### Constraints
Standard library only. No absolute path and no file text in the bundle. The command writes nothing to disk.

## 4. Stakeholders and Impact

- **Primary stakeholders:** coding agents writing profiles and the maintainers who review them.
- **Affected components or capabilities:** `application/query.py`, new `application/profile_context.py`, `application/indexing/scan.py`, `adapters/sqlite/database.py`, `adapters/cli/main.py`, `adapters/mcp/server.py`.
- **Dependencies:** `be-profile-v2` (declared fields and the accessor).
- **Compatibility considerations:** additive; one new tool and one new command; existing tools unchanged; `scan` unchanged.

## 5. Proposed Direction

Build the bundle from `get_project` data so the two entry points cannot disagree; compute differences per checkout from the read models; reuse the whole scan pipeline for the live path by writing into an in-memory index that is dropped. Alternatives (launching an agent, an index-only command, a command that updates the real index, automatic correction) are rejected in `knowledge/decisions/profile-context-for-agents.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Context bundle | Facts, profile, differences, workflow in one read | Must |
| REQ-002 | MCP tool | Served from the stored observation, with source and time | Must |
| REQ-003 | CLI command | Live read-only scan, nothing written | Must |
| REQ-004 | Differences | Only where observation supports; findings for review | Must |
| REQ-005 | No paths or text | Bundle has no absolute path or file text | Must |
| REQ-006 | Not launching, not writing | No agent started; profile unchanged | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Differences make absence claims from partial data | Misleading findings | Each rule requires a complete assessment; tested with partial fixtures |
| Live and stored bundles diverge in shape | Confusing agents | Both come from the same function over the same read models |
| The in-memory index misses a migration side effect | Wrong live result | The same migrations are applied; a test compares live and stored bundles for one repository |
| Workflow text steers agents unsafely | Prompt-injection surface | Fixed text only; no repository content is placed in it |

### Assumptions
- A project's profile applies to every checkout of it, so differences are computed per checkout against the one profile shown.
- The CLI path is the repository root; a subdirectory is not a project.

### Open Questions
- [ ] Owner confirmation of Q21 and Q22.

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python -m pytest` and `python scripts/verify_workflows.py` show no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-profile-context`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-profile-context`
- **Requirement package:** `docs/requirements/project-profile/requirement.md`
- **Knowledge references:** `knowledge/decisions/profile-context-for-agents.md` — bundle, sources, differences; `knowledge/decisions/profile-schema-v2-full-template.md` — declared fields; `knowledge/decisions/observation-freshness-without-query-time-io.md` — no query-time file access; `knowledge/decisions/read-only-access-and-git-policy.md` — read-only
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/project-query`, `openspec/specs/mcp-server`, `openspec/specs/scan-command`
- **Related ADRs:** `knowledge/decisions/profile-context-for-agents.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved (`docs/requirements/project-profile/grill-log.md`, Q14–Q22).
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
