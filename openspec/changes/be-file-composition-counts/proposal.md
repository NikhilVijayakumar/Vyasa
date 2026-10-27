# Change Proposal: be-file-composition-counts

## Why

FR-021 asks Vyasa to report code, documentation, and other file counts per checkout so a documentation-only project can be told from a code-heavy one without reading any file. Nothing in the repository implements any detector yet. This change delivers the first, self-contained core: versioned file-type data, a bounded walk, and honest counts.

## What Changes

- **file-composition**: a library core that classifies files by extension from versioned data, walks one checkout under depth, time, and entry bounds without following symlinks, and returns counts, a completeness marker, a derived documentation-only indicator, and evidence.

## 1. Problem and Motivation

### Current Situation
The requirement package `docs/requirements/file-composition/` is reviewed (owner confirmed Q4 and Q8 on 2026-10-27). The repository holds no source tree, no `pyproject.toml`, no detector framework, and no discovery code.

### Problem
FR-021 cannot be verified without code. The detector framework (`be-detector-framework`) and discovery (`be-discover-one-root`) are separate changes that do not exist yet, so FR-021 cannot wait for them to start.

### Evidence
- `ls` of the repository root on 2026-10-27: `AGENTS.md CLAUDE.md GEMINI.md README.md docs knowledge openspec scripts skills`; no `src/`.
- The metadata-and-evidence package lists `be-detector-framework` as a proposed, not delivered, change.
- A predecessor tool counted unknown file types as code (reviewed 2026-10-27), which is the failure this change must not repeat.

## 2. Desired Outcome

### Goals
- [ ] A function returns exact counts for a complete walk and lower-bound counts with a named limit for a partial one.
- [ ] Classification data is versioned and validated.
- [ ] The core has no dependency on infrastructure and can later be wrapped as a detector without change.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in `specs/file-composition/spec.md` has a passing test.
- [ ] Fixtures cover documentation-only, mixed, unknown types, over the cap, empty, unreadable directory, and a symlink escape.
- [ ] The same tree gives the same result under shuffled directory order.

## 3. Scope

### In Scope
- Project scaffolding as a prerequisite: `pyproject.toml`, `src/vyasa` package, `tests/`.
- `FileTypes` (loaded and validated from a versioned data file), `WalkLimits`, `FileComposition`, and `compose(root, types, limits, exclusions)`.
- A bounded walk adapter and the default exclusion set.

### Out of Scope
- Detector registry, evidence persistence, SQLite, MCP tools, project details, and the search filter (`be-file-composition-query`).
- Workspace configuration and discovery (the caller supplies a checkout path).
- Synchronization of counts (machine-local in phase 1, owner decision Q8).
- The language detector and its per-language histogram.

### Constraints
Standard library only for the core; `pytest` for tests. Python 3.12+. File content is never read; no path is returned, only counts.

## 4. Stakeholders and Impact

- **Primary stakeholders:** maintainers and agents that will query projects.
- **Affected components or capabilities:** new package `src/vyasa`, new `tests/`, new data file.
- **Dependencies:** none. Later wrapped by the detector framework.
- **Compatibility considerations:** none; new code.

## 5. Proposed Direction

Layered as `knowledge/architecture/system-architecture/structure.md` proposes: a pure domain module for the model and classification, an application function that composes them, and a filesystem adapter that owns the walk. Detailed trade-offs and the durable decision are in `knowledge/decisions/file-composition-data-and-limits.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Counts classify by extension and agree | code + documentation + other = total | Must |
| REQ-002 | Unknown types are other | No unknown file counted as code | Must |
| REQ-003 | Documentation-only indicator | True, false, or unknown | Must |
| REQ-004 | Bounded walk, partial marker | Bound named; indicator unknown | Must |
| REQ-005 | Symlinks and exclusions | Nothing outside the checkout counted | Must |
| REQ-006 | Evidence | Data version, exclusions, completeness | Must |
| REQ-007 | Validated versioned data | Invalid data is rejected | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Depth 6 makes common nested layouts partial | Many counts partial | Limit is a parameter; validate against real workspaces and adjust the default |
| First code in the repository sets structure | Layout churn | Follow the proposed layout; create only the packages used |
| Time limit makes tests flaky | Unreliable tests | The clock is injected; no test sleeps |

### Assumptions
- A checkout path is given; discovery is not needed to test the core.

### Open Questions
- [ ] Whether the default depth of 6 suits counting; validated later against representative workspaces (not blocking).

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python3 scripts/verify_workflows.py` shows no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-file-composition-counts`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-file-composition-counts`
- **Requirement package:** `docs/requirements/file-composition/requirement.md`
- **Knowledge references:** `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.13 detector; `knowledge/decisions/file-composition-data-and-limits.md` — data and limits; `knowledge/decisions/scan-limits-and-symlink-defaults.md` — depth, time, symlinks; `knowledge/decisions/partial-results-never-imply-absence.md` — partial counts; `knowledge/architecture/system-architecture/structure.md` — layout; `knowledge/practices/vertical-slices.md` — slicing
- **Related issues or references:** None
- **Related existing specifications:** None
- **Related ADRs:** `knowledge/decisions/file-composition-data-and-limits.md`

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
