---
type: Decision
title: "Local-First SQLite Index"
description: The index is one SQLite file in a per-user directory, written by one writer in per-project transactions and read through read-only connections.
tags: [adr, sqlite, storage]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: ls
    resource: /architecture/local-storage.md
    title: Local Storage
  - id: tech
    resource: /technologies/sqlite.md
    title: SQLite for the Local Index
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Vyasa needs a durable, queryable store that works offline, survives crashes, and can be read by a server process while a scan writes.

# Decision

Use SQLite in WAL mode. The file lives in a per-user data directory outside every scanned repository, with user-only permissions. One writer at a time holds a lock; each project commits in its own transaction; query paths open the file read-only. Migrations are forward-only and ordered.

# Alternatives considered

- **Plain files (JSON or YAML).** No atomic multi-record writes and no queries without loading everything.
- **Embedded key-value store.** Fast, but no relational queries or constraints.
- **A database server.** Needs infrastructure and breaks local-first operation.

# Consequences

- Only one writer at a time; a second refresh is refused rather than queued.
- The file must be on a local disk.
- Schema changes need migrations and a pre-migration backup.
- Queries are cheap and need no scan.

# Related

- [Local Storage](/architecture/local-storage.md)
- [Storage Views](/architecture/views/storage-views.md)
