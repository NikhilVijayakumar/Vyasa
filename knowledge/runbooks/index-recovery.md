---
type: Runbook
title: "Index Recovery"
description: How to respond to an interrupted scan, a stuck writer lock, a failed migration, or a damaged database.
tags: [recovery, sqlite, migrations, locks]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: bk
    resource: /architecture/local-storage/backup-migrations-performance.md
    title: Backup, Migrations, and Query Performance
  - id: views
    resource: /architecture/views/storage-views.md
    title: Storage Views
---

# Symptoms and responses

| Symptom | Likely cause | Response |
|---|---|---|
| Index freshness is `partial`; the last run is `interrupted` | A scan ended unexpectedly | Run a scan. Committed projects stay valid; unchanged work is reused. |
| A refresh reports another operation in progress | A scan is running, or a writer died holding the lock | Wait for the run. If its heartbeat is stale and no process exists, the lock may be taken over; the takeover is recorded. |
| Startup refuses the database as newer than the code | The index was written by a newer version | Install the newer version. Do not edit the schema marker. |
| A migration failed | Unexpected data or an interrupted migration | Restore the pre-migration copy, then retry with the fixed version. |
| `INDEX_INCONSISTENT` or an integrity check fails | Damage or a bug | Keep a copy of the file, then restore a backup or rebuild. |

# Restore versus rebuild

*Restore* returns an earlier snapshot, including its older state. *Rebuild* recomputes generated data by rescanning the
repositories and loses nothing that exists in them. Human-managed data is recovered from the shared registry when
available. Always say which path was taken, and never replace a damaged database without keeping a copy.[^bk]

# After recovery

Run a full scan, confirm index status is `current`, and note the cause for follow-up.

# Related

- [Storage Views](/architecture/views/storage-views.md)
- [Local Storage](/architecture/local-storage.md)

[^bk]: Backup, Migrations, and Query Performance
