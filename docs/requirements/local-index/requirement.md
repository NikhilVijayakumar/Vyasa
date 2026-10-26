# Requirement: Local Index and Incremental Refresh

- **Package:** `docs/requirements/local-index/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1
- **Owns:** FR-007, FR-008, NFR-003
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-007-local-project-index.feature](features/fr-007-local-project-index.feature), [fr-008-incremental-scanning-and-refresh.feature](features/fr-008-incremental-scanning-and-refresh.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/architecture/local-storage.md` — SQLite layout, WAL, locking, migrations, backup
- `knowledge/architecture/data-model.md` — scan run, scan item result, observations, retention
- `knowledge/architecture/scanning-and-evidence.md` — incremental scanning and invalidation (§6, §10.4)
- `knowledge/concepts/evidence-and-provenance.md` — stale and inaccessible statuses
- `knowledge/architecture/c4-system-views.md` — Project Index Service and persistence adapter

## Intent

Vyasa keeps what it learned in a local SQLite index that survives restarts, crashes, schema changes, and failed scans, and refreshes it without redoing unchanged work. The index is the only thing queries read, so its integrity is the foundation of every answer.

## Scope

- **Included:**
  - Persistence, migrations, and integrity of the index.
  - Scan runs and their lifecycle, including interruption.
  - Incremental invalidation, deleted sources, and missing projects.
  - Single-writer concurrency and freshness states.
- **Excluded:**
  - Query semantics (project-query).
  - Registry and remote tables (later phases).
  - Encryption at rest.
- **Deferred:**
  - Resumable scans.
  - Automatic archival of long-missing projects.
  - Parallel scanning.

## Requirements

### FR-007 — Local Project Index (P1)

Vyasa MUST maintain a local index that supports project discovery and retrieval without requiring external services.

### FR-008 — Incremental Scanning and Refresh (P1)

Vyasa MUST support refreshing the local index while minimizing unnecessary work where practical.

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- Indexed projects survive restarts and become searchable when discovered (`fr-007`).
- Missing or inaccessible projects keep a state and their history (`fr-007` S4).
- Unchanged work is reused; interrupted and overlapping refreshes never corrupt state (`fr-008`).

## Constraints

- WAL journal, one writer, readers never blocked (local-storage).
- Per-project transactions; a failed project never rolls back others.
- Forward-only migrations; a newer schema than the code is refused.
- A failed scan never destroys previously valid data (DOR-009).

## Acceptance Expectations

- Phase 1 criteria 7, 8, 9 and 10 in `phase-acceptance-criteria.md`.
- Fault-injection test: a failure during project N leaves 1..N-1 committed and the run interrupted.
- A second process attempting a refresh gets OPERATION_IN_PROGRESS.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| SE-010 | Reuse a detector result when input fingerprints, detector version, and options are unchanged. | Q6 |
| NFD-005 | WAL with one writer lock; a second refresh returns OPERATION_IN_PROGRESS. | Q7 |
| SP-005 | Never auto-delete missing projects; mark them and let retention only archive. | Q4 |
| NFD-003/004 | Keep proposed p95 targets non-blocking until a benchmark validates them. | Q13 |
| freshness | Index is current for 24 hours after a completed run (configurable). | Q15 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-index-schema-and-migrations`: schema, user_version migrations, backup before migrating.
- `be-scan-run-lifecycle`: running, completed, interrupted, plus the writer lock.
- `be-incremental-reuse`: fingerprints, detector versions, deleted-file handling.
- `be-missing-and-freshness`: missing and inaccessible states and index freshness.
