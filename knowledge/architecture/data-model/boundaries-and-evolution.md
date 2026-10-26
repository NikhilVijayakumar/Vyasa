---
type: Architecture
title: "Data Model: Data Boundaries, Mapping, and Schema Evolution"
description: Local versus shared data, SQLite mapping guidance, serialization, and schema change.
tags: [data-model, index, evidence]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/data-model.md
    title: Data Model
---

# Data Model: Data Boundaries, Mapping, and Schema Evolution

*Sections 19–22 of [Data Model](/architecture/data-model.md).*

## 19. Local and Shared Data Boundaries

The model separates data into three categories.

### 19.1 Local Operational Data

Stored only in local persistence:

- Absolute checkout paths.
- Workspace roots.
- Local database location.
- Local scan state.
- Machine-specific mappings.
- Local diagnostics.
- Local configuration and credential references.

### 19.2 Shareable Project Metadata

Potentially synchronized after explicit approval:

- Stable project ID.
- Project name.
- Repository URL.
- Technologies.
- Documentation and standards status.
- Approved lifecycle information.
- Shared review status.

These fields are not automatically exported merely because they are available.

### 19.3 Credentials and Secrets

Credentials and secret values are not project metadata.

They must not be persisted in the shared registry, metadata observations, evidence references, or ordinary operational logs.

The export mechanism must use a positive allowlist rather than excluding only known sensitive fields.

---

## 20. SQLite Mapping Guidance

The physical SQLite schema should preserve the logical distinctions in this document.

A possible logical table inventory is:

| Table | Purpose |
|---|---|
| `projects` | Logical project records. |
| `repositories` | Repository identity and shared repository attributes. |
| `project_repositories` | Project-to-repository associations. |
| `local_checkouts` | Machine-specific checkout mappings. |
| `external_identities` | Provider and other external identity references. |
| `field_definitions` | Supported metadata field definitions, if persisted. |
| `metadata_observations` | Field observations and provenance. |
| `evidence_references` | Source references supporting observations. |
| `project_relationships` | Explicit and derived project relationships. |
| `scan_runs` | Scan execution summaries. |
| `scan_item_results` | Per-item scan outcomes. |
| `sync_runs` | Phase 2 synchronization summaries. |
| `sync_item_results` | Per-project synchronization outcomes. |
| `shared_registry_records` | Phase 2 shared registry mappings and status. |
| `remote_discovery_runs` | Phase 3 provider discovery summaries. |

This inventory is a proposed mapping, not a requirement to create every table during Phase 1.

The SQLite design must define:

- Primary and foreign keys.
- Unique constraints.
- Search indexes.
- Transaction boundaries.
- Migration strategy.
- Retention policy.
- JSON usage, if any.
- Database integrity checks.

The physical schema must not duplicate every metadata value into unrelated tables without a clear reason. A hybrid design may be appropriate: stable entity and operational tables plus normalized observations and typed query projections.

---

## 21. API and Serialization Boundaries

The domain model must not be exposed directly as an unversioned persistence representation.

MCP responses and Google Sheets rows should use explicit mapping layers.

### 21.1 MCP Serialization

MCP response schemas should define:

- Stable identifiers.
- Structured metadata fields.
- Observation status.
- Source provenance.
- Freshness information.
- Error representation.

Responses must not require clients to understand SQLite table structures.

### 21.2 Google Sheets Mapping

The Sheets adapter maps the approved shareable subset of the domain model to the agreed workbook schema.

Spreadsheet column names and ordering must not determine the internal domain model.

### 21.3 Remote Provider Mapping

GitHub and Bitbucket responses must be normalized into the repository, observation, and evidence models.

Provider-specific extensions may be preserved when useful, but provider API response structures must not become mandatory core fields.

---

## 22. Schema Evolution

The model must evolve without losing valid project knowledge.

### 22.1 Versioning

The implementation must track the SQLite schema version and define a migration strategy.

Metadata detector versions and shared registry schema versions should be tracked independently where needed.

### 22.2 Adding Fields

New fields must define:

- Type.
- Owner.
- Allowed sources.
- Validation rules.
- Resolution policy.
- Export policy.
- Freshness policy.

A new field must not become shareable by default.

### 22.3 Changing Field Semantics

If a field's meaning changes, the change must be documented and tested.

For example, changing `last_scanned_at` from local scan time to last synchronization time is not a harmless rename; these are distinct operational facts and should remain distinct fields.

### 22.4 Identity Migrations

Changes to project identity rules must include a reconciliation strategy.

The migration must detect collisions and ambiguous mappings instead of merging records destructively.

### 22.5 Backward Compatibility

Database migrations must preserve valid records where possible. Breaking MCP or registry changes require an explicit compatibility and migration policy.
