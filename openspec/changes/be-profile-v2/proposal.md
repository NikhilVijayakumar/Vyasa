# Change Proposal: be-profile-v2

## Why

The first profile schema holds nine short fields, so a coding agent cannot declare a project's purpose, scope, capabilities, architecture, interfaces, documentation map, or relationships in a predefined, validated form. FR-026 adds a second schema that declares all of this as optional nested TOML tables, read field by field, while version 1 profiles keep working and Vyasa's identity rules stay untouched.

## What Changes

- **project-profile**: schema version 2 validation (about ninety optional fields in nested tables), declared ids stored as labels only, text and path safety rules, a version-2 writer guide, and a committed version-2 JSON Schema; version 1 reading is unchanged.

## 1. Problem and Motivation

### Current Situation
`src/vyasa/domain/profile.py` validates schema version 1: `name`, `purpose`, `lifecycle`, `domain`, `tags`, `technologies`, `owners`, `related_projects`, `documentation.entry_point`. `read_profile` parses TOML up to 64 KiB, `get_profile_guide` returns the generated guide, and `schemas/project-profile.v1.json` is committed. Stored profile fields are a flat dictionary in `checkout_profiles.fields`. The requirement package `docs/requirements/project-profile/` records the second grill (Q14–Q22); the owner decided Q14–Q20 on 2026-10-28.

### Problem
There is nowhere to declare, in a validated shape, what a project is for, what it does, how it is built, and where its documents are. Agents asked to write a comprehensive profile have no schema to write against.

### Evidence
- `validate_profile` rejects any version other than 1 (`src/vyasa/domain/profile.py`, verified 2026-10-28).
- `docs/requirements/project-profile/grill-log.md` Q14–Q22 and the pasted Project Profile Standard proposal.

## 2. Desired Outcome

### Goals
- [ ] A version 2 profile is validated field by field and stored under dotted names.
- [ ] Version 1 profiles read exactly as before.
- [ ] The guide and JSON Schema describe version 2 from the same definitions as the validation.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in the spec has a passing test, including hostile profile text.
- [ ] The committed version-2 schema file equals the generated one.
- [ ] The MCP tool snapshot changes only in the guide tool's description.

## 3. Scope

### In Scope
- A table-driven version 2 field definition used by the validator, the guide, and the JSON Schema.
- Safety rules for text, contacts, paths, dates, ids, and commits.
- `schemas/project-profile.v2.json` and the version-2 guide with a complete example.
- A single accessor that reads a declared value from either version.

### Out of Scope
- The context bundle, the differences list, the MCP context tool, and the CLI command (`be-profile-context`).
- A draft generator; profile editing commands; monorepo component profiles.
- Using any declared id for identity, matching, or merging.
- Copying observed technology, activity, delivery status, or portfolio priority into the profile.

### Constraints
Standard library only (`tomllib`). Profile text is untrusted repository content (NFR-020). The profile size limit stays 64 KiB.

## 4. Stakeholders and Impact

- **Primary stakeholders:** coding agents that write profiles and tools that read them through Vyasa.
- **Affected components or capabilities:** `domain/profile.py`, `adapters/filesystem/profile_file.py` (no change expected), `adapters/mcp/server.py` (guide description), `schemas/`, tests.
- **Dependencies:** none.
- **Compatibility considerations:** version 1 files and stored version 1 fields are unchanged; stored fields of version 2 use dotted names; the guide's returned `schema_version` becomes 2 and it lists both versions.

## 5. Proposed Direction

Describe version 2 once as data (a path-to-kind table), and drive the validator, the guide, and the JSON Schema from it. Reject unsafe values at validation. Keep the reader unchanged. Alternatives (YAML, replacing version 1, growing version 1, declared ids driving identity) are rejected in `knowledge/decisions/profile-schema-v2-full-template.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Version 2 read field by field | Valid fields kept, invalid dropped and reported | Must |
| REQ-002 | Version 1 unchanged | Existing profiles read as before | Must |
| REQ-003 | Unknown field and version | Reported; unrelated extraction continues | Must |
| REQ-004 | Declared ids are labels | Never influence identity | Must |
| REQ-005 | Text, contact, and path safety | Credentials, emails, and unsafe paths rejected | Must |
| REQ-006 | Bounded lists and tables | Counts and lengths limited | Must |
| REQ-007 | Enumerations, dates, commits | Fixed values and formats | Must |
| REQ-008 | Guide and JSON Schema | Generated from the validation definitions | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| ~90 fields drift between validator, guide, and schema | Wrong guidance to agents | One definition table drives all three; a test compares the committed schema |
| Owners copy observed or portfolio data into the profile | Stale duplicates | The guide's rules state what not to declare; the schema has no such fields |
| Declared text carries instructions aimed at agents | Prompt injection through the profile | Values are length-capped, stripped of control characters, and returned as typed data |
| A large profile slows scans | Cost | The 64 KiB limit stays |

### Assumptions
- A TOML date value (local date) is accepted and stored as an ISO date string.
- `schema_version` is the only top-level key besides `project` in version 2.

### Open Questions
- [ ] Owner confirmation of Q21 and Q22.

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python -m pytest` and `python scripts/verify_workflows.py` show no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-profile-v2`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-profile-v2`
- **Requirement package:** `docs/requirements/project-profile/requirement.md`
- **Knowledge references:** `knowledge/decisions/profile-schema-v2-full-template.md` — schema; `knowledge/decisions/canonical-profile-and-draft.md` — path and format; `knowledge/decisions/stored-identity-with-aliases.md` — identity stays remote-derived; `knowledge/concepts/field-ownership.md` — declared versus observed
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/project-profile`, `openspec/specs/mcp-server`
- **Related ADRs:** `knowledge/decisions/profile-schema-v2-full-template.md`

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
