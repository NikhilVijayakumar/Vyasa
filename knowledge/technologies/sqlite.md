---
type: Technology
title: "SQLite for the Local Index"
description: What SQLite gives Vyasa and the settings and limits that matter: WAL, foreign keys, version markers, backup, read-only opens, and full-text search.
tags: [sqlite, wal, migrations, backup, fts5]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
stale_after: 2027-01-26T00:00:00Z
sources:
  - id: ls
    resource: /architecture/local-storage.md
    title: Local Storage
  - id: tx
    resource: /architecture/local-storage/types-config-transactions.md
    title: Data Types, SQLite Configuration, and Transactions
---

# Why SQLite

An embedded, transactional, single-file database that Python ships with. It needs no server, which suits a local-first
tool, and its transactions are what make per-project writes safe.[^ls]

# Settings that matter

| Concern | Practice |
|---|---|
| Concurrency | Write-ahead logging lets readers run while one writer writes. There is still only one writer at a time. |
| Referential integrity | Foreign keys are off by default for each connection; turn them on when opening. |
| Waiting | Set a busy timeout so a locked database waits briefly and then reports an error instead of hanging or failing at once. |
| Schema version | `PRAGMA user_version` stores one integer in the file header, which suits ordered migrations. |
| Backup | The online backup API copies a consistent snapshot while the database is in use. Copying the file alone is unsafe when WAL is active. |
| Query-only use | Open with a read-only URI (`mode=ro`) so a query path cannot write even by mistake. |
| Integrity | `PRAGMA quick_check` is cheap; run it after a crash or on request, not on every start. |
| Text search | FTS5 is a compile-time option that is common but not guaranteed; keep a plain `LIKE` fallback. |

# Limits

- WAL relies on shared memory and file locking and is not reliable on network filesystems. Keep the database on a local
  disk and warn when the path looks remote.
- Dates have no native type; store ISO 8601 text with an offset.
- Enumerations are not enforced unless a `CHECK` constraint says so.[^tx]

# Related

- [Local Storage](/architecture/local-storage.md)
- [Storage Views](/architecture/views/storage-views.md)

[^ls]: Local Storage
[^tx]: Data Types, SQLite Configuration, and Transactions
