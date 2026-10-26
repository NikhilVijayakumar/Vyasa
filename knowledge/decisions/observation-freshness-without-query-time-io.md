---
type: Decision
title: "Observation Freshness Without Query-Time I/O"
description: Queries report observation age and index freshness; they never inspect files or refresh to decide staleness.
tags: [adr, freshness, queries]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: fr
    resource: /concepts/freshness-and-staleness.md
    title: Freshness and Staleness
  - id: ex
    resource: /concepts/explicit-operations.md
    title: Explicit Operations
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

A query that checks whether files changed does hidden filesystem work and changes latency unpredictably.

# Decision

Observations become `stale` only at a scan, when their fingerprint or detector version differs or the source is unreadable. Between scans a result carries the time it was observed, and the index reports `current`, `stale`, `partial`, or `unknown` from the last run and a configurable threshold.

# Alternatives considered

- **Stat files on each query.** More current, but hidden work.
- **Refresh when stale.** Violates explicit operations.

# Consequences

- A change since the last scan is visible only as age.
- The threshold needs a default and documentation.

# Related

- [Freshness and Staleness](/concepts/freshness-and-staleness.md)
