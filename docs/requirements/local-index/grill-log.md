# Grill Log: Local Index and Incremental Refresh

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 2 | 0 |
| Behaviour | 5 | 2 |
| Data | 2 | 0 |
| Integration | 1 | 0 |
| Architecture | 1 | 0 |
| Acceptance | 2 | 1 |
| Ambiguity | 2 | 1 |

## Intent

**Q1. Why SQLite and not JSON files?**

- **Recommendation:** SQLite: transactional, embedded, queryable, and already chosen. Per-project transactions are what make partial scans safe.
- **Why:** Atomic writes across many small records are the hard part of a file store.
- **Status:** Settled
- **Feeds:** FR-007


## Scope

**Q2. What can be rebuilt and what cannot?**

- **Recommendation:** Observations, evidence, and inventory are rebuildable by rescanning. Scan history, identity events, and review decisions are durable. The schema separates the two so a rebuild never loses durable state.
- **Why:** Without the split a corrupt database costs human decisions.
- **Status:** Recommended
- **Feeds:** FR-007 S5

**Q3. Where does the database live?**

- **Recommendation:** The platform data directory (`~/.local/share/vyasa`, `~/Library/Application Support/Vyasa`, `%LOCALAPPDATA%\Vyasa`), overridable with `VYASA_HOME`. Directory mode 0700 and file mode 0600 on POSIX. Never inside a scanned repository.
- **Why:** A few lines of standard library avoid a dependency; permissions follow the security rules.
- **Status:** Settled
- **Feeds:** SEC-019


## Behaviour

**Q4. A project disappears. What happens (FR-007 S4)?**

- **Recommendation:** It becomes `missing` (path gone) or `inaccessible` (present but unreadable) after one scan. Observations and history stay. Nothing is deleted; retention can mark long-missing projects `archived`.
- **Why:** Deleting evidence because a drive is unmounted is the worst outcome of a failed scan.
- **Status:** Decision needed
- **Feeds:** FR-007 S4

**Q5. A manifest is deleted. What happens to its facts (FR-008 S4)?**

- **Recommendation:** The current resolved value becomes `not_detected`; the previous observation is kept as history. Nothing is silently dropped.
- **Why:** Example A in the ownership requirements says exactly this.
- **Status:** Settled
- **Feeds:** FR-008 S4

**Q6. When may a previous result be reused (SE-010)?**

- **Recommendation:** Per project and detector: the inputs are the detector's declared files with (relative path, size, mtime_ns), the detector version, and the detector options. All equal means reuse. A changed mtime with an equal content hash also reuses. A changed Git HEAD invalidates repository-wide detectors. A `--full` rescan bypasses reuse.
- **Why:** Matches the architecture rule that timestamps alone must not justify reuse when other evidence says otherwise.
- **Status:** Recommended
- **Feeds:** FR-008 S2, S3

**Q7. How do overlapping refreshes behave (NFD-005)?**

- **Recommendation:** One writer at a time through a lock row with owner and heartbeat, on top of WAL and a 5 s busy timeout. A second refresh returns `OPERATION_IN_PROGRESS` and is not queued. A lock whose heartbeat is older than twice the interval can be taken over, and the takeover is recorded.
- **Why:** Queued refreshes pile up; a clear refusal is simpler and safe.
- **Status:** Decision needed
- **Feeds:** FR-008 S6

**Q8. What does an interrupted scan leave behind?**

- **Recommendation:** A run row written first as `running`. At startup a `running` run whose lock is dead becomes `interrupted`, and index freshness is `partial` until a run completes. Committed per-project work stays.
- **Why:** Makes the failure visible instead of leaving an unfinished run that looks fine.
- **Status:** Recommended
- **Feeds:** FR-008 S5


## Data

**Q9. How do migrations work (FR-007 S5)?**

- **Recommendation:** Forward-only numbered SQL files applied in one transaction each, tracked in `PRAGMA user_version`. The database file is copied with the SQLite backup API before a schema change. A schema newer than the code is refused with a clear error and never downgraded.
- **Why:** A pre-migration copy turns a bad migration into a recoverable event.
- **Status:** Recommended
- **Feeds:** FR-007 S5

**Q10. How is corruption handled?**

- **Recommendation:** Foreign keys on, CHECK constraints for enums, and `quick_check` at startup only after a crash. On corruption report `INDEX_INCONSISTENT`, keep a `.corrupt` copy, and offer a rebuild that preserves durable tables where readable.
- **Why:** Detect early, preserve evidence, and make recovery a command.
- **Status:** Recommended
- **Feeds:** NFR-003


## Integration

**Q11. What about network drives?**

- **Recommendation:** Documented limitation with a best-effort warning when the database path looks like a network filesystem; WAL needs working shared memory and locks.
- **Why:** Already stated in local-storage; a warning costs little.
- **Status:** Settled
- **Feeds:** local-storage


## Architecture

**Q12. ORM or plain SQL?**

- **Recommendation:** The standard library `sqlite3` with a thin repository layer and SQL migration files. No ORM.
- **Why:** One dependency fewer and every query is visible and testable.
- **Status:** Recommended
- **Feeds:** NFR-027


## Acceptance

**Q13. How are the proposed performance targets validated (NFD-003/004)?**

- **Recommendation:** A seeded synthetic corpus generator for 10, 100, 500, and 1,000 projects in `tests/bench/`, recording p95 for lookup, search, context, and related queries. Targets stay non-blocking until measured and reviewed.
- **Why:** The requirements say proposed targets must be validated before they gate a release.
- **Status:** Decision needed
- **Feeds:** NFR-006, NFR-010

**Q14. How is crash safety proven?**

- **Recommendation:** Fault injection that raises while indexing project N of M; a multiprocessing test of two writers; a migration test from a committed fixture database of the previous version.
- **Why:** Each guarantee gets one test that would fail if it broke.
- **Status:** Recommended
- **Feeds:** FR-008 S5, S6


## Ambiguity

**Q15. What do current, stale, partial, and unknown mean?**

- **Recommendation:** `current`: last run completed within 24 hours (configurable). `stale`: older. `partial`: the last run was partial or interrupted. `unknown`: never scanned. Queries report this state and never scan.
- **Why:** The vocabulary exists in the MCP interface; this fixes the thresholds.
- **Status:** Decision needed
- **Feeds:** FR-007 S1

**Q16. What does 'works offline' cover?**

- **Recommendation:** Every phase 1 operation: scanning, queries, migrations, and status. A test blocks sockets and runs the whole suite.
- **Why:** Easy to promise, easy to break; the socket-blocking test keeps it true.
- **Status:** Recommended
- **Feeds:** FR-007 S6; NFR-011

## Decisions for you

None open. Q4, Q6, Q7, Q13 and Q15 were confirmed by the owner on 2026-10-27.
