---
type: Decision
title: "Ownership-Based Conflict Resolution"
description: Conflicts are decided by who owns the field, field by field, and never by newest timestamp alone.
tags: [adr, ownership, conflicts, synchronization]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: own
    resource: /concepts/field-ownership.md
    title: Field Ownership
  - id: cf
    resource: /architecture/synchronization/conflicts-and-idempotency.md
    title: Conflicts, Upserts, and Idempotency
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Local scans, repository declarations, human edits in the registry, and providers can all hold a value for the same field. Last-write-wins would let a stale device or a scan overwrite a person.

# Decision

Each field has one owner category and a precedence list. A human-managed shared field is authoritative in the sheet and is imported. A scanner-owned shared field is written only when the last scan completed and the shared cell still holds the last synchronized value; a hand-edited cell is recorded as a conflict and left untouched. Unresolved ownership is a conflict. Conflict records hold no sensitive values, and resolution happens at the owning source.

# Alternatives considered

- **Last write wins.** Simple, but silently destroys human edits.
- **Always prefer local.** Overwrites portfolio management.
- **Always prefer the sheet.** Lets any editor override declared facts.

# Consequences

- A conflict record and status are required, and counts are reported.
- Some differences wait for a person.
- Per-field handling lets unrelated fields still synchronize.

# Related

- [Field Ownership](/concepts/field-ownership.md)
- [Reviewing a Synchronization Conflict](/runbooks/sync-conflict-review.md)
