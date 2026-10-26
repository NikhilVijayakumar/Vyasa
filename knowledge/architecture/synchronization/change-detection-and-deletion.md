---
type: Architecture
title: "Synchronization: Change Detection and Deletion"
description: Detecting what changed since the last sync, and why records are retired rather than deleted.
tags: [sync, google-sheets, phase-2]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/synchronization.md
    title: Synchronization
---

# Synchronization: Change Detection and Deletion

*Sections 11–12 of [Synchronization](/architecture/synchronization.md).*

## 11. Change Detection and Sync State

### 11.1 Local State

SQLite should track the last known synchronization state separately from scanner observations.

Proposed local state includes:

- Shared spreadsheet identity.
- Sheet schema version.
- Last successful pull timestamp.
- Last successful push timestamp.
- Last attempted synchronization.
- Last known remote record fingerprint or revision, where available.
- Per-record synchronization outcome.
- Pending verification state.
- Outstanding conflicts.

### 11.2 Fingerprints

A deterministic fingerprint may be calculated over a normalized set of fields.

The fingerprint must:

- Include only fields relevant to the comparison.
- Use a documented canonical serialization.
- Exclude timestamps that change without semantic content changes.
- Exclude secrets and machine-local state.
- Change when a relevant field value changes.

A fingerprint is a change-detection aid, not a substitute for ownership validation.

### 11.3 Remote Change Detection

Google Sheets does not necessarily provide the same revision and transaction semantics as a database.

The adapter must define how it detects changes using available API responses, stored fingerprints, and read-back verification.

It must not assume that a row remains unchanged merely because its project ID is stable.

### 11.4 Pending Writes

When a remote write result is uncertain, record the pending operation and reconcile it on the next synchronization attempt.

Do not discard the intended update merely because the local process stopped before receiving confirmation.

---

## 12. Deletion and Retirement Policy

Deletion requires special handling because devices may have different workspace contents.

### 12.1 Local Project Missing

If a project is not discovered during a scan:

- Mark its local discovery or checkout status according to the approved policy.
- Preserve its logical project record.
- Preserve the shared registry record.
- Do not delete the project from Sheets.

A device may have had the repository removed, excluded, or temporarily inaccessible.

### 12.2 Shared Row Missing

If a shared row disappears:

- Record the absence during a successful registry read.
- Compare it with the previous synchronization state.
- Do not immediately recreate or delete records when the cause is ambiguous.
- Follow the explicit policy for shared-record deletion and human-managed fields.

### 12.3 Retirement

Lifecycle retirement is a separate semantic operation from physical deletion.

A project may be marked archived or retired through an approved lifecycle workflow. The system must not infer retirement solely from age, inactivity, or local absence.

### 12.4 Tombstones

If reliable deletion synchronization is required later, a tombstone or explicit retirement record may be introduced.

It must identify the entity and deletion intent without relying solely on a missing spreadsheet row.

The initial implementation should favour preservation and review over automatic deletion.
