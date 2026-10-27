# Change Proposal: be-language-query

## Why

The language detector (`be-language-detector`) returns results only to a caller of a library function. FR-023 needs agents to see a project's languages and narrow a search by them. This change stores languages during the scan, shows them per checkout in project details, and adds a language filter to project search, without any query touching the filesystem.

## What Changes

- **language-observations**: the scan detects languages once per eligible checkout and stores an observation (current and previous) with one row per language and status; a failure is stored as a failed observation and the scan continues.
- **project-query**: `search_projects` gains `language` and `language_status`; `get_project` lists languages per checkout. The MCP tool descriptions and snapshot change accordingly.

## 1. Problem and Motivation

### Current Situation
`detect_languages` exists (`src/vyasa/application/scanning/languages.py`) but nothing calls it. The index has `checkouts` and `checkout_profiles` (migration 0005) and no language storage. `search_projects` filters by query, state, provider, and identity status. The requirement package `docs/requirements/language-detection/` records a second grill (Q9–Q19) with eight owner decisions and three recommendations.

### Problem
An agent cannot ask "which of my projects are Python" or learn what a project is written in without opening it.

### Evidence
- `src/vyasa/application/query.py` `search_projects` has no language parameter (verified 2026-10-27).
- `src/vyasa/application/indexing/scan.py` calls only `discover` and `store_run`.
- `docs/requirements/language-detection/features/fr-023-language-query.feature` (proposed scenarios).

## 2. Desired Outcome

### Goals
- [ ] After a scan, each eligible checkout has a stored language observation.
- [ ] `search_projects` filters by language and status; `get_project` shows languages per checkout.
- [ ] No query reads the filesystem; a partial or missing observation never reads as "no languages".

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in the specs has a passing test, including the SQLite persistence layer against a real database file.
- [ ] The MCP tool snapshot test passes with the new parameters.
- [ ] Rescanning keeps exactly the current and previous observation per checkout.

## 3. Scope

### In Scope
- Migration 0006 (`language_observations`, `checkout_languages`).
- Scan integration: detect per eligible candidate, store inside the candidate's transaction.
- `search_projects` filter and `get_project` output; the MCP tool signature and description.

### Out of Scope
- File composition persistence and its filter (`be-file-composition-query`).
- Incremental rescan, share thresholds, per-directory results, synchronization to the shared registry.
- Any change to profile `technologies`.

### Constraints
Standard library only. Python 3.12+. No path is returned by the new fields. The index is opened read-only for queries.

## 4. Stakeholders and Impact

- **Primary stakeholders:** agents querying the index, and maintainers running scans.
- **Affected components or capabilities:** `application/indexing/scan.py`, `adapters/sqlite/projects.py` and migrations, `application/query.py`, `adapters/mcp/server.py`, `domain/discovery.py` (`Candidate`).
- **Dependencies:** `be-language-detector` (merged).
- **Compatibility considerations:** the migration only adds tables. Existing indexes upgrade on open; existing checkouts report `not_observed` until the next scan. Existing tool parameters and results are unchanged; `languages` is an added field.

## 5. Proposed Direction

Detection runs in `scan_workspace` between discovery and storing, following how the profile is carried on `Candidate`. Storage is rows per language under an observation per checkout. Alternatives (query-time detection, a separate step, a JSON blob) are rejected in `knowledge/decisions/language-observations-in-index.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Scan stores observations | One per eligible checkout, current and previous kept | Must |
| REQ-002 | Partial and failed observations | Stored and flagged; absence never implied | Must |
| REQ-003 | Language filter | Label list, optional status, any present checkout | Must |
| REQ-004 | Unknown label | `INVALID_INPUT` listing allowed labels | Must |
| REQ-005 | Details per checkout | Never summed; `not_observed` when absent | Must |
| REQ-006 | Separate from profile | `technologies` untouched | Must |
| REQ-007 | Query is read-only | No filesystem access | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Every scan re-walks every checkout | Slower scans | The observation records the walk's duration; incremental rescan is a later change |
| Detection runs before the lock is taken | A held lock is found only at store time | Detection is read-only and cheap to discard; the lock check is unchanged |
| A crash between candidates | Some checkouts have older observations | Each candidate commits alone, as today; the run is partial |

### Assumptions
- Detection for a candidate is done in `scan_workspace` and passed on `Candidate`.
- Inaccessible and missing checkouts keep their last observation.

### Open Questions
- [ ] Owner confirmation of Q17 (`not_observed`), Q18 (failed observation isolates one checkout), and Q19 (accept the extra walk).

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python -m pytest` and `python scripts/verify_workflows.py` show no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-language-query`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-language-query`
- **Requirement package:** `docs/requirements/language-detection/requirement.md`
- **Knowledge references:** `knowledge/decisions/language-observations-in-index.md` — storage and filter; `knowledge/decisions/language-evidence-statuses.md` — statuses; `knowledge/decisions/retention-defaults.md` — current and previous; `knowledge/decisions/observation-freshness-without-query-time-io.md` — no query I/O; `knowledge/decisions/partial-results-never-imply-absence.md` — partial results
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/project-query`, `openspec/specs/local-index`, `openspec/specs/mcp-server`
- **Related ADRs:** `knowledge/decisions/language-observations-in-index.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved (`docs/requirements/language-detection/grill-log.md`, Q9–Q19).
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
