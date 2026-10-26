# Diagrams: Local Index and Incremental Refresh

C4 vocabulary: `knowledge/architecture/c4-system-views.md`.

## How does an incremental refresh stay safe? (dynamic view)

```mermaid
sequenceDiagram
  autonumber
  participant Idx as Project Index Service
  participant Db as SQLite Persistence Adapter
  participant Det as Detector Registry
  Idx->>Db: acquire writer lock (owner, heartbeat)
  alt lock held by a live owner
    Db-->>Idx: busy
    Idx-->>Idx: return OPERATION_IN_PROGRESS
  else lock free or dead
    Idx->>Db: insert run (running)
    loop each project
      Idx->>Db: read prior fingerprints and detector versions
      alt inputs, version, and options unchanged
        Idx-->>Idx: reuse prior results
      else changed or new
        Idx->>Det: run affected detectors
        Det-->>Idx: observations or item error
        Idx->>Db: commit this project in one transaction
      end
    end
    Idx->>Db: close run (completed, partial) and release lock
  end
```

## What states can a scan run be in?

```mermaid
stateDiagram-v2
  [*] --> pending
  pending --> running
  running --> completed: all items inspected
  running --> partial: some items or roots failed
  running --> failed: nothing usable
  running --> cancelled: stopped by the user
  running --> interrupted: process stopped
  interrupted --> [*]
  cancelled --> [*]
  completed --> [*]
  partial --> [*]
  failed --> [*]
```
