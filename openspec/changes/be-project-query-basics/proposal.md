# Change Proposal: be-project-query-basics

## Why

The index holds projects, identity, and review state, but nothing reads it for an agent. Vyasa needs a read-only, deterministic, bounded query layer, independent of MCP, to search projects, get one project, and report index status, so the MCP server can wrap it without owning any logic.

## What Changes

- **project-query**: a new capability. `search_projects`, `get_project`, and `get_index_status` as plain functions over a read-only connection, with the shared response envelope, cursor pagination, structured errors, and local paths omitted by default.

## 1. Problem and Motivation

### Current Situation

`vyasa.adapters.sqlite` offers `list_projects`, `list_flags`, `list_candidates`, and `freshness`. They return raw rows, are unordered across pages, and have no limits, envelope, or error codes.

### Problem

An agent cannot ask "which projects do I know about, and how reliable is that?" without raw SQL. The MCP layer must not carry query logic (core must not depend on MCP).

### Evidence

- Verified: the index stores display name, state, identity status and source, aliases, checkouts with remote provider, host, identity and status, runs, flags, and decisions.
- Verified: no languages, technologies, purpose, dependencies, or documentation fields exist yet; those need detectors.
- Verified: the owner asked to proceed on the recommended directions of the project-query and mcp-server grill logs on 2026-10-27; they remain recommendations, not confirmations.

## 2. Desired Outcome

### Goals

- [ ] Search by text and by state, provider, and identity status, with stable order and pagination.
- [ ] Return one project with identity, checkouts, and open candidates.
- [ ] Report index status including freshness.
- [ ] Never write, scan, or expose a local path by default.

### Team Focus

Interface contracts, trust boundary (paths), determinism, bounded output, read-only enforcement.

### Success Criteria

- [ ] Identical queries return identical output.
- [ ] A read-only connection cannot be written through any query function.
- [ ] Default and maximum page sizes are 20 and 100.
- [ ] No result contains an absolute path unless asked.

## 3. Scope

### In Scope

- `search_projects`, `get_project`, `get_index_status`, envelope, cursor, errors.
- Filters available from stored data: `state`, `provider`, `identity_status`.

### Out of Scope

- `get_project_context`, `find_related_projects`, `get_project_dependencies`, and the language, technology, documentation, OpenSpec, tests, and lifecycle filters: they need detectors and a profile.
- The MCP server, transports, and Pydantic tool schemas (`be-mcp-skeleton`).
- Full-text search (FTS5); substring matching suffices for names and remote identities.
- Any refresh or scan.

### Constraints

Standard library; read-only; bounded; deterministic.

## 4. Stakeholders and Impact

- **Primary stakeholders:** coding agents (through the MCP change); the owner.
- **Affected components or capabilities:** new `vyasa.application.query`; reuses `vyasa.adapters.sqlite`.
- **Dependencies:** all merged index changes.
- **Compatibility considerations:** new surface only.

## 5. Proposed Direction

Pure functions taking a read-only connection and returning plain dictionaries in the envelope `{schema_version, data, meta}`. Order is `lower(display_name)` then `project_id`; the cursor is that pair, opaque. Unknown filter values are errors. Considered: building queries in the MCP layer (couples logic to the transport) and an FTS index (not needed yet).

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Search is deterministic and bounded | stable order, pages | Must |
| REQ-002 | Filters validate | unknown values rejected | Must |
| REQ-003 | Project details carry identity and review | missing marked | Must |
| REQ-004 | Status reports freshness | current, stale, partial, unknown | Must |
| REQ-005 | Read-only, paths omitted | safe by default | Must |

## 7. Risks and Open Questions

### Risks

| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Schema shape changes when detectors arrive | Client churn | Versioned envelope; new fields are additive |
| `lower()` is ASCII only | Odd ordering for non-ASCII names | Documented; order stays deterministic |

### Assumptions

- Recommended search rules (name substring, AND across filter groups, OR within) are accepted.

### Open Questions

- [ ] Whether `local_checkout_available` should be stricter than "has an active checkout".

## 8. Acceptance Summary

- [ ] Every spec scenario has a test against a real database file.
- [ ] `pytest`, `verify_workflows.py`, `verify_knowledge.py`, `openspec validate` pass.

## 9. Traceability

- **OpenSpec Change ID:** `be-project-query-basics`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-project-query-basics`
- **Requirement package:** `docs/requirements/project-query/requirement.md`
- **Knowledge references:**
  - `knowledge/architecture/mcp-interface.md` — envelope, conventions, search semantics
  - `knowledge/decisions/mcp-local-paths-omitted-by-default.md` — paths omitted
  - `knowledge/concepts/freshness-and-staleness.md` — freshness terms
  - `knowledge/decisions/review-decisions-stay-local.md` — candidates in details
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/local-index`, `openspec/specs/project-identity`, `openspec/specs/identity-review`, `openspec/specs/review-candidates`
- **Related ADRs:** `knowledge/decisions/mcp-local-paths-omitted-by-default.md`

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
