# Implementation Tasks: be-local-index

- **OpenSpec Change ID:** `be-local-index`
- **Status:** Planned
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

> Test-first per slice (Red, Green, Refactor), each against a real temporary SQLite file.

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [ ] 1.3 Confirm branch `feature/be-local-index`.

## 2. Prerequisite: domain rules

**Traceability:** Requirement: Freshness is reported · Knowledge: `knowledge/decisions/index-lifecycle-and-single-writer.md`

- [ ] 2.1 `vyasa.domain.index`: state and status constants, `IndexStoreError` with codes, `freshness`.
- [ ] 2.2 Tests: freshness table with a fixed clock.

## 3. Slice: open and migrate

**Traceability:** Requirements: The database is created safely; Migrations are forward-only

- [ ] 3.1 `index_path`, `open_index`, pragmas, permissions, migration runner, backup, `0001_initial.sql`.
- [ ] 3.2 Tests: first open, POSIX modes (skipped and reported on Windows), pragmas, pending migration with backup, raising migration rolls back, newer schema leaves the file byte-identical, up to date makes no backup.

## 4. Slice: store and rescan projects

**Traceability:** Requirements: Discovered projects are stored; Rescans do not duplicate

- [ ] 4.1 `store_run` for new and existing checkouts; remote stored credential-free.
- [ ] 4.2 Tests: new project, restart, changed project keeps its ID, no raw URL in any column, same tree twice, shuffled order.

## 5. Slice: missing and inaccessible

**Traceability:** Requirement: A vanished project is marked, not erased

- [ ] 5.1 Mark absent checkouts under the same root on a complete run; mark reported inaccessible paths; restore on reappearance.
- [ ] 5.2 Tests: removed, unreadable, partial and failed runs change nothing, reappears, other root untouched.

## 6. Slice: run lifecycle and single writer

**Traceability:** Requirements: Runs have a visible lifecycle; One writer at a time

- [ ] 6.1 `scan_runs` rows, `index_lock` acquire, heartbeat, release, dead-lock takeover, `interrupted` recovery.
- [ ] 6.2 Tests: completed run row, fault injection at project N (1..N-1 committed), previous data kept, second connection refused, two-process refusal, release then reacquire, dead writer recovery with a fixed clock.

## 7. Slice: read-only access and offline

**Traceability:** Requirements: Freshness is reported; The index works offline

- [ ] 7.1 `open_index(read_only=True)`, `list_projects`.
- [ ] 7.2 Tests: read-only changes no row; whole suite passes with sockets blocked (fixture).

## 8. Final Verification

- [ ] 8.1 `python -m pytest`
- [ ] 8.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [ ] 8.3 `openspec validate be-local-index`
- [ ] 8.4 Each spec scenario has a test; skips and unrun checks are reported.
- [ ] 8.5 Store a real discovery run of the owner's workspace into a scratch database; rescan; confirm no duplicates.
- [ ] 8.6 Review the diff for scope and the contract (no raw remote, no path outside local tables, no deletes).

## 9. Documentation and Handover

- [ ] 9.1 Update the knowledge decision if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 9.2 Mark the decision concept accepted when the owner accepts it.

## 10. Review, Merge, and Archive

- [ ] 10.1 Pull request with the change ID.
- [ ] 10.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 10.3 Archive the change.
