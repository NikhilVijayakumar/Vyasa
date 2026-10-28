# Change Proposal: be-project-report

## Why

The profile holds a short, bounded summary of a project. A coding agent working in a repository understands far more (architecture, modules, flows, how to run it, risks), and that knowledge is lost when the session ends. Vyasa cannot call a model, so the agent must write it. Vyasa needs to give the agent a template over MCP, read what the agent wrote on the next scan, and serve it to any later agent from the index.

## What Changes

- **project-report**: a fixed-section markdown report at `.vyasa/project-report.md`, read by the scan as bounded text and stored by section with its hash and scan time.
- **mcp-server**: `get_report_template` (no index) and `get_project_report` (from the index), plus a report status object in `get_project`.
- **profile-context**: the context workflow adds a step that names the report template.

## 1. Problem and Motivation

### Current Situation

`get_profile_guide` and `get_profile_context` let an agent write a structured profile. The profile has length and size caps and holds no long-form description.

### Problem

There is no durable place for an agent's detailed reading of a repository, and no way for another agent, in another repository, to retrieve it through Vyasa.

### Evidence

- Verified: profile schema v2 is bounded by design (`knowledge/decisions/profile-schema-v2-full-template.md`).
- Verified: the owner chose a long-form report stored as a bounded copy in the index on 2026-10-28 (grill Q1, Q2).

## 2. Desired Outcome

### Goals

- [ ] An agent can fetch a template with no index and write a valid report.
- [ ] `vyasa scan` stores the report by section, bounded, with source and time.
- [ ] Any agent can fetch the report, whole or by section, from the index.
- [ ] A hostile report cannot break the scan or the server.

### Team Focus

MCP tool contract, untrusted text handling, size bounds, no drift between the template and the reader, scan stays read-only.

### Success Criteria

- [ ] The template's example report validates and stores every section.
- [ ] Limits in the template equal the reader's constants.
- [ ] A repository hash is unchanged by a scan.
- [ ] The tool snapshot lists the two new read-only tools and no new input path.

## 3. Scope

### In Scope

- Report definition, reader, storage migration, two tools, status in `get_project`, workflow step, docs.

### Out of Scope

- Vyasa writing the report or calling any model.
- Staleness comparison with the head commit (stored declared commit and date only).
- Monorepo component reports, full-text search, synchronization.

### Constraints

Standard library; read-only MCP; stdio only; report text is untrusted data and local.

## 4. Stakeholders and Impact

- **Primary stakeholders:** coding agents; maintainers.
- **Affected components or capabilities:** profile detection area of the scanner, SQLite schema, MCP server, profile context.
- **Dependencies:** `be-profile-v2`, `be-profile-context`, `be-standalone-build` (merged).
- **Compatibility considerations:** new migration (additive tables); two added tools; existing tool fields unchanged except one added `report` key in `get_project`.

## 5. Proposed Direction

One domain module defines the sections (names, purposes, limits). The template, the reader, and the tool read it. The scan reads `.vyasa/project-report.md` with the same safe-read rules as the profile (real directory, real file, size cap), splits on second-level headings, keeps known sections up to the limit, and stores sections, hash, and status per checkout. The tool returns stored sections marked as declared. Considered: raising profile limits, serving only a path, and a model-written report; all rejected in `knowledge/decisions/project-report-in-the-repository.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | The template is served without an index | works first | Must |
| REQ-002 | The scan reads and bounds the report | safe storage | Must |
| REQ-003 | Unknown and oversize content is reported | no silent loss | Must |
| REQ-004 | The report is served from the index as declared data | cross-repo use | Must |
| REQ-005 | `get_project` shows status only | small default response | Must |
| REQ-006 | A failure keeps other data | integrity | Must |

## 7. Risks and Open Questions

### Risks

| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Agent invents facts | Misleading report | Template says omit unknowns; text is labelled declared |
| Prompt injection in report text | Agent misled | Returned as typed data with a warning field; never as instructions |
| Secrets written into the report | Leak into the index | Reject credential-bearing URLs; template forbids secrets |
| Report grows the index | Disk use | 256 KiB per checkout |

### Assumptions

- Agents can write files in the repository they work in.

### Open Questions

- [ ] Staleness check against the head commit.
- [ ] Report per component in monorepos.

## 8. Acceptance Summary

- [ ] Every spec scenario has a test.
- [ ] `pytest`, `verify_workflows.py`, `verify_knowledge.py`, `verify_requirements.py`, `openspec validate` pass.

## 9. Traceability

- **OpenSpec Change ID:** `be-project-report`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-project-report`
- **Requirement package:** `docs/requirements/project-report/requirement.md`
- **Knowledge references:**
  - `knowledge/decisions/project-report-in-the-repository.md` — the decision
  - `knowledge/decisions/profile-context-for-agents.md` — Vyasa never launches an agent
  - `knowledge/concepts/untrusted-content.md` — report text is data
  - `knowledge/decisions/mcp-local-paths-omitted-by-default.md` — no local paths in responses
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/project-profile`, `openspec/specs/profile-context`, `openspec/specs/mcp-server`
- **Related ADRs:** `knowledge/decisions/project-report-in-the-repository.md`

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
