---
type: Architecture
title: "Local Storage: Proposed Tables: Core"
description: Tables for migrations, projects, repositories, associations, checkouts, observations, and evidence.
tags: [sqlite, storage, index]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/local-storage.md
    title: Local Storage
---

# Local Storage: Proposed Tables: Core

*Sections 6.1–6.7 of [Local Storage](/architecture/local-storage.md).*

## 6. Proposed Tables

The following tables are the proposed initial logical inventory. Exact columns, SQL types, constraints, and indexes will be finalized during implementation.

### 6.1 `schema_migrations`

Records database schema changes.

Proposed fields:

- `version`
- `migration_id`
- `applied_at`
- `checksum`, where useful

Requirements:

- Every successful migration must be recorded.
- A migration must not be marked complete before its changes are committed.
- Reapplying an already completed migration must not duplicate its effects.
- Unexpected migration state must produce an actionable error.

### 6.2 `projects`

Stores stable logical project records used by local queries.

Proposed fields:

- `project_id`
- `display_name`
- `identity_status`
- `lifecycle_status`
- `tracking_level`, if applicable
- `details_status`
- `created_at`
- `updated_at`
- `last_observed_at`
- `record_version`

Rules:

- `project_id` must be stable according to the approved identity policy.
- Display names are not unique identifiers.
- Missing descriptive metadata must not prevent the project record from existing.
- Human-managed fields must follow the ownership rules.
- Project deletion must not be inferred from one failed or incomplete scan.

The table should contain a compact resolved representation, not duplicate every source observation as an untraceable value.

### 6.3 `repositories`

Stores logical repository identities.

Proposed fields:

- `repository_id`
- `display_name`
- `repository_type`
- `provider_type`
- `remote_identity`
- `provider_repository_id`, when available
- `default_branch`, when known
- `repository_status`
- `created_at`
- `updated_at`

Rules:

- Repository identity must be distinct from local checkout identity.
- Remote URLs must be normalized using a documented provider-specific policy.
- Credentials embedded in remote URLs must be removed before persistence or exposure.
- Forks and upstream repositories must not be merged merely because their names are similar.

### 6.4 `project_repositories`

Associates logical projects with repositories.

Proposed fields:

- `project_id`
- `repository_id`
- `association_type`
- `association_status`
- `source_type`
- `created_at`
- `updated_at`

This association supports a logical project containing multiple repositories and permits a repository to have explicitly managed associations where the domain rules allow them.

The uniqueness constraints must prevent accidental duplicate associations without preventing legitimate many-to-many relationships.

### 6.5 `local_checkouts`

Stores machine-local repository checkout information.

Proposed fields:

- `checkout_id`
- `repository_id`
- `local_path`
- `workspace_root`
- `checkout_type`
- `last_known_revision`
- `last_scan_at`
- `checkout_status`
- `created_at`
- `updated_at`

This table is local-only.

It must never be exported to Google Sheets as a shared project record.

Local paths must be treated as machine-specific identifiers, not as stable project IDs.

If a directory moves, Vyasa should attempt to reconcile the checkout using repository identity rather than automatically creating a new logical project.

### 6.6 `metadata_observations`

Stores individual declarations and detected facts.

Proposed fields:

- `observation_id`
- `entity_type`
- `entity_id`
- `field_key`
- `value_type`
- `value_json` or an equivalent typed representation
- `status`
- `source_type`
- `source_entity_id`
- `detector_id`
- `detector_version`
- `observed_at`
- `source_revision`
- `content_fingerprint`
- `is_current`
- `created_at`

The actual schema should use validated types and avoid encoding all fields as arbitrary unvalidated JSON.

Rules:

- Values must be validated against field definitions.
- Status must use the documented observation vocabulary.
- Observations from different sources must remain distinguishable.
- Historical records must not silently appear current.
- A detector update must not falsely rewrite the provenance of an old observation.

If a project field has several competing observations, the resolution layer must apply the ownership and precedence rules rather than relying on whichever database row was written last.

### 6.7 `evidence_references`

Stores references to the sources that support observations.

Proposed fields:

- `evidence_id`
- `observation_id`
- `source_type`
- `repository_id`, when applicable
- `checkout_id`, when applicable
- `relative_path`
- `field_reference`
- `line_start`
- `line_end`
- `source_revision`
- `content_fingerprint`
- `observed_at`

Rules:

- Evidence paths should be repository-relative where possible.
- Line numbers should be stored only when the detector can establish them reliably.
- Evidence references must not contain secret values.
- A missing source must not cause evidence to be silently reassigned to another file.
- Stale evidence must remain distinguishable from current evidence.
