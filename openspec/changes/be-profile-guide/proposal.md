# Change Proposal: be-profile-guide

## Why

A project's profile is meant to be written once by a coding agent working in the repository, but the agent has no way to know the file's name, fields, limits, or rules. Vyasa needs a read-only MCP tool that returns exactly that, plus a committed JSON Schema, so any agent can write a valid profile without Vyasa ever writing into a repository.

## What Changes

- **project-profile**: a generated guide (path, fields, limits, allowed values, an example, and writing rules) and a committed JSON Schema kept equal to the validation rules.
- **mcp-server**: a fourth tool, `get_profile_guide`, serving the guide without needing an index.

## 1. Problem and Motivation

### Current Situation

`be-profile-read` reads and validates `.vyasa/project-profile.toml`. The schema lives only in code and the README.

### Problem

An agent asked to "fill in the Vyasa profile" has no machine-readable instructions. Guessing produces invalid fields; asking the human defeats the point.

### Evidence

- Verified: the schema constants are in `vyasa.domain.profile`; the MCP server serves static-safe, read-only tools.
- Verified: the owner decided on 2026-10-27 that an MCP tool plus a schema file guides agents (no template-writing command).

## 2. Desired Outcome

### Goals

- [ ] One tool returns everything an agent needs to write a valid profile.
- [ ] The guide, the schema file, and the validator cannot drift apart.
- [ ] The tool works before any scan, with no index.

### Team Focus

MCP tool contract, no drift between documented and enforced rules, untrusted-content stance in the guide.

### Success Criteria

- [ ] The guide's example is a valid profile.
- [ ] The committed JSON Schema equals the generated one.
- [ ] `get_profile_guide` answers with no index present.
- [ ] The tool snapshot lists four tools and no new input path.

## 3. Scope

### In Scope

- `profile_guide()` and `json_schema()` in `vyasa.domain.profile`; `schemas/project-profile.v1.json`.
- `get_profile_guide` tool and the snapshot update.

### Out of Scope

- A command that writes a template or the profile (Vyasa never writes repositories).
- Validating a candidate profile through MCP (a later `check_profile` could take text, not a path).
- Prompts or resources.

### Constraints

Read-only; no input; no filesystem access; stdout protocol only.

## 4. Stakeholders and Impact

- **Primary stakeholders:** coding agents; maintainers writing profiles by hand.
- **Affected components or capabilities:** `vyasa.domain.profile`, `vyasa.adapters.mcp.server`, `schemas/`, the tool snapshot.
- **Dependencies:** `be-profile-read`, `be-mcp-server` (merged).
- **Compatibility considerations:** one added tool; existing tools unchanged.

## 5. Proposed Direction

Build the guide from the same constants the validator uses, so a change to a limit changes the guide. Commit the JSON Schema and test it equal to `json_schema()`. The tool returns the guide in the shared envelope (with `meta.generated_at` only, since no index is read). Considered: a hand-written guide (drifts) and a template-writing command (writes into repositories).

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | The guide is generated from the rules | no drift | Must |
| REQ-002 | A JSON Schema is committed | editor validation | Must |
| REQ-003 | The tool needs no index | works first | Must |
| REQ-004 | The tool list is four read-only tools | pinned | Must |

## 7. Risks and Open Questions

### Risks

| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| An agent invents facts to fill every field | Wrong declarations | Guide says to omit unknown fields and describe only what is verifiable |
| An agent writes secrets into the profile | Leak into the index | Guide forbids credentials; length caps limit damage |

### Assumptions

- Agents can write a file in the repository they are working in.

### Open Questions

- [ ] A `check_profile` tool that validates text before writing.

## 8. Acceptance Summary

- [ ] Every spec scenario has a test.
- [ ] `pytest`, `verify_workflows.py`, `verify_knowledge.py`, `openspec validate` pass.

## 9. Traceability

- **OpenSpec Change ID:** `be-profile-guide`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-profile-guide`
- **Requirement package:** `docs/requirements/project-profile/requirement.md`
- **Knowledge references:**
  - `knowledge/decisions/canonical-profile-and-draft.md` — agent or maintainer writes it; Vyasa reads
  - `knowledge/concepts/untrusted-content.md` — profile text is data
  - `knowledge/decisions/explicit-tools-disabled-by-default.md` — the tool is read-only
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/project-profile`, `openspec/specs/mcp-server`
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
