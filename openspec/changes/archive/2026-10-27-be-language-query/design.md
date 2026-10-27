# Design: be-language-query

## 1. Overview

### Purpose
Persist language observations during the scan and expose them through the existing read-only query functions and MCP tools.

### Scope
A migration, a store function in the SQLite adapter, scan enrichment, query changes, and the MCP declaration.

### Design Principles
Follow how the profile is carried and stored. Queries read stored data only. Every candidate commits alone. Partial and failed results are results.

## 2. Context and Constraints

### Current State
`repository_walk` attaches a `ProfileResult` to each eligible `Candidate`; `projects.upsert` stores it in `checkout_profiles` inside the candidate's `BEGIN IMMEDIATE` transaction. `scan_workspace` calls `discover(root)` then `store_run`. `search_projects` builds fixed SQL clauses with bound values; `_choices` validates against fixed sets.

### Constraints
- Technical constraints: Python 3.12+, standard library only, SQLite.
- Security and privacy constraints: no path in the new fields; values bound as parameters; the exception text is not stored.
- Performance and reliability constraints: one extra bounded walk per eligible checkout per scan.
- Compatibility and migration constraints: additive migration only; existing tool output keeps working.
- Operational constraints: single-writer lock; queries use a read-only connection.

### Existing Decisions and Conventions
Retention defaults (current and previous), observation freshness without query-time I/O, partial results never imply absence, read-only access policy.

### Knowledge References
- `knowledge/decisions/language-observations-in-index.md` — storage and filter.
- `knowledge/decisions/language-evidence-statuses.md` — statuses.
- `knowledge/decisions/retention-defaults.md` — keep two.
- `knowledge/decisions/observation-freshness-without-query-time-io.md` — no query I/O.
- `knowledge/decisions/partial-results-never-imply-absence.md` — partial results.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Scan stores an observation per checkout | `Candidate.languages`, `projects.store_languages` | Persistence tests on a real database file |
| Current and previous kept | prune inside `store_languages` | Persistence test with three scans |
| Partial rescan current and flagged | `status`, `stopped_by` columns | Persistence test with a small cap |
| Detection failure isolated | `scan_workspace` catches per candidate | Scan test with an injected failing detector |
| Not reached keeps observation | `store_languages` only called from `upsert` | Persistence test |
| Migration preserves the index | `0006_languages.sql` | Migration test on a version 5 database |
| Search by language and status | clauses in `search_projects` | Contract tests via `queries` and the MCP snapshot |
| Rejected values | `_choices` with fixed sets | Contract tests |
| Details per checkout | `projects.checkout_languages` | Contract tests |
| Separate from the profile | `languages` is a sibling of `profile` | Contract test |

## 4. Architecture and Design

### Architectural Approach
`scan_workspace` takes a `detect` callable (default wraps `detect_languages` with the shipped data). For each eligible candidate in a discovered run it computes a `LanguageOutcome` and rebuilds the candidate with `dataclasses.replace`, then calls `store_run` as before. `upsert` stores the outcome after `_store_profile`, in the same transaction.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.discovery.Candidate` | gains `languages: LanguageOutcome | None` | domain |
| `vyasa.domain.languages` | `LanguageOutcome` (report or failure reason) | domain |
| `vyasa.application.indexing.scan` | runs the detector per eligible candidate, isolating failures, marks the run partial on a failure | scanning |
| `vyasa.adapters.sqlite.projects` | `store_languages`, `checkout_languages` read helper, candidate filter SQL | sqlite |
| `vyasa.adapters.sqlite/migrations/0006_languages.sql` | tables and index | none |
| `vyasa.application.query` | parameters, validation, `languages` in details | adapters |
| `vyasa.adapters.mcp.server` | signature and description | queries |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Scan: discover → detect per eligible candidate (failure becomes a failed outcome) → `store_run` → per candidate `upsert` + `store_languages` → prune to two observations. Query: validate → SQL over `checkout_languages` joined to the current observation and present checkouts → items.

## 5. Data and State Management

The current observation of a checkout is the one with the highest `observation_id`; pruning deletes all but the two highest after each insert. The filter joins `checkout_languages` to the current observation (`observation_id = (SELECT MAX(...) WHERE checkout_id = c.checkout_id)`) and to `checkouts` with `state = 'active'`. A project's `languages` in a search item is the sorted union of labels from its present checkouts' current observations. A run with at least one failed detection is stored as partial; `store_run` receives that through the run's warnings, so the rule that absence is only inferred from a complete run still holds.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Detection raises | Failed observation, scan continues, run partial | Fix and rescan |
| Unreadable directory / bound | Partial observation | Raise limits or accept lower bounds |
| Crash mid-run | Earlier candidates committed, later ones keep older observations | Rescan |
| Bad filter value | `INVALID_INPUT` | Caller corrects |

## 7. Security and Privacy

Trust boundary as in the contract. Walk behavior is unchanged (no symlink follow, no file opened). The failed reason is a fixed code, never the exception message. Languages are machine-local. No material privacy impact beyond the existing index.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Integrity | At most two observations; a failed one has no rows | Pruning and insert in one transaction | Persistence tests |
| Honesty | Partial never implies absence | Positives only; no row removal | Partial tests |
| Read-only queries | No filesystem access | Queries read the index only | Test that changes files after the scan |
| Determinism | Stable ordering | Sorted items and labels | Ordering tests |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in both spec files.

### Test Strategy
Persistence tests against a real temporary SQLite file (migration, retention, rollback of a failed candidate); scan tests with injected `discover` and `detect`; contract tests through `queries` and the MCP snapshot (`tests/snapshots/mcp_tools.json`); unit tests for validation.

### Testability
`detect` and `discover` are injectable; the clock is injectable.

### Verification Evidence
`python -m pytest`, `python scripts/verify_workflows.py`; skips are reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Migration and store, then scan enrichment and isolation, then the filter, then details, then the MCP declaration and snapshot.

### Migration and Rollout
Additive migration on open. Existing checkouts read `not_observed` until the next scan.

### Documentation and Operations
Update the tool descriptions, `README.md` if it lists tool parameters, and `knowledge/log.md`.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/language-observations-in-index.md`; see `adr.md`.

## 12. Risks, Trade-offs, and Open Questions

### Risks
Detection before the lock means a lock failure wastes the walk; accepted because the walk is read-only.

### Trade-offs
Rows per language cost a join but make the filter indexed. Two observations per checkout cost storage but keep "what changed".

### Open Questions
None.

## 13. Traceability

Proposal, specs, and contract share the change ID `be-language-query`; requirement package `docs/requirements/language-detection/`.

## 14. Design Readiness Review

- [x] Requirements are traced to design elements and checks.
- [x] Boundaries, failure handling, and the trust boundary are stated.
- [x] The architecture decision checkpoint is answered.
- [x] Risks and trade-offs are visible.

**Status:** Draft
