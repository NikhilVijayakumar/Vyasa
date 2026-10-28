# Change Proposal: be-framework-detector

## Why

FR-025 asks Vyasa to report what each checkout is built with, from the dependencies declared in its standard manifests. The scan reports languages, counts, and markers from names only and has never opened a repository file, so an agent still has to open a project to learn its frameworks. This change reads four ecosystems' root manifests under strict safety rules, maps dependencies to technologies through a registry, stores the result on the observation, and exposes it in project details and a `technology` search filter.

## What Changes

- **framework-detection**: a strict manifest reader, pure parsers for `pyproject.toml`, `requirements*.txt`, `package.json`, `Cargo.toml`, and `go.mod`, a versioned technology registry, per-ecosystem states, storage on the checkout observation with scoped capped dependencies and technologies.
- **project-query**: `search_projects` gains `technology`; `get_project` lists `frameworks` per checkout. The MCP tool descriptions and snapshot change accordingly.

## 1. Problem and Motivation

### Current Situation
`scan_checkout` (`src/vyasa/application/scanning/checkout_scan.py`) walks once and returns counts, languages, and markers; the observation (`language_observations`, migrations 0006–0008) stores them. No code reads a repository file except the profile and ignore file. The requirement package `docs/requirements/framework-detection/` is grilled; the owner decided Q2–Q6, Q8, Q9, and Q10 on 2026-10-28.

### Problem
FR-025 cannot be verified, and agents cannot search for projects by framework. Reading manifests from untrusted repositories needs explicit safety rules before any code does it.

### Evidence
- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` §9.4 defines the detector and forbids flattening scopes and speculative parsing.
- `docs/requirements/decisions-for-review.md` Q2 names the Phase 1 manifests.
- Python 3.12 provides `tomllib` and `json` in the standard library (verified 2026-10-28).

## 2. Desired Outcome

### Goals
- [ ] The scan reads supported root manifests safely and records technologies with their scopes.
- [ ] Hostile or malformed files produce a fixed status, never a guess, and never hide other manifests.
- [ ] Details show per-ecosystem states; search filters by technology.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in the specs has a passing test, including hostile-file fixtures and persistence against a real database file.
- [ ] No repository code is executed or imported, and `setup.py` is never read.
- [ ] The MCP tool snapshot test passes with the new parameter.

## 3. Scope

### In Scope
- `technologies.json` registry (version 1), its loader, and the parsers.
- A strict reader adapter; detection in `scan_checkout`; migration 0009; storage; details; the `technology` filter; MCP declaration.

### Out of Scope
- Dockerfile, compose, `setup.cfg`, `tsconfig.json`, Maven, Gradle, Unreal; lock files; transitive dependencies; internal-relationship matching (§9.10).
- Nested and workspace member manifests (counted, not parsed).
- Synchronization of technologies (machine-local in phase 1).

### Constraints
Standard library only. Python 3.12+. Repository content is untrusted and never executed. No file text is stored; no absolute path is stored or returned.

## 4. Stakeholders and Impact

- **Primary stakeholders:** agents querying the index and maintainers running scans.
- **Affected components or capabilities:** `adapters/filesystem` (new reader), `domain` (new modules), `application/scanning`, `application/indexing/scan.py`, `adapters/sqlite/projects.py` and migrations, `application/query.py`, `adapters/mcp/server.py`.
- **Dependencies:** `be-project-markers` (merged).
- **Compatibility considerations:** additive migration; `scan_checkout` called without a registry behaves as before; existing observations report `not_assessed` until the next scan; existing tool parameters and fields are unchanged.

## 5. Proposed Direction

Read after the walk, from the walk's own file list, with one reader that enforces the safety rules; parse with pure functions; map through the registry; store per manifest, dependency, and technology under the observation; derive ecosystem states when reading. Alternatives (any-depth parsing, lenient parsing, following links, a YAML dependency, free-text dependency search) are rejected in `knowledge/decisions/framework-detection-from-manifests.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Strict reader | Regular root files only, 1 MiB, strict UTF-8, nothing executed | Must |
| REQ-002 | Per-manifest status | One bad file does not hide others; fixed reasons | Must |
| REQ-003 | Scoped capped dependencies | Constraint and scope kept; cap 200 with total; skips counted | Must |
| REQ-004 | Registry technologies | Only from the registry; scopes preserved | Must |
| REQ-005 | Ecosystem states | Absence only after a complete assessment | Must |
| REQ-006 | Nested and workspace | Counted or flagged, not expanded | Must |
| REQ-007 | Stored on the observation | Same walk, retention, and failure isolation | Must |
| REQ-008 | Filter and details | `technology`, `frameworks` per checkout | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| A crafted manifest exhausts a parser | Scan stalls or crashes | 1 MiB cap, recursion errors caught, per-manifest isolation, fixture for deep nesting |
| TOML or JSON parser raises an unexpected exception type | Detection fails | The reader catches `Exception` per manifest and records `malformed`; the checkout still isolates failures |
| Registry vocabulary is incomplete | Technologies missed | Unknown dependencies are still stored; growth is a data change |
| Dependency lists bloat the index | Storage | Cap of 200 per manifest, four ecosystems at the root |

### Assumptions
- Matching registry entries by normalized dependency name is enough for the seed vocabulary.
- A Go module path is matched exactly against registry entries.

### Open Questions
- [ ] Owner confirmation of Q7 and Q11–Q15.

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python -m pytest` and `python scripts/verify_workflows.py` show no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-framework-detector`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-framework-detector`
- **Requirement package:** `docs/requirements/framework-detection/requirement.md`
- **Knowledge references:** `knowledge/decisions/framework-detection-from-manifests.md` — reading, scopes, states; `knowledge/decisions/technology-registry-as-data.md` — registry; `knowledge/decisions/scan-limits-and-symlink-defaults.md` — limits and links; `knowledge/decisions/partial-results-never-imply-absence.md` — partial results; `knowledge/decisions/checkout-walk-observation.md` — one walk and observation; `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.4
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/project-query`, `openspec/specs/project-markers`
- **Related ADRs:** `knowledge/decisions/framework-detection-from-manifests.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved (`docs/requirements/framework-detection/grill-log.md`).
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
