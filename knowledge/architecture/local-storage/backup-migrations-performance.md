---
type: Architecture
title: "Local Storage: Backup, Migrations, and Query Performance"
description: Consistent backup and recovery, schema migrations, and indexing for queries.
tags: [sqlite, storage, index]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/local-storage.md
    title: Local Storage
---

# Local Storage: Backup, Migrations, and Query Performance

*Sections 16–18 of [Local Storage](/architecture/local-storage.md).*

## 16. Backup and Recovery

### 16.1 Backup Scope

A backup should include the SQLite database and any additional local state required for recovery.

The implementation must document whether configuration, logs, and any local auxiliary files are included.

Secrets should not be copied into backups unnecessarily.

### 16.2 Consistent Backups

When WAL mode is used, backups must account for WAL state.

Use a SQLite-supported backup mechanism or another tested method that produces a consistent database snapshot. Do not assume that copying only the main database file while the database is active is sufficient.

### 16.3 Recovery

Vyasa must:

- Detect database initialization and migration failures.
- Report corruption or integrity problems clearly.
- Preserve a recoverable copy before destructive repair where feasible.
- Avoid silently deleting a damaged database and rebuilding without informing the user.
- Provide a documented rebuild path for reconstructible generated data.
- Preserve shared human-managed data when it is available from the shared registry.

### 16.4 Rebuild Versus Restore

These operations have different meanings.

**Rebuild** reconstructs generated index data from available sources.

**Restore** recovers previously persisted state from a backup.

A rebuild may lose historical scan data, cached observations, or local associations that cannot be rediscovered. The CLI and documentation must not present rebuild as a lossless replacement for backup restoration.

---

## 17. Schema Migrations

### 17.1 Versioning

The database schema must have a monotonically increasing migration version.

Application startup must compare the database schema version with the version supported by the application.

### 17.2 Migration Rules

Migrations must:

- Be ordered and versioned.
- Be deterministic.
- Be tested against representative earlier schemas.
- Use transactions where supported and appropriate.
- Preserve existing records unless a documented migration intentionally changes them.
- Fail safely if required transformations cannot be completed.
- Record completion only after successful application.

### 17.3 Compatibility

The application must detect a database schema newer than the version it supports.

It must not attempt to downgrade or modify an unknown future schema automatically.

The error should explain that a compatible Vyasa version or an explicit migration procedure is required.

### 17.4 Migration Testing

Tests should cover:

- Fresh database initialization.
- Every supported migration path.
- Interrupted migration recovery.
- Constraint preservation.
- Data preservation.
- Migration failure.
- Compatibility with the application version.

---

## 18. Query Performance and Indexing

### 18.1 Query Requirements

The database should support efficient access by:

- Project ID.
- Repository ID.
- Normalized technology identifier.
- Programming language.
- Lifecycle and tracking status.
- Documentation and standards indicators.
- Observation status and freshness.
- Relationship endpoints and type.
- Scan run ID and outcome.

### 18.2 Index Selection

Add indexes based on actual query patterns.

Likely candidates include:

- Project primary key.
- Repository identity.
- Project-to-repository association keys.
- Observation entity and field keys.
- Current observation lookup keys.
- Relationship source, target, and type.
- Scan run timestamps and status.
- File inventory repository and relative path.

Avoid indexing every field indiscriminately, since additional indexes increase storage and write costs.

### 18.3 Text Search

If ordinary SQLite queries are insufficient for project search, SQLite FTS may be evaluated.

Text-search indexes must be rebuildable and must not replace structured metadata filters.

Search behaviour must remain deterministic and consistent with the MCP contract.

### 18.4 Performance Validation

Validate the storage implementation against representative workspace sizes, including the planned 10, 100, 500, and 1,000-project benchmarks.

The storage layer must meet the performance objectives in `non-functional-requirements.md` or document evidence-backed changes to those targets.
