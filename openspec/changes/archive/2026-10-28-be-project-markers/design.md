# Design: be-project-markers

## 1. Overview

### Purpose
Detect standard project markers from the scan's single walk, store them on the checkout observation, and expose them through the existing read-only queries.

### Scope
The walk adapter, a pure detector with versioned rules, a migration, storage, query changes, and the MCP declaration.

### Design Principles
One walk. Names only. Reuse the observation and the query patterns of the language and composition changes. Derive absence from completeness. Partial and not assessed are results.

## 2. Context and Constraints

### Current State
`walk_checkout` returns base file names and a stop reason; `scan_checkout` classifies them into counts and languages; `projects._store_languages` inserts the observation with its language rows and counts and prunes to two; `search_projects` builds fixed SQL clauses joined to the current observation (`MAX(observation_id)`), and `get_project` reads per-checkout objects.

### Constraints
- Technical constraints: Python 3.12+, standard library only (`fnmatch`), SQLite.
- Security and privacy constraints: names only; no absolute path stored or returned; values bound as parameters.
- Performance and reliability constraints: no extra walk; only matching paths are kept.
- Compatibility and migration constraints: additive; existing behavior kept.
- Operational constraints: single-writer lock; queries use a read-only connection.

### Existing Decisions and Conventions
Checkout walk observation, language observations in the index, partial results never imply absence, MCP omits local paths by default.

### Knowledge References
- `knowledge/decisions/project-marker-observations.md` — rules, states, evidence.
- `knowledge/decisions/checkout-walk-observation.md` — one walk and observation.
- `knowledge/decisions/partial-results-never-imply-absence.md` — partial semantics.
- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.5–9.9.

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| Markers from names and directories | `markers_of` over relative paths | Unit tests on path lists, no filesystem |
| Location rules, tests, OpenSpec | rule groups with a root-only flag | Unit tests |
| Three states | derived on read from `markers_version`, status, rows | Persistence and contract tests |
| Evidence relative and capped | cap in `markers_of`; paths from the walk | Unit and persistence tests |
| Stored on the observation | `_store_markers` in the same transaction | Persistence tests on a real database file |
| Older and failed not assessed | nullable `markers_version` | Migration and persistence tests |
| Rules are validated data | `load_marker_rules` | Unit tests on temp JSON |
| Walk reports paths | `WalkResult.files`, `.directories` | Adapter tests on real temp trees |
| Search and details | clauses and `projects.checkout_markers` | Contract tests and the MCP snapshot |

## 4. Architecture and Design

### Architectural Approach
The walk collects relative POSIX paths of files and of directories (found, including those not entered at the depth limit). `scan_checkout` passes them to the pure `markers_of(files, directories, rules)`, which returns a `MarkerReport`. `scan_workspace` carries the report on the `LanguageOutcome`; `_store_languages` inserts the rows with the observation and the rules version.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.adapters.filesystem.checkout_walk` | also returns `files` and `directories` | stdlib |
| `vyasa.domain.markers` | `MarkerRules`, `MarkerHit`, `MarkerReport`, `markers_of`, marker names | stdlib |
| `vyasa.application.scanning.markers` | `load_marker_rules`, `default_marker_rules` | domain |
| `vyasa/data/markers.json` | versioned rules | none |
| `vyasa.application.scanning.checkout_scan` | passes paths to `markers_of` when rules are given | domain, adapter |
| `vyasa.domain.languages` | `CheckoutScan.markers`; `LanguageOutcome.markers` | domain |
| `vyasa.adapters.sqlite.projects` | `_store_markers`, `checkout_markers` read model, filter helpers | sqlite |
| `vyasa/adapters/sqlite/migrations/0008_project_markers.sql` | column, table, index | none |
| `vyasa.application.query`, `vyasa.adapters.mcp.server` | parameters, validation, details, descriptions | adapters |

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Scan: `scan_checkout` with default rules per eligible candidate (failure becomes a failed outcome) → `upsert` + `_store_languages` inserts the observation, rows, counts, `markers_version`, and marker rows → prune to two. Query: validate → SQL over the current observation of active checkouts → items; details derive each state from the stored rows and the observation.

## 5. Data and State Management

`markers_of` matches in one pass: for each file path, its base name and parent directory; for each directory path, its base name. Root-only rules apply when the path has no parent. OpenSpec indicators look for the directory at the root and then for `config.yaml`/`config.yml`, `specs`, and `changes` as direct children of it (files for config, files or directories for the others). Agent files record scope `root` or the parent directory. Paths are sorted and truncated to 20 with `more` derived from `total`. The state of a marker with no row is `not_detected` when the current observation is complete and has a rules version, `unknown` when partial with a rules version, and the whole checkout is `not_assessed` when the version is null.

Filter SQL for `detected`: an EXISTS over active checkouts joined to the current observation and `checkout_markers` with `marker IN (...)`. For `not_detected`: for each requested marker, an EXISTS over active checkouts whose current observation has `status = 'complete'`, `markers_version IS NOT NULL`, and no row for that marker, combined with OR.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Detection raises | Failed observation, no version, no rows, run partial | Fix and rescan |
| Bound or unreadable directory | Partial observation; unmatched markers unknown | Raise limits or accept |
| Bad rules data | `MarkerRulesError` at load | Fix the data |
| Bad filter value | `INVALID_INPUT` | Caller corrects |

## 7. Security and Privacy

Trust boundary as in the contract. No file is opened. Paths come from the walk, which never follows links or leaves the checkout. No absolute path is stored. No material privacy impact beyond the existing index.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Honesty | Absence only from a complete assessment | State derived from status and version | Partial and not-assessed tests |
| Determinism | Same tree gives same result | Sorted paths and rules | Shuffled-order test |
| Cost | No extra walk | Same walk | Single-call test from the composition change still passes |
| Compatibility | Counts and languages unchanged | Additive walk fields | Existing tests unchanged |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in both spec files.

### Test Strategy
Unit tests for `markers_of` and the loader (no filesystem); adapter tests for the walk on real temp trees; persistence tests against a real temporary SQLite file; contract tests through `queries` and the MCP snapshot (`tests/snapshots/mcp_tools.json`).

### Testability
`discover`, `detect`, the clock, and limits are injectable; rules are plain data.

### Verification Evidence
`python -m pytest`, `python scripts/verify_workflows.py`; skips are reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Rules and detector, then the walk, then migration and storage, then the filter, then details, then the MCP declaration.

### Migration and Rollout
Additive migration on open; existing observations read `not_assessed` until the next scan.

### Documentation and Operations
Update the tool descriptions and `knowledge/log.md`.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/project-marker-observations.md`; see `adr.md`.

## 12. Risks, Trade-offs, and Open Questions

### Risks
Test name patterns can match non-test files; the matching rule is recorded.

### Trade-offs
Markers are stored only when detected, so absence costs nothing but must be derived with care.

### Open Questions
None.

## 13. Traceability

Proposal, specs, and contract share the change ID `be-project-markers`; requirement package `docs/requirements/project-markers/`.

## 14. Design Readiness Review

- [x] Requirements are traced to design elements and checks.
- [x] Boundaries, failure handling, and the trust boundary are stated.
- [x] The architecture decision checkpoint is answered.
- [x] Risks and trade-offs are visible.

**Status:** Draft
