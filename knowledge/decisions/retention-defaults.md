---
type: Decision
title: "Retention Defaults"
description: Observations keep the current and previous value; run history and logs are bounded by count and age.
tags: [adr, retention, storage, privacy]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: dm
    resource: /architecture/data-model/observations-and-evidence.md
    title: Metadata Observations and Evidence
  - id: ls
    resource: /architecture/local-storage/phase-tables-retention.md
    title: Phase 2 and 3 Storage and Retention
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Unbounded history grows the index, keeps data longer than its value, and widens what a leak could expose. Too little history cannot explain a change such as a removed README.

# Decision

Keep, per field and source, the current observation and the one before it; older values survive only in run summaries. Keep the last 50 scan runs or 90 days, whichever is larger, with item-level detail for the most recent 10. Keep logs as five rotating files of about 1 MiB or 14 days. Durable state (identity events, review decisions) is never removed by retention. All values are configurable; they are starting points to adjust after measuring real volume.

# Alternatives considered

- **Keep everything.** Complete, but unbounded growth and exposure.
- **Keep only the current value.** Smallest, but cannot show what changed.

# Consequences

- Older history is not recoverable once removed.
- Retention runs as an explicit step and reports what it removed.
- Backups hold whatever existed when taken and carry the same classification.

# Related

- [Local Storage](/architecture/local-storage.md)
- [Logging and Redaction](/practices/logging-and-redaction.md)
