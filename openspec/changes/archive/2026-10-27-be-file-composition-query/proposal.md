# Change Proposal: be-file-composition-query

## Why

FR-021 asks Vyasa to report per checkout how many files are code, documentation, or other, and to let an agent find documentation-only projects. The counts exist as a library function (`compose`) but are neither stored nor queryable, and walking each checkout a second time for them would double scan cost. This change makes the scan walk once, store the counts with the language observation, and expose them in project details and a `documentation_only` search filter.

## What Changes

- **file-composition**: the scan derives the counts and the language results from one walk and stores the counts on the checkout's observation; a stored observation without counts reads as not counted.
- **project-query**: `search_projects` gains `documentation_only`; `get_project` lists `composition` per checkout with a derived indicator. The MCP tool description and snapshot change accordingly.

## 1. Problem and Motivation

### Current Situation
`compose` (`src/vyasa/application/scanning/file_composition.py`) and `detect_languages` (`.../languages.py`) each call `walk_checkout`. The scan calls only `detect_languages` and stores languages in `language_observations` (migration 0006). Nothing stores or serves counts. The requirement package `docs/requirements/file-composition/` records a second grill (Q13–Q17).

### Problem
An agent cannot ask for documentation-only projects or see how much code a project holds without opening it. A separate walk for counts would double scan input and could disagree with the language histogram about the tree.

### Evidence
- `src/vyasa/application/indexing/scan.py` calls only `detect_languages` (verified 2026-10-27).
- `src/vyasa/application/query.py` has no composition field or filter.
- `docs/requirements/file-composition/grill-log.md` Q6 promises a histogram that sums to the code count; two walks cannot guarantee it under change.

## 2. Desired Outcome

### Goals
- [ ] One walk per checkout per scan feeds both results.
- [ ] Counts are stored on the observation and shown per checkout, never summed.
- [ ] `documentation_only` filters search; a partial or uncounted checkout matches neither value.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in the specs has a passing test, including persistence against a real database file.
- [ ] `compose` and `detect_languages` return what they did before.
- [ ] The MCP tool snapshot test passes with the new parameter.

## 3. Scope

### In Scope
- A shared `scan_checkout` over one walk; `compose` and `detect_languages` delegate to it.
- Migration 0007 adding nullable count columns to the observation.
- Storing counts in the scan; `documentation_only` filter; `composition` in details; MCP declaration.

### Out of Scope
- Renaming the observation tables, per-directory breakdowns, incremental rescan, synchronization of counts (machine-local, owner decision Q8).
- Any change to classification data or limits.

### Constraints
Standard library only. Python 3.12+. No path is returned. Queries read the index only.

## 4. Stakeholders and Impact

- **Primary stakeholders:** agents querying the index and maintainers running scans.
- **Affected components or capabilities:** `application/scanning`, `application/indexing/scan.py`, `domain/languages.py`, `adapters/sqlite/projects.py` and migrations, `application/query.py`, `adapters/mcp/server.py`.
- **Dependencies:** `be-file-composition-counts`, `be-language-detector`, `be-language-query` (all merged).
- **Compatibility considerations:** additive nullable columns. Existing observations report `not_counted` until the next scan. Existing tool parameters and fields are unchanged.

## 5. Proposed Direction

Extract one function that walks once and returns both results; keep the two public functions as thin views of it. Store the counts as columns on the existing observation. Derive the indicator when reading. Alternatives (a second walk, separate tables, storing the indicator) are rejected in `knowledge/decisions/checkout-walk-observation.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | One walk | Counts and language sum agree by construction | Must |
| REQ-002 | Counts stored on the observation | Code, documentation, other; shared status | Must |
| REQ-003 | Not counted is not zero | Old or failed observation reports `not_counted` | Must |
| REQ-004 | `documentation_only` filter | Any active checkout; unknown matches neither | Must |
| REQ-005 | Details per checkout | Counts and derived indicator, never summed | Must |
| REQ-006 | Queries are read-only | No filesystem access | Must |
| REQ-007 | Existing behavior kept | `compose` and `detect_languages` unchanged | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Refactor changes `compose` or `detect_languages` results | Regression | Existing tests stay unchanged and must pass; a new test compares both views to one scan |
| Observation tables are named for languages | Misleading names | Documented in the decision; rename deferred |
| The scan hook takes a different callable | Test churn | Only this repository's tests inject it; updated in the first slice |

### Assumptions
- The indicator and counts of a failed observation are not counted, never zero.

### Open Questions
- [ ] Owner confirmation of Q16 (`not_counted`) and Q17 (indicator derived, not stored).

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python -m pytest` and `python scripts/verify_workflows.py` show no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-file-composition-query`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-file-composition-query`
- **Requirement package:** `docs/requirements/file-composition/requirement.md`
- **Knowledge references:** `knowledge/decisions/checkout-walk-observation.md` — one walk, shared observation, filter; `knowledge/decisions/file-composition-data-and-limits.md` — data and limits; `knowledge/decisions/language-observations-in-index.md` — observation storage; `knowledge/decisions/partial-results-never-imply-absence.md` — partial results; `knowledge/decisions/observation-freshness-without-query-time-io.md` — no query I/O
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/file-composition`, `openspec/specs/language-observations`, `openspec/specs/project-query`
- **Related ADRs:** `knowledge/decisions/checkout-walk-observation.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved (`docs/requirements/file-composition/grill-log.md`, Q13–Q17).
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
