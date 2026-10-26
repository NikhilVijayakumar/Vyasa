---
type: Architecture
title: "Data Model: Metadata Observations and Evidence"
description: How values, statuses, sources, current-value resolution, retention, and evidence references are modelled.
tags: [data-model, index, evidence]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/data-model.md
    title: Data Model
---

# Data Model: Metadata Observations and Evidence

*Sections 9–10 of [Data Model](/architecture/data-model.md).*

## 9. Metadata Observation Entity

### 9.1 Purpose

Metadata Observation records a value or status observed from a particular source at a particular time.

It is central to Vyasa's evidence-based design.

Instead of storing only one mutable value, the system should retain enough information to distinguish the currently resolved value from the observations supporting it.

### 9.2 Logical Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `observation_id` | String | Yes | Unique identifier for the observation. |
| `entity_type` | Enum | Yes | Project, repository, or checkout. |
| `entity_id` | String | Yes | Entity being observed. |
| `field_key` | String | Yes | Stable identifier for the metadata field. |
| `value` | Typed value or unknown | No | Observed value. |
| `value_status` | Enum | Yes | Status of the observation. |
| `source_type` | Enum | Yes | Source category. |
| `source_ref` | String or unknown | No | Reference to the source. |
| `observed_at` | Timestamp | Yes | Time the source was observed. |
| `detector_id` | String or unknown | No | Detector or extraction rule that produced the observation. |
| `detector_version` | String or unknown | No | Version of the detector. |
| `source_revision` | String or unknown | No | Relevant repository revision when available. |
| `content_fingerprint` | String or unknown | No | Optional fingerprint for invalidation and change detection. |
| `is_current` | Boolean | Yes | Whether this observation is considered current under the retention policy. |

The logical `value` may be a string, number, boolean, list, structured object, or explicit status depending on the field schema.

The physical database representation must validate values against the field definition rather than allowing arbitrary untyped data.

### 9.3 Value Status

Proposed values:

- `observed`
- `declared`
- `unknown`
- `not_detected`
- `unsupported`
- `inaccessible`
- `stale`
- `conflicting`

These states have different meanings.

| Status | Meaning |
|---|---|
| `observed` | A supported detector found evidence for a value. |
| `declared` | A recognized authoritative source explicitly declared the value. |
| `unknown` | Available evidence cannot establish a value. |
| `not_detected` | The relevant supported search was completed, but the indicator was not found. |
| `unsupported` | The system does not support assessing this field or source format. |
| `inaccessible` | The source could not be inspected successfully. |
| `stale` | The observation may no longer represent the source's current state. |
| `conflicting` | Multiple observations disagree and cannot yet be resolved by the ownership policy. |

These statuses must not be collapsed into a boolean.

For example, `not_detected` for a README after a successful complete scan is different from `inaccessible` when the repository cannot be read.

### 9.4 Source Type

Proposed values:

- `local_git`
- `local_file`
- `canonical_profile`
- `project_documentation`
- `google_sheets`
- `github_api`
- `bitbucket_api`
- `derived_rule`

The list may grow as supported sources are added.

### 9.5 Current Value Resolution

The system may expose a resolved value for a field, but that value must be computed from observations using the field's ownership and precedence rules.

The resolution process must:

1. Identify the field's authoritative owner.
2. Filter out invalid or unsupported observations.
3. Evaluate freshness and source availability.
4. Apply the documented precedence policy.
5. Preserve conflicts that cannot be resolved.
6. Return the resolved value together with appropriate provenance.

The most recently observed value must not automatically win when the source does not own that field.

### 9.6 Observation Retention

The implementation must define which historical observations are retained and which are replaced or compacted.

At minimum, it must retain sufficient information to:

- Explain the current resolved value.
- Distinguish a new observation from an unchanged value.
- Recover from interrupted scans.
- Report stale or unavailable evidence accurately.
- Diagnose identity and synchronization conflicts.

An unlimited history of every file read is not required. Retention should be designed around auditability and storage efficiency.

---

## 10. Evidence Reference Entity

### 10.1 Purpose

Evidence Reference identifies the source supporting a metadata observation.

It should reference evidence rather than copy unnecessary source content into the index.

### 10.2 Logical Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `evidence_id` | String | Yes | Unique evidence identifier. |
| `observation_id` | String | Yes | Associated metadata observation. |
| `evidence_type` | Enum | Yes | File, manifest field, Git configuration, API metadata, or other supported source. |
| `source_locator` | String | Yes | Repository-relative path, field reference, or provider locator. |
| `field_locator` | String or unknown | No | Specific configuration key or field when applicable. |
| `line_start` | Integer or unknown | No | Starting line for line-addressable evidence. |
| `line_end` | Integer or unknown | No | Ending line for line-addressable evidence. |
| `source_revision` | String or unknown | No | Relevant source revision when available. |
| `content_fingerprint` | String or unknown | No | Optional fingerprint of the relevant evidence. |
| `observed_at` | Timestamp | Yes | Time evidence was inspected. |

### 10.3 Evidence Rules

- Paths must be relative to the repository when that representation is sufficient.
- Absolute local paths must not be exported.
- Evidence must identify the relevant file or field as precisely as practical.
- Line numbers should be included when reliable and useful.
- Remote evidence should identify the provider and relevant repository revision where available.
- A missing or inaccessible source must not be represented as current positive evidence.
- Sensitive values must not be copied into evidence records unnecessarily.

A content fingerprint can support change detection, but it must not be treated as proof of semantic equivalence.
