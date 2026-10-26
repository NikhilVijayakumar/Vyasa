---
type: Architecture
title: "Data Model: Field Definitions, Profile, and Uniqueness"
description: Value vocabularies, canonical and draft profiles, and identity and uniqueness rules.
tags: [data-model, index, evidence]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/data-model.md
    title: Data Model
---

# Data Model: Field Definitions, Profile, and Uniqueness

*Sections 16–18 of [Data Model](/architecture/data-model.md).*

## 16. Field Definitions and Validation

Every supported metadata field must have a registered definition.

A field definition should specify:

| Attribute | Purpose |
|---|---|
| `field_key` | Stable machine-readable field identifier. |
| `value_type` | String, boolean, number, list, structured object, or other supported type. |
| `entity_scope` | Project, repository, or checkout. |
| `owner_category` | Repository-owned, Vyasa-generated, portfolio-owned, provider-owned, machine-local, or derived. |
| `allowed_sources` | Sources permitted to produce observations for the field. |
| `validation_rules` | Type and value constraints. |
| `resolution_policy` | Rules for selecting or reporting the resolved value. |
| `export_policy` | Whether the field may be shared, subject to an explicit allowlist. |
| `freshness_policy` | How the value becomes stale or requires revalidation. |

A field registry may be implemented as typed code definitions initially. A separate configurable schema registry is not required unless a concrete extension need justifies it.

### 16.1 Technology Fields

Programming languages and frameworks should be represented as normalized collections of technology observations, rather than one opaque comma-separated string.

Each technology observation should retain:

- Normalized technology identifier.
- Display name.
- Technology category.
- Source evidence.
- Detection status.
- Optional version or constraint when explicitly available.

The model must not imply that a detected manifest proves that a technology is installed or currently used at runtime.

### 16.2 Documentation Fields

Documentation metadata should distinguish:

- File or directory presence.
- Recognized entry points.
- Recognized structure.
- Configuration validity.
- Assessment status.

A directory existing is not sufficient to claim that documentation is complete or useful.

---

## 17. Canonical Profile and Draft Profile

The profile lifecycle must fit the ownership model.

### 17.1 Canonical Profile

A canonical profile is a project-maintained source of declared metadata.

It is read by Vyasa and represented through metadata observations.

The proposed structured format is `.vyasa/project-profile.yaml`, but the final path and schema remain subject to approval.

The model must not require both a structured profile and a root-level `VYASA.md` to be independent authorities for the same fields.

### 17.2 Generated Draft

A generated draft is non-authoritative and optional.

The proposed draft path is `.vyasa/project-profile.draft.yaml`, git-ignored by default.

Draft generation must:

- Be explicitly enabled.
- Include only supported values.
- Mark missing information clearly.
- Never overwrite the canonical profile.
- Never be automatically promoted to canonical status.

### 17.3 Draft Representation

Draft status should be represented separately from canonical profile status.

The system must not treat the existence of a draft file as proof that a canonical profile exists.

A draft's content may become stale. The implementation must define whether it is preserved, marked stale, or regenerated, without silently destroying human edits.

---

## 18. Identity and Uniqueness Constraints

The implementation must enforce or validate the following invariants.

### 18.1 Project Identity

- Every project has a unique `project_id`.
- Project identity is not based solely on a display name.
- Local path changes do not automatically create a new project.
- Ambiguous matches are retained for review.

### 18.2 Repository Identity

- Every repository has a unique `repository_id`.
- Provider identifiers are unique within their relevant provider namespace.
- A remote URL is not universally treated as immutable identity.
- Forks and mirrors are handled according to documented identity rules.

### 18.3 Checkout Identity

- Every local checkout maps to one known repository or a provisional repository record.
- Multiple checkouts may reference the same repository.
- Local checkout paths are unique within the relevant local namespace, subject to the documented filesystem policy.

### 18.4 Observations

- Every observation identifies a valid entity and field.
- Observation values satisfy the field's validation rules.
- Provenance is retained for supported detected or declared values.
- Current-value resolution follows the field ownership policy.

### 18.5 Relationships

- A relationship cannot point to a nonexistent project.
- A relationship must not silently connect unrelated projects based solely on a name collision.
- Derived relationships identify their rule and evidence.
- Self-relationships are rejected unless a specific supported use case explicitly permits them.
