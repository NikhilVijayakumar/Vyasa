# Diagrams: Shared Registry and Cross-Device Visibility

C4 vocabulary: `knowledge/architecture/c4-system-views.md`.

## Who talks to the registry and what may cross? (context view)

```mermaid
C4Context
  title Registry synchronization boundary
  Person(dev, "Developer", "Runs sync, edits portfolio fields in the sheet")
  System(vyasa, "Vyasa on this device", "Local index, allowlist, conflict handling")
  System_Ext(sheets, "Google Sheets registry", "Approved summaries and portfolio fields")
  System(other, "Vyasa on another device", "Reads registry-only projects")
  Rel(dev, vyasa, "sync --dry-run, sync")
  Rel(vyasa, sheets, "Allowlisted fields out; portfolio fields in")
  Rel(other, sheets, "Same allowlist and rules")
```

## What happens in one sync run? (dynamic view)

```mermaid
sequenceDiagram
  autonumber
  actor Dev as Developer
  participant Sync as Registry sync
  participant Own as Ownership Policy
  participant Db as Project index
  participant Gs as Google Sheets
  Dev->>Sync: sync (or --dry-run)
  Sync->>Gs: read schema marker and headers
  alt required tab or column missing
    Sync-->>Dev: schema error, nothing written
  else schema valid
    Sync->>Db: read allowlisted fields and shared state
    Sync->>Gs: read rows
    Sync->>Own: compare per field by owner
    Own-->>Sync: writes, imports, conflicts
    opt not dry-run
      Sync->>Gs: batched upserts (backoff, bounded retries)
      Sync->>Db: import portfolio fields, record run
    end
    Sync-->>Dev: counts, conflicts, errors
  end
```
