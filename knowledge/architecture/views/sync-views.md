---
type: Architecture
title: "Synchronization Views"
description: The registry context, one synchronization run, and how a field conflict is decided.
tags: [sync, google-sheets, conflicts, sequence]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: sy
    resource: /architecture/synchronization.md
    title: Synchronization
  - id: wf
    resource: /architecture/synchronization/modes-and-workflow.md
    title: Synchronization Modes and Workflow
  - id: cf
    resource: /architecture/synchronization/conflicts-and-idempotency.md
    title: Conflicts, Upserts, and Idempotency
---

# Question

What crosses the registry boundary, in what order does a run proceed, and how is a difference between local and shared values decided?

# The registry boundary

```mermaid
C4Context
  title Registry synchronization boundary
  Person(dev, "Developer", "Runs synchronization; edits portfolio fields in the sheet")
  System(local, "Vyasa on this device", "Local index, ownership policy, export allowlist")
  System_Ext(sheet, "Google Sheets registry", "Project Registry, Documentation and Standards, Scan History")
  System(peer, "Vyasa on another device", "Same rules, own local index")
  Rel(dev, local, "Starts a run")
  Rel(local, sheet, "Allowlisted fields out; human-managed fields in")
  Rel(peer, sheet, "Same")
```

# One run

```mermaid
sequenceDiagram
  autonumber
  actor Dev as Developer
  participant Sync as Synchronizer
  participant Own as Ownership Policy
  participant Db as Local index
  participant Gs as Google Sheets
  Dev->>Sync: start run
  Sync->>Gs: validate schema and version marker
  alt schema unexpected
    Sync-->>Dev: schema error, no writes
  else schema valid
    Sync->>Db: read approved local fields
    Sync->>Gs: read registry rows
    Sync->>Own: plan changes per field
    Own-->>Sync: writes, imports, conflicts, skips
    Sync-->>Dev: plan (and stop here in read-only mode)
    Sync->>Gs: apply planned writes in batches
    opt ambiguous or critical updates
      Sync->>Gs: read back to verify
    end
    Sync->>Db: commit imports, conflicts, and run result
  end
  Sync-->>Dev: counts, conflicts, errors
```

# Deciding a difference

```mermaid
flowchart TD
  A[Local and shared values differ] --> B{Is project identity unambiguous?}
  B -- no --> X1[Stop writes for this project; report]
  B -- yes --> C{Who owns the field?}
  C -- human-managed in the sheet --> D[Import the shared value into the local cache]
  C -- scanner-owned --> E{Did the last scan complete successfully?}
  E -- no --> X2[Keep the shared value; do not clear it]
  E -- yes --> F{Was the shared cell changed by someone else since the last sync?}
  F -- no --> G[Write the new value]
  F -- yes --> H[Record a conflict; leave both values]
  C -- ownership unresolved --> H
```

Not every difference is a conflict. A newer scanner observation of a scanner-owned field legitimately replaces an older one.
A blank shared value follows its explicit empty-value rule and is never assumed to mean delete. Conflict records hold no
sensitive values.

# Run status

```mermaid
stateDiagram-v2
  [*] --> running
  running --> completed: all planned changes applied
  running --> partial: some changes failed or were skipped
  running --> failed: nothing could be applied
  running --> cancelled: stopped by the user
  running --> interrupted: process ended unexpectedly
  completed --> [*]
  partial --> [*]
  failed --> [*]
  cancelled --> [*]
  interrupted --> [*]
```

# Related

- [Synchronization](/architecture/synchronization.md)
- [Field Ownership](/concepts/field-ownership.md)
