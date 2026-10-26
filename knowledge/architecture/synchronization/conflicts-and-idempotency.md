---
type: Architecture
title: "Synchronization: Conflicts, Upserts, and Idempotency"
description: Detecting and resolving conflicts, and making repeated runs converge.
tags: [sync, google-sheets, phase-2]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/synchronization.md
    title: Synchronization
---

# Synchronization: Conflicts, Upserts, and Idempotency

*Sections 9–10 of [Synchronization](/architecture/synchronization.md).*

## 9. Conflict Detection and Resolution

### 9.1 Conflict Definition

A conflict occurs when multiple sources provide incompatible values for a field and the ownership rules do not authorize an automatic resolution.

Not every difference is a conflict.

For example, a new scanner observation for a scanner-owned field may legitimately replace an older scanner observation when the scan completed successfully.

### 9.2 Conflict Examples

| Situation | Required behaviour |
|---|---|
| Shared tracking level changed by a human | Pull the shared value into the local cache |
| Local scan detects new technologies | Update approved scanner-owned fields in Sheets |
| Project name differs between profile and sheet | Apply the defined name ownership policy; otherwise flag |
| Local project identity is ambiguous | Do not create or merge automatically |
| Sheet row has a duplicate project ID | Stop writes affecting the ambiguous identity and report it |
| Local repository is temporarily inaccessible | Do not clear previously valid shared metadata |
| Shared field is blank | Apply its explicit empty-value policy; do not assume blank means delete |
| Spreadsheet schema is unexpected | Reject writes and report a schema error |

### 9.3 Field-Level Conflict Handling

When a conflict is limited to one field, unrelated fields may still synchronize if doing so is safe and supported by the change plan.

The synchronizer must not discard the entire project record unnecessarily, nor should it continue with an unsafe identity or schema ambiguity.

### 9.4 Conflict Records

Conflicts should be stored locally with enough detail to explain:

- Logical project and field.
- Local candidate value and source.
- Shared candidate value and source.
- Detection timestamp.
- Ownership policy applied.
- Reason automatic resolution was not allowed.
- Resolution status, if a later resolution workflow is implemented.

Sensitive values must not be copied into conflict records.

### 9.5 Manual Resolution

The initial implementation may require a human or coding agent to resolve conflicts through the project's normal metadata-maintenance workflow or the shared registry.

Vyasa must not silently modify the canonical project profile to resolve a conflict.

A dedicated conflict-resolution tool is not required for the initial phase.

---

## 10. Upsert and Idempotency Rules

### 10.1 Upsert Key

The primary matching key for project rows is `Project ID`.

The primary matching key for documentation and standards rows is also `Project ID`.

The scan history uses `Run ID` to identify an operation.

### 10.2 Upsert Behaviour

For each approved record:

1. Read and validate the existing row.
2. Match by stable ID.
3. Compare the fields owned by the current source.
4. Skip unchanged fields.
5. Update only approved fields.
6. Preserve human-managed and local-only fields.
7. Verify the resulting state where practical.
8. Record the outcome.

### 10.3 Retry Safety

If a write times out:

- Do not assume it failed.
- Read the affected record when feasible.
- Compare its values with the intended update.
- Mark it successful if the intended state is already present.
- Retry only the remaining changes.

### 10.4 Duplicate Prevention

The adapter must validate that each logical project ID appears only once in each relevant tab.

If duplicate IDs exist, the system must not select an arbitrary row and overwrite it.

The ambiguity must be reported and handled through an explicit repair process.

### 10.5 No Blind Row Replacement

The synchronizer must not clear and rewrite entire rows unless the row is exclusively owned by the synchronizer and the replacement semantics have been explicitly approved.
