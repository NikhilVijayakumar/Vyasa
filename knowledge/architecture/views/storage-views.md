---
type: Architecture
title: "Storage Views"
description: How the index database opens and migrates, how a scan writes safely, and how recovery chooses between restore and rebuild.
tags: [storage, sqlite, migrations, recovery, transactions]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: ls
    resource: /architecture/local-storage.md
    title: Local Storage
  - id: tx
    resource: /architecture/local-storage/types-config-transactions.md
    title: Data Types, SQLite Configuration, and Transactions
  - id: bk
    resource: /architecture/local-storage/backup-migrations-performance.md
    title: Backup, Migrations, and Query Performance
---

# Question

How does the index stay consistent when Vyasa starts, migrates, writes, crashes, or finds damage?

# Opening the database

```mermaid
stateDiagram-v2
  [*] --> Locating
  Locating --> Opening: data directory found or created with restricted permissions
  Opening --> CheckingVersion: connection configured (foreign keys, WAL, busy timeout)
  CheckingVersion --> Ready: schema current
  CheckingVersion --> Migrating: schema older and supported
  CheckingVersion --> Refused: schema newer than the code
  Migrating --> BackedUp: consistent backup taken first
  BackedUp --> Migrated: ordered migrations in transactions
  Migrated --> Ready: version recorded after success
  Migrating --> RecoveryNeeded: migration fails
  Opening --> RecoveryNeeded: integrity problem detected
  Ready --> [*]
  Refused --> [*]
  RecoveryNeeded --> [*]
```

A newer schema is refused rather than downgraded, and a failed migration leaves a recoverable copy.

# Writing one scan

```mermaid
sequenceDiagram
  autonumber
  participant Idx as Project Index Service
  participant Db as SQLite
  Idx->>Db: begin, insert scan run as running, commit
  loop each project
    Idx->>Db: begin
    Idx->>Db: write observations, evidence, identity mapping, item result
    alt success
      Idx->>Db: commit
    else failure
      Idx->>Db: rollback, then record item failure if still writable
    end
  end
  Idx->>Db: begin, close run with status and counts, commit
```

Each project commits on its own, so a failure never rolls back earlier projects and incomplete results are never marked current.

# Choosing recovery

```mermaid
flowchart TD
  P[Problem found] --> Q{Can the database still be read?}
  Q -- yes --> R{Is it only an old or failed migration?}
  R -- yes --> RS[Restore the pre-migration copy]
  R -- no --> RB[Rebuild generated data by rescanning]
  Q -- no --> KC[Keep a copy of the damaged file]
  KC --> RT{Is a consistent backup available?}
  RT -- yes --> RS2[Restore from the backup]
  RT -- no --> RB2[Rebuild generated data by rescanning]
  RS --> N[Tell the user what was restored]
  RS2 --> N
  RB --> N
  RB2 --> N
```

Restore returns an earlier state; rebuild recomputes generated data from the repositories. Human-managed shared data is
recovered from the shared registry when available. The user is told which path was taken; a damaged database is never
silently replaced.

# Related

- [Local Storage](/architecture/local-storage.md)
- [Data Model Views](/architecture/views/data-model-views.md)
