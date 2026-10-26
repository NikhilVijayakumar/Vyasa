---
type: Architecture
title: "Local Storage: Storage Principles and Database Location"
description: Storage principles and responsibilities, and where and how the database is created.
tags: [sqlite, storage, index]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/local-storage.md
    title: Local Storage
---

# Local Storage: Storage Principles and Database Location

*Sections 1–4 of [Local Storage](/architecture/local-storage.md).*

## 1. Purpose

This document defines how Vyasa persists and retrieves its local workspace intelligence.

It specifies:

- SQLite database responsibilities and boundaries.
- Logical storage entities and table relationships.
- Persistence of project metadata, observations, evidence, and relationships.
- Scan history and incremental scanning state.
- Transaction and concurrency rules.
- Database migrations and compatibility.
- Backup, recovery, and corruption handling.
- Local-only information and privacy boundaries.
- Preparation for Google Sheets synchronization and remote repository discovery.

The storage layer must support deterministic scanning and fast MCP queries without making SQLite the authoritative owner of project-maintained information.

## 2. Storage Principles

### 2.1 Local-First

Phase 1 must operate without an external database or network service.

SQLite stores the local index and the operational state needed to maintain it.

### 2.2 Generated Index, Not Source of Truth

The local database contains generated observations, normalized metadata, resolved query records, and operational state.

It must not silently become the canonical owner of project purpose, documentation, or other project-maintained facts.

The ownership model defined in `data-ownership.md` determines which source is authoritative for each field.

### 2.3 Deterministic and Rebuildable

The index should be reconstructible from accessible repositories and supported external sources, subject to the configured scope and source availability.

A rebuild may not recover machine-local observations, historical scan records, or human-managed portfolio fields unless those are preserved separately.

Vyasa must not claim that every database field can be reconstructed from repository files alone.

### 2.4 Preserve Provenance

Stored facts must retain enough provenance to explain their origin.

Where applicable, records should identify:

- Source type.
- Source entity.
- Source location.
- Detector or provider.
- Observation time.
- Relevant revision or fingerprint.
- Status and freshness.

### 2.5 Atomic and Consistent Updates

A failed scan must not leave half-written records that appear to represent a completed observation.

Transactions should commit logically consistent updates, while allowing independent projects to succeed even if another project fails.

### 2.6 Explicit Separation of Local and Shared Data

Machine-specific state must remain local.

Google Sheets will become a shared registry in Phase 2. It must not receive local paths, database paths, local-only identifiers, credentials, or other machine-specific operational state.

---

## 3. Storage Responsibilities

The SQLite database is responsible for:

1. Maintaining stable local mappings to logical projects and repositories.
2. Storing metadata observations and their status.
3. Storing evidence references.
4. Maintaining resolved project and repository records for efficient queries.
5. Recording project relationships and dependency observations.
6. Recording scan runs and per-project outcomes.
7. Tracking incremental scanning fingerprints and detector versions.
8. Supporting index status, freshness evaluation, and diagnostics.
9. Providing consistent query access to the application and MCP layers.
10. Supporting schema migrations and safe recovery.

SQLite is not responsible for:

- Editing project documentation or canonical profiles.
- Executing repository code.
- Replacing the repository's own Git history.
- Storing full repository contents.
- Acting as a secret store.
- Becoming the shared cross-device registry.
- Automatically deleting projects because they are no longer visible locally.

---

## 4. Database Location and Configuration

### 4.1 Database Path

The database location must be configurable.

The default should use the operating system's appropriate per-user application-data directory, rather than placing the database inside an arbitrary project repository.

A proposed default layout is:

```text
<user-data-directory>/
└── vyasa/
    ├── vyasa.db
    ├── backups/
    └── logs/
```

The exact directory resolution must be implemented using a cross-platform library or a documented operating-system-specific policy.

The database must not be created in the current working directory by accident.

### 4.2 Configuration

Configuration should support:

- Database path.
- Workspace roots.
- Exclusion rules.
- Scanning options.
- Database busy timeout.
- Backup location and retention policy.
- Logging configuration.
- Enabled optional capabilities.

Configuration secrets must not be stored in the database unless a future, explicitly reviewed requirement establishes a secure and necessary use case.

### 4.3 Directory Permissions

Vyasa should create its application-data directory with appropriately restrictive permissions where supported.

The implementation must not assume that filesystem permissions behave identically across Linux, Windows, and macOS.
