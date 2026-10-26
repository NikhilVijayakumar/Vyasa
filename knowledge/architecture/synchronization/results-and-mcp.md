---
type: Architecture
title: "Synchronization: Results, MCP Interaction, and Observability"
description: Run result reporting, how sync relates to MCP, and diagnostics.
tags: [sync, google-sheets, phase-2]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/synchronization.md
    title: Synchronization
---

# Synchronization: Results, MCP Interaction, and Observability

*Sections 16–18 of [Synchronization](/architecture/synchronization.md).*

## 16. Synchronization Results and History

### 16.1 Run Status

Recommended statuses (the same set every run type uses):

- `pending`
- `running`
- `completed`
- `partial`
- `failed`
- `cancelled`
- `interrupted`

### 16.2 Result Counters

A run summary should include:

- Records read.
- Records created.
- Records updated.
- Records unchanged.
- Fields skipped due to ownership.
- Conflicts detected.
- Records requiring review.
- Records skipped.
- Errors.
- Pending verification operations.

The exact counters must be defined consistently between local history and the shared `Scan History` tab.

### 16.3 Local History

SQLite should retain detailed synchronization runs and item-level results.

Google Sheets should contain only the approved aggregate history summary.

### 16.4 Honest Completion

A run is `completed` only when all required operations for its declared scope have succeeded or were safely determined to require no change.

If some required operations remain unresolved or failed, the result must be `partial` or `failed`, according to the defined run policy.

---

## 17. Synchronization and MCP Interface

### 17.1 Query Behaviour

The existing MCP query tools should read from the local index and expose source provenance.

A shared-only project may be returned even when no local checkout exists.

### 17.2 Explicit Synchronization

If synchronization is exposed through MCP, the proposed tool is:

`sync_shared_registry`

Its contract should include:

- Direction: pull, push, or bidirectional.
- Scope: all eligible records or a supported subset.
- Dry-run option.
- Run status and summary.
- Conflicts and pending work.
- Whether writes were performed.

The final input schema must prevent ambiguous combinations and require explicit authorization for writes.

### 17.3 Capability Controls

The sync tool must be unavailable when the integration is not configured or the user has not enabled it.

A read-only deployment must not silently gain write access because credentials happen to be present.

### 17.4 Query Consistency

The MCP interface must distinguish:

- Last local scan.
- Last successful pull.
- Last successful push.
- Last synchronization attempt.
- Current known conflicts.

A successful pull does not prove that local repository observations are fresh.

---

## 18. Observability and Diagnostics

Logs and structured results should identify:

- Sync run ID.
- Direction and scope.
- Spreadsheet identity, represented safely.
- Schema validation outcome.
- Counts of reads, writes, skips, and conflicts.
- Retry attempts.
- API failure category.
- Verification outcome.
- Completion status.

They must not include tokens, secret configuration, or full raw project records unnecessarily.

Diagnostics should make it possible to determine whether a problem occurred during authentication, schema validation, matching, conflict resolution, API writing, verification, or local persistence.
