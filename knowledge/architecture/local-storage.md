---
type: Architecture
title: "Vyasa (व्यास) — Local Storage"
description: How Vyasa persists its index, configuration, and scan history locally in SQLite.
tags: [sqlite, storage, index]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
---
# Vyasa (व्यास) — Local Storage

Related architecture:

- [system-architecture](/architecture/system-architecture.md)
- [data-model](/architecture/data-model.md)
- [scanning-and-evidence](/architecture/scanning-and-evidence.md)
- [mcp-interface](/architecture/mcp-interface.md)

## Summary

This document defines how Vyasa persists and retrieves its local workspace intelligence.

## Parts

This concept is split into parts so each can be read on its own. Section numbers in the table are those of the original document, so references such as "§9.11" resolve to the part that contains them.

| Part | Sections | What it answers |
|---|---|---|
| [Storage Principles and Database Location](local-storage/principles-and-location.md) | §1–4 | Storage principles and responsibilities, and where and how the database is created. |
| [Logical Storage Model](local-storage/logical-model.md) | §5 | The logical groups of stored data and how they relate. |
| [Proposed Tables: Core](local-storage/tables-core.md) | §6.1–6.7 | Tables for migrations, projects, repositories, associations, checkouts, observations, and evidence. |
| [Proposed Tables: Relationships, Runs, and Inventory](local-storage/tables-operations.md) | §6.8–6.13 | Tables for relationships, scan runs and results, detector runs, file inventory, and the resolved index. |
| [Data Types, SQLite Configuration, and Transactions](local-storage/types-config-transactions.md) | §7–9 | Serialization, journal mode and pragmas, connection use, and transaction boundaries. |
| [Incremental State, Identity, and Local-Only Data](local-storage/incremental-identity-sharing.md) | §10–12 | What incremental scanning stores, deduplication, and the line between local and shareable data. |
| [Phase 2 and 3 Storage and Retention](local-storage/phase-tables-retention.md) | §13–15 | Registry and remote provider state, and retention and cleanup. |
| [Backup, Migrations, and Query Performance](local-storage/backup-migrations-performance.md) | §16–18 | Consistent backup and recovery, schema migrations, and indexing for queries. |
| [Concurrency, Diagnostics, Testing, and Acceptance](local-storage/operations-testing-acceptance.md) | §19–25 | Locking and concurrent operation, logging, test strategy, sequence, decisions, and acceptance. |
