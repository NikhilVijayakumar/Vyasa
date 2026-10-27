# Change Proposal: be-project-markers

## Why

FR-024 asks Vyasa to report whether a checkout has a README, documentation, agent instruction files, an OpenSpec setup, and tests, from names and directories alone. The scan reports languages and file counts but nothing about these markers, so an agent must open a project to learn them. This change detects the markers on the scan's single walk, stores them on the observation, and exposes them in project details and a search filter, without reading any file.

## What Changes

- **project-markers**: versioned rules; a pure detector over the walk's file and directory paths that reports eight markers with evidence; storage on the checkout observation with three states and a not-assessed state for older observations.
- **project-query**: `search_projects` gains `marker` and `marker_state`; `get_project` lists `markers` per checkout. The MCP tool descriptions and snapshot change accordingly.

## 1. Problem and Motivation

### Current Situation
`scan_checkout` (`src/vyasa/application/scanning/checkout_scan.py`) walks once and returns counts and languages; the observation (`language_observations`, migrations 0006–0007) stores them. `walk_checkout` returns only base file names. The requirement package `docs/requirements/project-markers/` is grilled; the owner decided Q2, Q3, Q5, Q6, Q9, and Q10 on 2026-10-27.

### Problem
FR-024 cannot be verified, and agents cannot search for projects with tests, documentation, or OpenSpec setups. The walk does not report directories or relative paths, which markers need.

### Evidence
- `src/vyasa/adapters/filesystem/checkout_walk.py`: `WalkResult` has `names` and `stopped_by` only (verified 2026-10-27).
- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` §9.5–9.9 define the detectors and the separate-indicator rules.

## 2. Desired Outcome

### Goals
- [ ] The scan detects eight markers per eligible checkout from the same walk.
- [ ] Details show each marker as detected (with evidence), not detected, or unknown, or the checkout as not assessed.
- [ ] Search filters by marker and state without touching the filesystem.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in the specs has a passing test, including persistence against a real database file.
- [ ] `scan_checkout` still returns the same counts and languages.
- [ ] The MCP tool snapshot test passes with the new parameters.

## 3. Scope

### In Scope
- `markers.json` rules data, a loader with validation, and a pure `markers_of` function.
- `walk_checkout` also reporting relative file paths and directories.
- Migration 0008 (marker column and table), storing in the scan, details, filter, MCP declaration.

### Out of Scope
- Reading any file: OKF, OpenSpec configuration validity, README parsing or quality.
- Test framework configuration and dependencies; test execution.
- Synchronization of markers (machine-local in phase 1).

### Constraints
Standard library only. Python 3.12+. File content is never read; no absolute path is stored or returned.

## 4. Stakeholders and Impact

- **Primary stakeholders:** agents querying the index and maintainers running scans.
- **Affected components or capabilities:** `adapters/filesystem/checkout_walk.py`, `application/scanning`, `application/indexing/scan.py`, `domain/languages.py`, `adapters/sqlite/projects.py` and migrations, `application/query.py`, `adapters/mcp/server.py`.
- **Dependencies:** `be-file-composition-query` (merged).
- **Compatibility considerations:** `WalkResult` gains fields (existing ones unchanged); additive migration; existing observations report `not_assessed`; existing tool parameters and fields are unchanged.

## 5. Proposed Direction

Extend the walk to report relative paths and directories; run a pure detector over them with versioned rules; store one row per detected marker linked to the observation; derive `not_detected` and `unknown` when reading. Alternatives (file reading, count-only, uncapped paths, any-depth everywhere) are rejected in `knowledge/decisions/project-marker-observations.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Markers by names and directories | Eight markers by documented rules | Must |
| REQ-002 | Location rules | Root-only versus any depth per marker | Must |
| REQ-003 | Three states | Not detected only after a complete assessment | Must |
| REQ-004 | Separate OpenSpec indicators | Directory without config implies no config | Must |
| REQ-005 | Capped relative evidence | At most 20 paths and the total; no absolute path | Must |
| REQ-006 | Stored on the observation | Same walk, retention, and status | Must |
| REQ-007 | Not assessed | Older and failed observations never read as not detected | Must |
| REQ-008 | Filter and details | `marker`, `marker_state`, `markers` per checkout | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Walk change affects counts or languages | Regression | Existing tests stay unchanged; the new fields are additive |
| Large trees make path lists big in memory | Memory | Only matching paths are kept; the walk is already capped at 50,000 entries |
| Test name patterns give false positives | Overstated "tests" | The matching rule is recorded; the meaning is "detected by these rules" |
| Directories at the depth limit are listed but not entered | Misleading evidence | They are reported as directories only; contents are unknown and the walk is partial |

### Assumptions
- Matching file-name patterns is case-sensitive; directory and fixed names are case-insensitive.
- A directory removed by the ignore file or exclusions is not reported.

### Open Questions
- [ ] Owner confirmation of Q4, Q7, Q8, Q11, and Q12.

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python -m pytest` and `python scripts/verify_workflows.py` show no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-project-markers`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-project-markers`
- **Requirement package:** `docs/requirements/project-markers/requirement.md`
- **Knowledge references:** `knowledge/decisions/project-marker-observations.md` — rules, states, evidence; `knowledge/decisions/checkout-walk-observation.md` — one walk and observation; `knowledge/decisions/partial-results-never-imply-absence.md` — partial results; `knowledge/decisions/mcp-local-paths-omitted-by-default.md` — paths; `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.5–9.9
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/project-query`, `openspec/specs/file-composition`, `openspec/specs/language-observations`
- **Related ADRs:** `knowledge/decisions/project-marker-observations.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved (`docs/requirements/project-markers/grill-log.md`).
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
