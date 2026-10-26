# Diagrams: Workspace Discovery and Scan Reporting

C4 views for the whole system are in `knowledge/architecture/c4-system-views.md`. These two views answer
the questions specific to this package. Mermaid text; not rendered by any tool in this repository.

## What happens during one scan? (dynamic view)

```mermaid
sequenceDiagram
  autonumber
  actor Dev as Developer
  participant Idx as Project Index Service
  participant Cfg as Configuration Manager
  participant Disc as Workspace Discovery
  participant Insp as Repository Inspector
  participant Db as SQLite Persistence Adapter
  Dev->>Idx: request scan
  Idx->>Cfg: load and validate configuration
  alt no usable root
    Idx->>Db: record failed run (not_configured)
    Idx-->>Dev: not configured
  else at least one root usable
    Idx->>Db: record run as running
    loop each root, sorted
      Idx->>Disc: discover candidates (exclusions, depth, symlink policy)
      Disc-->>Idx: candidates with outcomes
    end
    loop each eligible candidate
      Idx->>Insp: inspect within limits
      Insp-->>Idx: inventory or item error
    end
    Idx->>Db: close run with status and counts
    Idx-->>Dev: report scope, counts, failures
  end
```

## How does a directory become a candidate outcome?

```mermaid
flowchart TD
  A[Directory found under a root] --> B{Excluded by pattern?}
  B -- yes --> X1[excluded]
  B -- no --> C{Symlink or outside roots?}
  C -- yes --> X2[skipped_by_policy]
  C -- no --> D{Readable?}
  D -- no --> X3[inaccessible]
  D -- yes --> E{Git root or supported marker?}
  E -- no --> X4[not_recognized]
  E -- yes --> F{Git metadata well formed?}
  F -- no --> X5[malformed]
  F -- yes --> G{Identity decidable?}
  G -- no --> X6[identity_unresolved]
  G -- yes --> X7[eligible]
```
