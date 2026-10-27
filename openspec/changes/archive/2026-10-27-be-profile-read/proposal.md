# Change Proposal: be-profile-read

## Why

A scanner cannot know a project's purpose, lifecycle, domain, or relations. A coding agent working inside a repository can write them down once, in a small profile file. Vyasa needs to read that file safely during a scan, validate it per field, store the declared values, and show them in the project details agents get over MCP.

## What Changes

- **project-profile**: a new capability. Discovery reads `.vyasa/project-profile.toml` from each eligible project (bounded, text only, never through a link); fields are validated individually; the result is stored per checkout; `get_project` returns the declared values with their source, and a status when there is no profile or it is invalid.

## 1. Problem and Motivation

### Current Situation

Project details hold only discovered facts: name, state, identity, checkouts, and remote. No declared facts exist.

### Problem

Agents asking "what is this project for, and is it still alive?" get nothing (FR-010, FR-014). The facts exist only in people's heads or prose.

### Evidence

- Verified: `Candidate` already carries per-project reads (`remote`); discovery is read-only and bounded.
- Verified: Python's standard library parses TOML (`tomllib`), already used for `config.toml`.
- Verified: the owner decided on 2026-10-27 that the profile is filled once by a coding agent in each repository, that its format is TOML (changing the earlier YAML decision), and that MCP project details come from it. Vyasa never writes it.

## 2. Desired Outcome

### Goals

- [ ] Read the profile during a scan, safely.
- [ ] Validate each field; keep valid fields when others are invalid.
- [ ] Store declared values with source and show them in `get_project`.
- [ ] Treat "no profile" as an ordinary state.

### Team Focus

Untrusted repository content, per-field validation, bounded reads, provenance of declared facts, and no repository writes.

### Success Criteria

- [ ] A valid profile appears in `get_project` as `declared` values with source.
- [ ] A profile with one bad field keeps the good fields and lists the problem.
- [ ] An unsupported `schema_version` marks the whole profile unsupported.
- [ ] A symlinked, oversized, or malformed file never stops the scan.
- [ ] A scan leaves the repository byte-identical.

## 3. Scope

### In Scope

- Profile schema v1 (fields below), validation, limits, the reader, storage, `get_project` output.
- Migration `0005` (`checkout_profiles`).

### Out of Scope

- The agent guide tool and JSON Schema (`be-profile-guide`).
- Searching or filtering by profile fields; obsolete candidates from declared lifecycle.
- Draft generation or any write into a repository.
- Resolving `related_projects` to indexed projects; precedence between declared and detected technologies (no detected technologies exist yet).
- Monorepo component profiles.

### Constraints

Standard library only; the file is untrusted text; values are capped and stripped of control characters; no path or URL with credentials accepted.

## 4. Stakeholders and Impact

- **Primary stakeholders:** coding agents and the owner.
- **Affected components or capabilities:** `vyasa.domain` (profile rules), `vyasa.adapters.filesystem` (reader), discovery candidates, `vyasa.adapters.sqlite`, `vyasa.application.query`.
- **Dependencies:** all merged index, query, scan, and MCP changes.
- **Compatibility considerations:** additive; `Candidate` gains an optional field; `get_project` gains a `profile` key.

## 5. Proposed Direction

Schema v1 fields: `schema_version` (1), `name`, `purpose`, `lifecycle` (`active`, `maintenance`, `experimental`, `deprecated`, `archived`), `domain`, `tags`, `technologies`, `owners` (string lists), `related_projects` (tables with `identity` and `relation`), and `documentation.entry_point` (a relative path). A pure `validate_profile(data)` returns a status, the valid fields, and problems. The reader attaches the result to the candidate; the store keeps one row per checkout. Considered: YAML (new dependency) and reading the README (guessing, not declaring).

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | The profile is read safely | bounded, text, no links | Must |
| REQ-002 | Fields validate individually | good fields survive | Must |
| REQ-003 | Declared values are stored with source | provenance kept | Must |
| REQ-004 | Project details show the profile | status and values | Must |
| REQ-005 | Absence is ordinary | no error, no flag | Must |

## 7. Risks and Open Questions

### Risks

| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Hostile profile text reaches agents | Prompt injection | Caps, control characters stripped, returned as typed data under a `declared` label; server instructions call it data |
| Profile contradicts reality | Wrong purpose shown | It is labelled declared and carries its source |
| Two checkouts differ | Ambiguous project profile | Deterministic choice: active first, then earliest seen |

### Assumptions

- One profile per repository root.

### Open Questions

- [ ] Whether `related_projects` identities should later resolve to project ids.

## 8. Acceptance Summary

- [ ] Every spec scenario has a test.
- [ ] `pytest`, `verify_workflows.py`, `verify_knowledge.py`, `openspec validate` pass.

## 9. Traceability

- **OpenSpec Change ID:** `be-profile-read`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-profile-read`
- **Requirement package:** `docs/requirements/project-profile/requirement.md`
- **Knowledge references:**
  - `knowledge/decisions/canonical-profile-and-draft.md` — the profile as the declared source (updated: TOML)
  - `knowledge/concepts/field-ownership.md` — declared values belong to the repository
  - `knowledge/concepts/untrusted-content.md` — profile text is data
  - `knowledge/concepts/evidence-and-provenance.md` — `declared` status and source
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/repository-discovery`, `openspec/specs/project-query`, `openspec/specs/mcp-server`
- **Related ADRs:** `knowledge/decisions/canonical-profile-and-draft.md`

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
