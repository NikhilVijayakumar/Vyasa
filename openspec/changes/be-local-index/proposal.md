# Change Proposal: be-local-index

## Why

Discovery results vanish when the process ends, so nothing can be queried, compared between scans, or shown as missing. Vyasa needs a local SQLite index that keeps discovered projects across restarts, updates them on rescan without duplicates, marks vanished ones instead of erasing them, and refuses overlapping writers.

## What Changes

- **local-index**: a new capability. A per-user SQLite database with forward-only migrations, a project and checkout record per discovered repository, a scan-run history, a single-writer lock, and a freshness state.

## 1. Problem and Motivation

### Current Situation

`discover_repositories` returns a `DiscoveryRun` in memory (`src/vyasa/domain/discovery.py`). Configuration already resolves the per-user data directory and `VYASA_HOME` (`data_directory`). Nothing is stored; there is no `sqlite3` code in `src/`.

### Problem

Without a store there is no restart survival (FR-007 S1), no way to tell a changed project from a new one (S2, S3), no missing state (S4), no migration path (S5), and no protection against two refreshes writing at once (FR-008 S6). Every later phase-1 feature (identity, profile, queries, MCP) reads the index.

### Evidence

- Verified: no database code exists; `data_directory()` exists; `DiscoveryRun` carries absolute local paths and a run status in the shared vocabulary.
- Verified: requirement package `docs/requirements/local-index/` is reviewed; the owner confirmed Q4, Q6, Q7, Q13, Q15 on 2026-10-27.
- Assumption: a project can be matched across rescans by its checkout path until the identity change adds stronger evidence.

## 2. Desired Outcome

### Goals

- [ ] Persist discovered repositories as projects with checkouts, in one SQLite file.
- [ ] Make a repeated scan update, not duplicate.
- [ ] Mark vanished or unreadable projects `missing` or `inaccessible` and keep their history.
- [ ] Apply migrations forward-only, backing up first, and refuse a newer schema.
- [ ] Allow one writer; a second gets `OPERATION_IN_PROGRESS`.
- [ ] Report index freshness: `current`, `stale`, `partial`, `unknown`.

### Team Focus

Judged on the data model and its invariants, failure modes (crash mid-scan, locked database, newer schema), migration impact, and the persistence layer that owns each behaviour (real SQLite file, no mocks).

### Success Criteria

- [ ] Restart (new connection) returns the same projects.
- [ ] Scanning the same tree twice yields the same project count and IDs.
- [ ] A fault raised while storing project N leaves projects 1..N-1 committed and the run `interrupted`.
- [ ] A second process refreshing at the same time gets `OPERATION_IN_PROGRESS`.
- [ ] Opening a database whose `user_version` is higher than the code's fails with a controlled error and changes nothing.
- [ ] The whole suite passes with sockets blocked.

## 3. Scope

### In Scope

- Database location, permissions, pragmas (WAL, foreign keys, busy timeout).
- Migration runner and migration `0001`.
- Tables: `projects`, `checkouts`, `scan_runs`, `index_lock`.
- Storing a `DiscoveryRun` per project transaction; missing and inaccessible states.
- Interrupted-run recovery and freshness.
- Read-only connection helper for later query code.

### Out of Scope

- Stable project identity, remote matching, aliases, duplicates (next change, `be-identity-create-and-rescan`).
- Observations, evidence, file inventory, detector result reuse (SE-010), composition counts storage. Added with the detectors that produce them.
- Corruption check, `.corrupt` copy, rebuild command (Q10); retention and archival; benchmark corpus (Q13).
- MCP tools, CLI commands, Sheets, remote providers.

### Constraints

Standard library `sqlite3` only; no ORM. Absolute paths stay in local tables (data ownership). Nothing is deleted because one scan did not see it. Python 3.12+.

## 4. Stakeholders and Impact

- **Primary stakeholders:** the owner; coding agents that will query the index.
- **Affected components or capabilities:** new `vyasa.adapters.sqlite` and `vyasa.application.indexing`; reads `vyasa.domain.discovery`. Discovery itself is unchanged.
- **Dependencies:** `be-discover-one-root`, `be-git-remote`, `be-workspace-config` (all merged).
- **Compatibility considerations:** first schema version; later changes add migrations.

## 5. Proposed Direction

SQLite file `index.sqlite3` in the data directory, WAL, foreign keys on. Numbered SQL migrations tracked in `PRAGMA user_version`, each in one transaction, with a backup-API copy before any schema change. A `store_run` operation takes the lock, writes a `scan_runs` row as `running`, then upserts each project in its own transaction, marks absent checkouts, and finishes the run. Matching is by canonical checkout path in this change. Considered: JSON files (no atomic multi-record writes); an ORM (a dependency for little gain).

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Create and migrate the database | Controlled, recoverable open | Must |
| REQ-002 | Persist and rescan projects | Restart-safe, no duplicates | Must |
| REQ-003 | Missing and inaccessible states | History kept | Must |
| REQ-004 | Run lifecycle and single writer | Interrupted visible; second refresh refused | Must |
| REQ-005 | Freshness | current, stale, partial, unknown | Should |

## 7. Risks and Open Questions

### Risks

| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Path-based matching duplicates a moved project | Duplicate rows until identity lands | Documented; identity change replaces matching and merges via aliases |
| Table shape blocks identity or observations | Rework | `project_id` is opaque text; later tables reference it; migrations are additive |
| Database on a network drive | WAL fails | Documented limitation; warn when the path looks networked is deferred |
| Stale lock after a crash | Refreshes blocked | Heartbeat expiry (see design) |

### Assumptions

- A checkout path is unique per machine.
- 24 hours is the default freshness window (Q15), configurable later.

### Open Questions

- [ ] Whether the data directory warning for network filesystems belongs here or with the doctor/status work.

## 8. Acceptance Summary

- [ ] Every spec scenario has a test against a real temporary database file.
- [ ] `python -m pytest`, `verify_workflows.py`, `verify_knowledge.py` pass.
- [ ] No absolute path leaves the local tables; no credential stored (remote only as the identity already produced).

## 9. Traceability

- **OpenSpec Change ID:** `be-local-index`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-local-index`
- **Requirement package:** `docs/requirements/local-index/requirement.md`
- **Knowledge references:**
  - `knowledge/architecture/local-storage.md` — layout, pragmas, transactions, migrations, locking
  - `knowledge/decisions/local-first-sqlite-index.md` — one file, one writer, per-project transactions
  - `knowledge/decisions/partial-results-never-imply-absence.md` — a partial scan never marks projects gone
  - `knowledge/decisions/unified-run-status-vocabulary.md` — run status values
  - `knowledge/concepts/freshness-and-staleness.md` — freshness terms
  - `knowledge/decisions/index-lifecycle-and-single-writer.md` — new: states, lock, recovery (created with this change)
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/repository-discovery`, `openspec/specs/git-remote`, `openspec/specs/workspace-configuration`
- **Related ADRs:** `knowledge/decisions/index-lifecycle-and-single-writer.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved, or explicitly recorded.
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
