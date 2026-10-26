---
type: Architecture
title: "Local Storage: Concurrency, Diagnostics, Testing, and Acceptance"
description: Locking and concurrent operation, logging, test strategy, sequence, decisions, and acceptance.
tags: [sqlite, storage, index]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/local-storage.md
    title: Local Storage
---

# Local Storage: Concurrency, Diagnostics, Testing, and Acceptance

*Sections 19–25 of [Local Storage](/architecture/local-storage.md).*

## 19. Concurrency and Operational Safety

### 19.1 Readers and Writers

The expected workload consists of frequent reads from MCP queries and occasional index updates.

The design should optimize for concurrent reads while maintaining correct writes.

### 19.2 Concurrent Refreshes

The application must define how simultaneous refresh requests are handled.

The initial recommendation is to serialize conflicting index refreshes within a database instance and reject or defer overlapping operations according to a documented policy.

### 19.3 Multiple Processes

SQLite may be accessed by multiple local processes, but the implementation must not assume that in-process locks coordinate all instances.

Database locking, transaction boundaries, and scan-run coordination must remain correct across multiple processes using the same database.

### 19.4 Read-Only Query Operations

Query tools must not update scan timestamps, observation records, or cache state merely because they were called, unless the operation's documented semantics explicitly require such an effect.

A read-only query should remain a read-only database operation.

### 19.5 Shutdown

The application must close database connections and release locks during orderly shutdown.

An interrupted process must not leave a partially committed project update or a scan run falsely marked as completed.

---

## 20. Logging and Diagnostics

Operational logs should record:

- Database initialization and migration outcomes.
- Scan-run lifecycle.
- Transaction failures.
- Lock contention.
- Integrity check outcomes.
- Backup and recovery results.
- Query failures.
- Sync and remote-provider failures in later phases.

Logs should not contain:

- API tokens.
- Secret configuration values.
- Full repository file contents.
- Unnecessary absolute paths.
- Sensitive project metadata unrelated to the diagnostic event.

Logs are not the authoritative source for scan history. The database's structured scan records should provide the machine-readable operational state required by MCP tools.

---

## 21. Testing Strategy

### 21.1 Storage Unit Tests

Test:

- Entity persistence and retrieval.
- Uniqueness constraints.
- Foreign-key behaviour.
- Observation status handling.
- Evidence associations.
- Relationship persistence.
- Transaction rollback.
- Timestamp serialization.
- Identifier stability.

### 21.2 Repository and Scanner Integration Tests

Verify:

- A complete scan produces consistent database records.
- Repeated scans do not create duplicate entities.
- Modified files invalidate affected observations.
- Deleted files invalidate previous positive evidence.
- Incomplete scans do not falsely confirm absence.
- Detector failures are isolated.
- A failed project update does not corrupt other committed project records.

### 21.3 Migration Tests

Verify fresh installation, sequential upgrades, failure recovery, and preservation of existing data.

### 21.4 Concurrency Tests

Test multiple readers, overlapping refresh requests, busy database conditions, and concurrent application instances where supported.

### 21.5 Recovery Tests

Test consistent backups, restore, rebuild, corruption reporting, and the preservation of non-reconstructible state.

### 21.6 Privacy Tests

Verify that:

- Local paths are not included in shared export records.
- Remote credentials are never persisted as ordinary metadata.
- Secret-bearing URLs are sanitized.
- Generic serializers cannot export unapproved fields.
- Error logs do not leak sensitive values.

---

## 22. Implementation Sequence

The recommended implementation order is:

1. Define the initial schema and migration framework.
2. Implement database configuration and connection lifecycle.
3. Add entity and repository persistence.
4. Add observations and evidence references.
5. Add scan-run and per-project result persistence.
6. Add incremental scanning fingerprints and inventory.
7. Add relationship storage.
8. Implement transactional project-level updates.
9. Implement query repositories for the MCP application services.
10. Add backup and recovery procedures.
11. Add concurrency, migration, and privacy tests.
12. Validate query and scan performance.
13. Introduce shared-registry synchronization state in Phase 2.
14. Introduce remote discovery state in Phase 3.

The Phase 1 schema should avoid premature complexity, but it must preserve the identity, provenance, and ownership distinctions required by later phases.

---

## 23. Decisions Required Before Implementation

| ID | Decision | Recommendation |
|---|---|---|
| LS-001 | Default database directory | Per-user application-data directory |
| LS-002 | SQLite journal mode | WAL, subject to platform testing |
| LS-003 | Connection lifecycle | Explicitly managed, operation-scoped connections or sessions |
| LS-004 | Migration framework | Versioned migrations with transactional safeguards |
| LS-005 | Observation history | Retain enough history for provenance and recovery; define retention limits |
| LS-006 | Resolved project projection | Start with the simplest design that meets query benchmarks |
| LS-007 | File fingerprint algorithm | Use a documented content fingerprint strategy |
| LS-008 | Scan transaction boundary | Commit consistent project-level updates |
| LS-009 | Concurrent refresh policy | Serialize conflicting refreshes |
| LS-010 | Backup mechanism | SQLite-supported consistent backup |
| LS-011 | Rebuild behaviour | Explicitly distinguish rebuild from restore |
| LS-012 | Phase 2 sync state | Separate local synchronization records from shared field ownership |
| LS-013 | Phase 3 remote state | Store provider observations separately from local checkout state |
| LS-014 | Retention policy | Set after estimating realistic scan and evidence volume |

These decisions should be resolved or explicitly accepted as implementation defaults before the corresponding code is written.

---

## 24. Acceptance Criteria

The local-storage implementation is ready for Phase 1 integration when:

1. SQLite initializes at a configured, platform-appropriate location.
2. Schema migrations are versioned, tested, and recoverable.
3. Project, repository, checkout, observation, evidence, relationship, and scan records are stored consistently.
4. Stable identities survive ordinary rescans.
5. Machine-local checkout state remains separate from shareable metadata.
6. Evidence and observation status remain traceable.
7. Incremental scanning can determine when cached detector results require revalidation.
8. Failed scans cannot silently mark incomplete observations as current.
9. Project-level transactions preserve consistent index state.
10. Concurrent reads and controlled writes behave predictably.
11. Database backup and recovery are documented and tested.
12. Query performance is validated against representative project counts.
13. Secrets and unnecessary local paths are not exposed through shared interfaces.
14. The schema supports later synchronization and remote discovery without conflating source ownership.
15. The index can be rebuilt without modifying project-owned files or profiles.

## 25. Governing Principle

SQLite is Vyasa's local persistence layer for generated intelligence and operational state.

It must preserve the distinction between logical projects, repositories, local checkouts, source observations, and resolved query results.

**Store what Vyasa knows, preserve why it knows it, and never let the local index silently become the owner of the projects it describes.**

---

## Proposed resolutions

These are drafts, not approvals.

| Decision | Proposed in |
|---|---|
| LS-001 to LS-011 location, journal mode, connections, migrations, transactions, backup, rebuild | [Local-First SQLite Index](/decisions/local-first-sqlite-index.md) |
| Run status vocabulary | [Unified Run Status Vocabulary](/decisions/unified-run-status-vocabulary.md) |
