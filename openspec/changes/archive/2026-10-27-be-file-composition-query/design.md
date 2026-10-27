# Design: be-file-composition-query

## 1. Overview

### Purpose
Store file-type counts from the scan's single walk and expose them through the existing read-only queries.

### Scope
A shared scan function, a migration, a store change, query changes, and the MCP declaration.

### Design Principles
Walk once. Reuse the observation and the query patterns of the language change. Derive what can be derived. Partial and absent are results.

## 2. Context and Constraints

### Current State
`compose` and `detect_languages` each call `walk_checkout` and classify the same names. `scan_workspace` calls `detect_languages`; `projects._store_languages` inserts the observation and rows and prunes to two. `search_projects` builds fixed SQL clauses with bound values; the language filter joins the current observation by `MAX(observation_id)`.

### Constraints
- Technical constraints: Python 3.12+, standard library only, SQLite.
- Security and privacy constraints: no path in the new field; values bound as parameters.
- Performance and reliability constraints: one walk per eligible checkout per scan (no extra cost).
- Compatibility and migration constraints: additive nullable columns; existing behavior kept.
- Operational constraints: single-writer lock; queries use a read-only connection.

### Existing Decisions and Conventions
Language observations in the index, partial results never imply absence, freshness without query-time I/O, file composition data and limits.

### Knowledge References
- `knowledge/decisions/checkout-walk-observation.md` — one walk, shared observation, filter.
- `knowledge/decisions/language-observations-in-index.md` — observation storage and retention.
- `knowledge/decisions/file-composition-data-and-limits.md` — data and limits.
- `knowledge/decisions/partial-results-never-imply-absence.md` — partial semantics.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| One walk feeds counts and languages | `scan_checkout`; `compose` and `detect_languages` delegate | Unit tests; a counting `walk_checkout` stub proves one call |
| Counts stored on the observation | `_store_languages` writes the three columns | Persistence tests on a real database file |
| Failed and older have no counts | null columns | Persistence and migration tests |
| Search filter | clauses in `search_projects` | Contract tests via `queries` and the MCP snapshot |
| Details per checkout | `projects.checkout_composition` | Contract tests |
| Read-only | queries read the index only | Test with `os.walk` patched to raise |

## 4. Architecture and Design

### Architectural Approach
`scan_checkout` (application) walks once, tallies classes with `FileTypes.classify`, runs `languages_of` on the same names, and returns a `CheckoutScan` holding a `FileComposition` and a `LanguageReport` that share `Evidence`. `compose` returns `.composition`; `detect_languages` returns `.languages`. `scan_workspace` takes a `detect` callable that returns a `CheckoutScan`; the outcome keeps the scan, and `_store_languages` writes counts from its composition.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.languages` | `CheckoutScan`; `LanguageOutcome` carries it | domain |
| `vyasa.domain.file_composition` | `documentation_only(code, documentation, complete)` shared by the property and the read model | stdlib |
| `vyasa.application.scanning.checkout_scan` | `scan_checkout` | walk adapter, domain |
| `vyasa.application.scanning.file_composition` and `languages` | thin views | `checkout_scan` |
| `vyasa.adapters.sqlite.projects` | store counts; `checkout_composition`; filter SQL | sqlite |
| `vyasa/adapters/sqlite/migrations/0007_composition_counts.sql` | columns | none |
| `vyasa.application.query`, `vyasa.adapters.mcp.server` | parameter, validation, details, description | adapters |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Scan: `scan_checkout` per eligible candidate (failure becomes a failed outcome) → `store_run` → `upsert` + `_store_languages` writes the observation, rows, and counts → prune to two. Query: validate → SQL over the current observation of active checkouts → items; details read the observation and derive the indicator.

## 5. Data and State Management

The filter for true is `status = 'complete' AND code_files IS NOT NULL AND code_files = 0 AND documentation_files > 0`; for false, `status = 'complete' AND code_files IS NOT NULL AND NOT (code_files = 0 AND documentation_files > 0)`. Both use the current observation and `state = 'active'`. The read model derives `documentation_only` through the same domain function as `FileComposition`, so there is one rule.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Detection raises | Failed observation, counts empty, run partial | Fix and rescan |
| Bound or unreadable directory | Partial observation, lower-bound counts | Raise limits or accept |
| Non-boolean filter | `INVALID_INPUT` | Caller corrects |

## 7. Security and Privacy

Trust boundary as in the contract. The walk is unchanged (no symlink follow, no file opened). No path is returned. No material privacy impact beyond the existing index.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Integrity | Language sum equals the code count | One file list | Sum test on stored rows |
| Honesty | Unknown matches neither value | `status = 'complete'` in both clauses | Partial and not-counted tests |
| Cost | No extra walk | `scan_checkout` | Single-call stub test |
| Compatibility | Public functions unchanged | Delegation | Existing tests unchanged |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in both spec files.

### Test Strategy
Unit tests for `scan_checkout`; persistence tests against a real temporary SQLite file; contract tests through `queries` and the MCP snapshot (`tests/snapshots/mcp_tools.json`). The existing `detect` stubs in `tests/test_language_query.py` are wrapped to return a `CheckoutScan`.

### Testability
`detect`, `discover`, the clock, and the walk limits are injectable.

### Verification Evidence
`python -m pytest`, `python scripts/verify_workflows.py`; skips are reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Shared scan and delegation, then migration and storage, then the filter, then details, then the MCP declaration.

### Migration and Rollout
Additive migration on open; existing observations read `not_counted` until the next scan.

### Documentation and Operations
Update the tool descriptions and `knowledge/log.md`.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/checkout-walk-observation.md`; see `adr.md`.

## 12. Risks, Trade-offs, and Open Questions

### Risks
The observation tables keep language-oriented names; documented, rename deferred.

### Trade-offs
Reusing the observation couples counts to language retention; the alternative (separate tables) duplicates status and failure columns.

### Open Questions
None.

## 13. Traceability

Proposal, specs, and contract share the change ID `be-file-composition-query`; requirement package `docs/requirements/file-composition/`.

## 14. Design Readiness Review

- [x] Requirements are traced to design elements and checks.
- [x] Boundaries, failure handling, and the trust boundary are stated.
- [x] The architecture decision checkpoint is answered.
- [x] Risks and trade-offs are visible.

**Status:** Draft
