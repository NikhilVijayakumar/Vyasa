---
type: Architecture
title: "Local Storage: Phase 2 and 3 Storage and Retention"
description: Registry and remote provider state, and retention and cleanup.
tags: [sqlite, storage, index]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/local-storage.md
    title: Local Storage
---

# Local Storage: Phase 2 and 3 Storage and Retention

*Sections 13–15 of [Local Storage](/architecture/local-storage.md).*

## 13. Phase 2 — Shared Registry Storage

Google Sheets is the shared project registry, while SQLite remains the local query index and cache.

### 13.1 Local Synchronization State

Phase 2 may introduce tables such as:

- `shared_registry_records`
- `sync_runs`
- `sync_item_results`
- `field_sync_state`

These are proposed logical entities, not mandatory physical table names.

### 13.2 Synchronization Metadata

Store enough information to track:

- Shared record identity.
- Last successful synchronization.
- Last attempted synchronization.
- Synchronization outcome.
- Field ownership.
- Conflict status.
- Relevant shared revision or fingerprint, when available.

### 13.3 Field Ownership

The synchronizer must know whether a field is:

- Repository-owned.
- Scanner-generated.
- Shared human-managed.
- Provider-owned.
- Machine-local.
- Derived.

It must not apply last-write-wins indiscriminately to all fields.

### 13.4 Conflict Handling

A sync failure must not corrupt the local index.

A conflict must remain visible until resolved according to the ownership policy. The system must not silently discard a local observation or overwrite a human-managed registry value.

### 13.5 No Local Paths in Shared State

Local checkout information must never be copied into the shared registry by a generic serialization routine.

The export adapter must construct an approved shared representation explicitly.

---

## 14. Phase 3 — Remote Provider Storage

Remote discovery may add:

- Provider identities.
- Remote repository observations.
- Remote discovery runs.
- Provider-specific pagination or continuation state, where safe.
- Provider access and error summaries.
- Remote revision information.

### 14.1 Remote Observations

Remote evidence must identify its provider and relevant repository revision where available.

Remote observations must remain distinguishable from local checkout observations.

### 14.2 Authentication State

Credentials must not be stored as ordinary SQLite metadata fields.

Provider connection configuration and secrets must use approved local configuration or secure secret storage.

The database may record a safe connection status or last successful access time without recording the credential itself.

### 14.3 Rate Limits and Failures

Provider errors and rate-limit state may be persisted as operational metadata.

A failed remote request must not cause existing repository records to be deleted or their previous values to be represented as confirmed absence.

---

## 15. Data Retention and Cleanup

### 15.1 Historical Observations

The implementation must define which historical observations are retained and for how long.

Current observations must remain easy to query. Historical records should not grow without bound if the scanner runs frequently.

### 15.2 Scan History

Scan history is useful for diagnosing incomplete scans and understanding changes.

Retention should be configurable or based on a documented policy. Any cleanup must preserve enough information to understand the current index state.

### 15.3 File Inventory Cleanup

Old inventory entries may be removed only when their lifecycle is understood.

The scanner must not treat an entry missing from a partial scan as a confirmed deletion.

### 15.4 Orphan Cleanup

Cleanup operations must use explicit consistency rules and foreign-key constraints.

A missing checkout must not automatically delete its repository or logical project.

### 15.5 Database Compaction

SQLite maintenance operations such as checkpointing or vacuuming should be performed deliberately.

They must not run on every query and must not compromise database availability during active operations.
