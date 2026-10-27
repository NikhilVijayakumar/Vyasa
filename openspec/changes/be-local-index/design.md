# Design: be-local-index

## 1. Overview

### Purpose
Keep what discovery found in a local SQLite file that survives restarts, rescans, crashes, and schema changes.

### Scope
Opening and migrating the database, storing one discovery run, the single-writer lock, and freshness. Identity beyond the checkout path, observations, and queries are later changes.

### Design Principles
Standard library `sqlite3` and visible SQL. Nothing is deleted because a scan did not see it. Each project commits alone. Pure rules (states, freshness) live in the domain; SQL lives in the adapter.

## 2. Context and Constraints

### Current State
`discover_repositories` returns a `DiscoveryRun` of `Candidate`s. `data_directory()` resolves the per-user directory and `VYASA_HOME`. No storage code exists.

### Constraints
- Technical constraints: Python 3.12+, `sqlite3` only, no ORM.
- Security and privacy constraints: user-only permissions; bound parameters only; no credential or raw remote stored; local paths stay in local tables.
- Performance and reliability constraints: one transaction per project; thousands of projects must store in seconds; a crash leaves committed work intact.
- Compatibility and migration constraints: first schema; later changes are additive migrations.
- Operational constraints: tests pass on Windows and Linux; POSIX permission checks are skipped, and reported as skipped, on Windows.

### Existing Decisions and Conventions
Local-first SQLite index; partial results never imply absence; unified run-status vocabulary; deterministic extraction.

### Knowledge References
- `knowledge/decisions/local-first-sqlite-index.md`
- `knowledge/decisions/index-lifecycle-and-single-writer.md`
- `knowledge/decisions/partial-results-never-imply-absence.md`
- `knowledge/decisions/unified-run-status-vocabulary.md`
- `knowledge/architecture/local-storage/` (pragmas, transactions, migrations, concurrency)

## 3. Requirements and Traceability

| Requirement or Spec Reference | Design Element | Verification Approach |
|---|---|---|
| The database is created safely | `open_index`, `connect` | Temp directory; pragma queries; POSIX mode check |
| Migrations are forward-only | `migrate`, `migrations/*.sql` | Fixture database at an older version; raising migration; newer-version file hashed before and after |
| Discovered projects are stored | `store_run` | Real file, close and reopen |
| Rescans do not duplicate | `checkouts.path_key` unique | Store twice; shuffled order |
| A vanished project is marked, not erased | `_mark_absent` | Complete, partial, failed, other-root runs |
| Runs have a visible lifecycle | `scan_runs` rows | Fault injection at project N |
| One writer at a time | `index_lock`, `acquire` | Second connection and a multiprocessing test; expired heartbeat with a fixed clock |
| Freshness is reported | `domain.index.freshness` | Table test with a fixed clock |
| The index works offline | no network code | Whole suite with sockets blocked |

## 4. Architecture and Design

### Architectural Approach
`store_run` takes the lock (`BEGIN IMMEDIATE`, read the lock row, insert or take over if dead), inserts a `scan_runs` row as `running`, then for each eligible candidate runs one transaction: look up `path_key`; insert a project and checkout if absent; otherwise update the checkout fields and `last_seen_at`, restoring `active`. Candidates reported `inaccessible` mark a matching checkout `inaccessible`. After all projects, if the run is `complete`, checkouts stored under the same `root` and not seen in this run become `missing`. The run row is finished, the lock released. The heartbeat is refreshed after each project. Any exception marks the run `interrupted`, releases the lock, and re-raises.

`root` matching is by the exact root string stored with the checkout, so a run of root B never touches root A.

