---
type: Architecture
title: "Local Storage: Proposed Tables: Relationships, Runs, and Inventory"
description: Tables for relationships, scan runs and results, detector runs, file inventory, and the resolved index.
tags: [sqlite, storage, index]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/local-storage.md
    title: Local Storage
---

# Local Storage: Proposed Tables: Relationships, Runs, and Inventory

*Sections 6.8–6.13 of [Local Storage](/architecture/local-storage.md).*

*Continues the section on proposed tables from [Proposed Tables (core)](/architecture/local-storage/tables-core.md).*

### 6.8 `project_relationships`

Stores confirmed and candidate relationships.

Proposed fields:

- `relationship_id`
- `source_project_id`
- `target_project_id`
- `relationship_type`
- `status`
- `rule_id`
- `rule_version`
- `source_observation_id`
- `created_at`
- `updated_at`

Supported relationship types may include:

- `depends_on`
- `uses_library`
- `shared_technology`
- `related_project`
- `same_logical_project`
- `potential_duplicate`

Rules:

- Confirmed relationships must have a defined basis.
- Candidate relationships must not be presented as established facts.
- Relationship rules must be deterministic and versioned.
- Rejected candidates should not reappear as confirmed relationships without new evidence or an explicit policy change.
- Self-referential relationships must be rejected unless a specific relationship type explicitly permits them.

### 6.9 `scan_runs`

Stores each scanning operation.

Proposed fields:

- `run_id`
- `scan_scope`
- `started_at`
- `completed_at`
- `status`
- `configuration_fingerprint`
- `scanner_version`
- `summary_json` or equivalent structured counters
- `error_count`
- `warning_count`

Suggested run statuses:

- `pending`
- `running`
- `completed`
- `partial`
- `failed`
- `cancelled`
- `interrupted`

An interrupted process may leave a run recorded as `running`. Startup recovery must detect such records and reconcile them without falsely claiming completion.

### 6.10 `scan_item_results`

Stores outcomes for individual projects, repositories, or other scan units.

Proposed fields:

- `result_id`
- `run_id`
- `entity_type`
- `entity_id`
- `status`
- `started_at`
- `completed_at`
- `detectors_attempted`
- `detectors_succeeded`
- `detectors_failed`
- `error_summary`

This table supports partial-scan reporting and prevents a single aggregate run status from hiding failures.

### 6.11 `detector_runs`

Optionally stores detailed detector-level execution outcomes.

Proposed fields:

- `detector_run_id`
- `run_id`
- `entity_type`
- `entity_id`
- `detector_id`
- `detector_version`
- `status`
- `started_at`
- `completed_at`
- `input_fingerprint`
- `error_code`

This table is useful when detector-level diagnostics and incremental invalidation become complex. It may be omitted initially if the same information can be represented adequately in `scan_item_results` without compromising queryability or auditability.

### 6.12 `file_inventory`

Stores relevant files discovered by the scanner.

Proposed fields:

- `inventory_id`
- `repository_id`
- `checkout_id`
- `relative_path`
- `file_role`
- `file_size`
- `modified_at`
- `content_fingerprint`
- `inspection_status`
- `last_seen_run_id`
- `last_seen_at`

Rules:

- Store only file information needed for supported detectors and incremental scanning.
- Do not store complete file contents by default.
- Distinguish a confirmed deletion from a file that was not inspected.
- Do not use modification time alone as universal proof of unchanged content.
- File inventory must respect exclusions and traversal boundaries.

### 6.13 `resolved_project_index`

A separate physical table is optional.

The implementation may derive resolved project summaries from normalized tables or maintain a materialized local projection for efficient queries.

If a projection is maintained:

- It must be rebuildable from authoritative local storage records and applicable external-source records.
- Updates must be transactional with the observations they represent, or carry an explicit generation/version that prevents mismatched reads.
- It must not become an independent source of truth.
- Its schema and refresh behaviour must be tested.

The implementation should prefer the simplest design that meets query performance requirements.
