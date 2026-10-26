---
type: Architecture
title: "Data Model: Shared Registry and Remote Observations"
description: Phase 2 and 3 entities: registry records, synchronization runs, and remote repository observations.
tags: [data-model, index, evidence]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/data-model.md
    title: Data Model
---

# Data Model: Shared Registry and Remote Observations

*Sections 13–15 of [Data Model](/architecture/data-model.md).*

## 13. Shared Registry Record — Phase 2

### 13.1 Purpose

The Shared Registry Record represents the shared view of a project in Google Sheets.

It is not a duplicate authoritative copy of all local SQLite data.

### 13.2 Logical Fields

| Field | Type | Description |
|---|---|---|
| `project_id` | String | Stable Vyasa project identifier. |
| `registry_record_id` | String or unknown | Registry row or external record identifier, if needed. |
| `registry_schema_version` | String | Version of the expected registry schema. |
| `shared_fields` | Structured value | Explicitly approved shareable metadata. |
| `portfolio_fields` | Structured value | Human-managed portfolio metadata. |
| `last_synced_at` | Timestamp or unknown | Last successful synchronization time for this record. |
| `sync_status` | Enum | Current synchronization status. |
| `conflict_status` | Enum | Whether unresolved field conflicts exist. |

The workbook's physical column layout is defined separately in the synchronization architecture.

### 13.3 Shared and Portfolio Fields

Shared fields may include:

- Project name.
- Repository URL.
- Programming languages.
- Frameworks and technologies.
- Documentation status.
- Standards configuration status.
- Approved lifecycle information.
- Last successful scan information with clearly defined semantics.

Portfolio fields may include:

- Tracking level.
- Priority, if enabled.
- Human-maintained notes.
- Review decisions.

The final ownership mapping must be approved before synchronization is implemented.

### 13.4 Registry Rules

1. Only allowlisted fields may be exported.
2. Local paths and machine-specific state are excluded.
3. Human-managed fields are not overwritten by local scans.
4. Missing local checkouts do not remove shared project records.
5. Registry schema changes must be detected and handled explicitly.
6. Synchronization status must distinguish success, partial success, failure, and conflict.

---

## 14. Synchronization Run — Phase 2

A Synchronization Run represents a synchronization attempt between local state and the shared registry.

Logical fields include:

- `sync_run_id`
- `started_at`
- `completed_at`
- `sync_direction`
- `run_status`
- `registry_schema_version`
- `projects_processed`
- `records_created`
- `records_updated`
- `conflicts_detected`
- `errors_encountered`

A per-record synchronization result should identify the affected project, the result, and relevant error or conflict information.

Synchronization must be retry-safe. A failed attempt must not automatically change a project's lifecycle status or delete the last known valid record.

---

## 15. Remote Repository Observations — Phase 3

Remote discovery extends the Repository and Metadata Observation entities.

Remote observations should preserve:

- Provider type.
- Provider repository ID.
- Repository URL.
- Access scope where relevant.
- Provider-reported metadata.
- Remote branch or revision inspected.
- Observation timestamp.
- Request outcome.
- Evidence for inspected files.

Provider-specific information may be retained as extension fields, but core identity and metadata must remain provider-neutral.

### 15.1 Remote Access Status

The model must distinguish:

- Successfully accessible.
- Confirmed unavailable under the supported access scope.
- Unauthorized or forbidden.
- Rate-limited.
- Temporarily unavailable.
- Unknown.

These states must not be collapsed into a simple `exists` boolean.

### 15.2 Remote Discovery Run

A remote discovery run should record:

- Provider.
- Configured discovery scope.
- Start and completion times.
- Pagination progress or completion state.
- Repositories discovered.
- Repositories inspected.
- Errors and rate-limit events.
- Overall outcome.

Credentials and secret values must never be stored in the run record.