### Components and Responsibilities
| Component | Responsibility | Dependencies |
|---|---|---|
| `vyasa.domain.index` | state and status constants, `IndexStoreError` with codes, `freshness` | none |
| `vyasa.adapters.sqlite.database` | `index_path`, `open_index`, pragmas, permissions, `migrate`, backup | `sqlite3`, `os` |
| `vyasa.adapters.sqlite.migrations/0001_initial.sql` | first schema | none |
| `vyasa.adapters.sqlite.lock` | acquire, heartbeat, release, takeover | `sqlite3` |
| `vyasa.adapters.sqlite.projects` | upsert, mark absent, `list_projects` | `sqlite3` |
| `vyasa.application.indexing` | `store_run` orchestration | domain, adapter |

Dependencies point inward: the application layer uses the domain; adapters implement storage; the domain imports nothing.

### Interfaces and Contracts
See `api-contract.md`.

### Key Workflows
Open → migrate (backup first if pending) → store run (lock → run row → per-project upserts → mark absent → finish → release). Reads: open read-only → `list_projects`, `freshness`.

## 5. Data and State Management

Schema and invariants are in the contract. Migration files ship as package data and are read by name in numeric order. `user_version` is set inside the same transaction as the migration. Timestamps come from an injected clock. A project's state mirrors its single checkout's state in this change; the identity change may attach more checkouts per project and will define aggregate state then.

## 6. Error Handling and Resilience

| Failure Scenario | Expected Behavior | Recovery or Mitigation |
|---|---|---|
| Crash mid-run | Committed projects stay; run stays `running` | Next writer sees a dead lock and marks it `interrupted` |
| Exception storing project N | Run `interrupted`, lock released, error raised | Rerun |
| Second writer | `OPERATION_IN_PROGRESS`, no writes | Retry later |
| Newer schema | `INDEX_SCHEMA_TOO_NEW`, file untouched | Upgrade Vyasa |
| Migration raises | Rolled back, `INDEX_MIGRATION_FAILED`, backup remains | Fix and reopen |
| Database locked beyond 5 s | `INDEX_UNAVAILABLE` | Retry |

## 7. Security and Privacy

Trust boundary as in the contract. Parameterized SQL only. File mode 0600 and directory 0700 on POSIX. The `.bak` copy has the same mode. Absolute paths live only in this local database, which is never synchronized. No raw remote URL exists to store.

## 8. Quality Attributes

| Attribute | Requirement or Constraint | Design Response | Verification |
|---|---|---|---|
| Integrity | A failed scan never destroys valid data | Per-project transactions; no deletes; foreign keys | Fault injection test |
| Determinism | Same input, same rows | Unique `path_key`; sorted insertion order not relied on | Shuffled-order test |
| Concurrency | One writer, readers unblocked | WAL; lock row; read-only connections | Multiprocessing test |
| Offline | No network | No network imports | Sockets-blocked run |

## 9. Testing and Verification Strategy

### Behavioral Verification
One test per scenario in the spec, against a real temporary database file (no mocked SQLite).

### Test Strategy
Unit tests for `freshness` and state rules (pure). Persistence tests with `tmp_path` for migrations, storing, and states. A fixture database at version 0 (empty) and a hand-built "future" file for the newer-schema case. Fault injection through an injected failing hook on project N. A two-process test for the lock. A conftest fixture that monkeypatches `socket.socket` to raise.

### Testability
The clock, the owner, and the heartbeat age are injected. `store_run` takes a connection, so tests control the file.

### Verification Evidence
`pytest` output; skipped tests (POSIX permissions on Windows) reported.

## 10. Implementation and Migration Considerations

### Implementation Order
Domain rules, open and migrate, store a new project, rescan, absent states, run lifecycle and lock, freshness (vertical slices in `tasks.md`).

### Migration and Rollout
None for existing data. Nothing calls `store_run` yet; wiring it to a CLI or MCP refresh belongs to a later change.

### Documentation and Operations
Knowledge decision created; `knowledge/log.md` entry; README unchanged.

## 11. Architecture Decision Checkpoint

- **New ADR required:** Yes — `knowledge/decisions/index-lifecycle-and-single-writer.md`; see `adr.md`.
