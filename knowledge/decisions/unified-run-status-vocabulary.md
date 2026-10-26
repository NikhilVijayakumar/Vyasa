---
type: Decision
title: "Unified Run Status Vocabulary"
description: Scan, synchronization, and discovery runs share one status set.
tags: [adr, status, runs]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: dm
    resource: /architecture/views/data-model-views.md
    title: Data Model Views
  - id: ls
    resource: /architecture/local-storage/tables-operations.md
    title: Proposed Tables: Relationships, Runs, and Inventory
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Run statuses were described differently in the data model, the storage tables, and the synchronization design, which would force translation and invite bugs.

# Decision

Use one vocabulary for every run: `pending`, `running`, `completed`, `partial`, `failed`, `cancelled`, `interrupted`. Skips that policy allows are counted, not a separate status. An interrupted or cancelled run is never reported as complete.

# Alternatives considered

- **One vocabulary per run type.** Accurate to each, but inconsistent for readers and tests.

# Consequences

- Documents and schema use the same words.
- Counters carry the detail that extra statuses would have carried.

# Related

- [Data Model Views](/architecture/views/data-model-views.md)
