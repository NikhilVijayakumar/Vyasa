---
type: Architecture
title: "Local Storage: Data Types, SQLite Configuration, and Transactions"
description: Serialization, journal mode and pragmas, connection use, and transaction boundaries.
tags: [sqlite, storage, index]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/local-storage.md
    title: Local Storage
---

# Local Storage: Data Types, SQLite Configuration, and Transactions

*Sections 7–9 of [Local Storage](/architecture/local-storage.md).*

## 7. Data Types and Serialization

### 7.1 Structured Values

Metadata may include strings, booleans, numbers, arrays, and structured objects.

The storage layer must preserve types rather than converting all values to strings.

For example, `tests_present: false` must not be indistinguishable from the string `"false"`.

### 7.2 JSON Columns

SQLite JSON storage may be used for bounded structured values where it simplifies extensibility.

However:

- Required fields should remain normal columns where practical.
- Important query filters should use indexed columns or supported indexed projections.
- Arbitrary JSON must not bypass validation.
- Schema changes must not depend on undocumented JSON shapes.
- Large source files must not be stored in JSON columns merely because JSON is available.

### 7.3 Timestamps

Persist timestamps in a consistent representation, preferably UTC ISO 8601 or a consistently defined numeric format.

The choice must be uniform across the schema and migrations.

User-facing timestamps may be converted to the client's local timezone.

### 7.4 Identifiers

Identifiers must be stable where their entity semantics require stability.

The implementation should use a consistent identifier format and avoid generating new project IDs on every scan.

Random scan-run IDs are acceptable because each run represents a distinct event.

---

## 8. SQLite Configuration

### 8.1 Journal Mode

WAL (Write-Ahead Logging) is the recommended initial journal mode, subject to platform and filesystem testing.

Benefits include improved reader/writer concurrency for local query workloads.

The implementation must document any limitations when the database is located on unsupported network filesystems or filesystems with unsuitable locking semantics.

### 8.2 Connection Management

Each operation must use a properly managed connection or session.

The implementation must define:

- Connection lifetime.
- Transaction ownership.
- Busy timeout.
- Error handling for locked databases.
- Shutdown behaviour.
- Whether connections are thread-local or operation-scoped.

Connections must not be shared unsafely across concurrent execution contexts.

### 8.3 Foreign Keys

Foreign-key enforcement should be enabled for every database connection that performs writes.

The schema should use foreign keys where they accurately represent ownership and lifecycle.

Deletion policies must be explicit. Cascading deletion must not accidentally remove useful scan history or evidence when a project is merely no longer discovered.

### 8.4 Durability

The SQLite durability settings must be selected deliberately.

The implementation should prefer safe, documented settings over aggressive performance settings that risk data loss. Any non-default durability choice must be justified and tested.

### 8.5 Database Locking

The implementation must handle temporary database contention with bounded waiting and actionable errors.

It must not retry indefinitely or silently discard writes when the database is locked.

---

## 9. Transaction Boundaries

### 9.1 Scan-Run Creation

Create a scan-run record before or at the start of scanning so that an interrupted run can be identified.

### 9.2 Project-Level Updates

A project-level update should commit a logically consistent group of changes, such as:

1. New observations.
2. Updated evidence references.
3. Invalidated superseded observations.
4. Resolved project summary.
5. Scan-item outcome.

These changes should be committed atomically where practical.

### 9.3 Partial Success

A failure for one project must not require rolling back unrelated projects that have already been successfully processed.

The scan-run summary should accurately report partial completion.

### 9.4 Failure Recovery

If a transaction fails:

- Roll back the affected transaction.
- Preserve previously committed valid state.
- Record the failure when the database remains writable.
- Avoid marking incomplete results as current.
- Allow a later scan to retry the affected work.

### 9.5 Index Consistency

A query must not observe a resolved summary that contradicts the corresponding committed observation state because an update was only partially applied.

Use transactional updates, explicit index generations, or another documented consistency mechanism.
