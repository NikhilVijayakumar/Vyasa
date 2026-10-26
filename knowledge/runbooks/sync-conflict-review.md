---
type: Runbook
title: "Reviewing a Synchronization Conflict"
description: How to read a conflict record and settle it at the owning source.
tags: [synchronization, conflicts, review]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: cf
    resource: /architecture/synchronization/conflicts-and-idempotency.md
    title: Conflicts, Upserts, and Idempotency
  - id: own
    resource: /concepts/field-ownership.md
    title: Field Ownership
---

# What a conflict record shows

The project and field, the local candidate value and its source, the shared candidate value and its source, when it was
detected, the ownership policy applied, and why automatic resolution was not allowed. It holds no sensitive values.[^cf]

# Steps

1. **Identify the owner** of the field using [Field Ownership](/concepts/field-ownership.md).
2. **Decide at the source.**
   - Portfolio-owned field: correct the value in the sheet.
   - Repository-declared field: correct the canonical profile in the repository and rescan.
   - Scanner-observed field: fix the underlying file, or accept that the observation is right and update the sheet.
3. **Rescan and resynchronize** so both sides agree.
4. **Check the run result** shows the conflict resolved.

# Never

Do not edit the canonical profile just to make a sheet value win, and do not clear a shared cell to force an overwrite.
Vyasa does not resolve conflicts by newest timestamp alone.[^own]

# Related

- [Synchronization Views](/architecture/views/sync-views.md)
- [Field Ownership](/concepts/field-ownership.md)

[^cf]: Conflicts, Upserts, and Idempotency
[^own]: Field Ownership
