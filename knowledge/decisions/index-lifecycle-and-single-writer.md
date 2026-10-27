---
type: Decision
title: "Index Lifecycle States and Single Writer"
description: A vanished project is marked missing or inaccessible and never deleted; one writer holds a heartbeat lock; a run left running by a dead writer becomes interrupted; freshness is current, stale, partial, or unknown.
tags: [adr, sqlite, index, concurrency]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T23:30:00Z }
sources:
  - id: base
    resource: /decisions/local-first-sqlite-index.md
    title: Local-First SQLite Index
  - id: partial
    resource: /decisions/partial-results-never-imply-absence.md
    title: Partial Results Never Imply Absence
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

An index is trusted only if a failed scan, a second scan, or an unmounted drive cannot quietly destroy or contradict it. The base decision fixes one writer and per-project transactions but not what a vanished project becomes, how a dead writer is detected, or when the index counts as current.

# Decision

**Vanished projects.** A project whose checkout was not found by a complete scan becomes `missing`; one that exists but cannot be read becomes `inaccessible`. Its record, history, and observations stay. Nothing is deleted. A partial or failed scan changes no project to missing, because it did not see the whole tree. Seeing the checkout again restores `active`.

**Single writer.** A lock row holds an owner and a heartbeat time. A writer takes it at the start of a run and refreshes it while working. A second writer finds a live lock and is refused with `OPERATION_IN_PROGRESS`; it is not queued. A lock whose heartbeat is older than 60 seconds is dead and may be taken over. WAL mode and a 5 second busy timeout sit underneath.

**Interrupted runs.** A run is written as `running` first. When a writer takes over a dead lock, any run still `running` becomes `interrupted`. Work already committed per project stays.

**Freshness.** `current`: the latest run completed within 24 hours. `stale`: it completed earlier. `partial`: the latest run ended partial, failed, or interrupted. `unknown`: no run exists. Reading the index never scans and never changes this state.

# Alternatives considered

- **Delete projects that disappear.** Tidy, but an unmounted drive would erase evidence.
- **Queue overlapping refreshes.** Friendlier, but requests pile up behind a long scan.
- **Rely on SQLite locking alone.** Cannot tell a second refresh from a slow one, and leaves no record of who held it.
- **Mark missing after a partial scan.** Faster feedback, but contradicts the rule that partial results never imply absence.

# Consequences

- The index grows until retention archives old missing projects.
- A crashed writer blocks others for at most one heartbeat window.
- Every consumer must show `missing`, `inaccessible`, and freshness rather than hide them.
- The thresholds are starting values to revisit with real use.

# Related

- [Local-First SQLite Index](/decisions/local-first-sqlite-index.md)
- [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md)
- [Unified Run Status Vocabulary](/decisions/unified-run-status-vocabulary.md)
- [Freshness and Staleness](/concepts/freshness-and-staleness.md)
- [Local Storage](/architecture/local-storage.md)
