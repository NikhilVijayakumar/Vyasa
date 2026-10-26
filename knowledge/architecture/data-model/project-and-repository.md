---
type: Architecture
title: "Data Model: Project and Repository"
description: The logical project and the repository entities with their fields, statuses, and associations.
tags: [data-model, index, evidence]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/data-model.md
    title: Data Model
---

# Data Model: Project and Repository

*Sections 5–6 of [Data Model](/architecture/data-model.md).*

## 5. Project Entity

### 5.1 Purpose

The Project entity represents a logical project independently of its name, local directory, and repository provider.

### 5.2 Logical Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `project_id` | String | Yes | Stable Vyasa project identifier. |
| `display_name` | String or unknown | No | Current resolved project name. |
| `identity_status` | Enum | Yes | Whether identity is resolved, provisional, or ambiguous. |
| `lifecycle_status` | Enum or unknown | No | Explicitly declared lifecycle state. |
| `details_status` | Enum | Yes | Completeness state of the available project metadata. |
| `created_at` | Timestamp | Yes | Time the local system first registered the record. |
| `updated_at` | Timestamp | Yes | Time the logical record was last updated. |
| `last_observed_at` | Timestamp | No | Time the project was last successfully observed. |
| `record_version` | Integer | Yes | Version for local record evolution or optimistic updates, as needed. |

The exact timestamp semantics must be documented in the implementation. In particular, `updated_at` must not be used as a substitute for a successful scan timestamp.

### 5.3 Project Metadata

Purpose, domain, project type, technologies, and other descriptive values are represented through metadata fields and their observations.

The model should not require every project to have every descriptive field populated.

### 5.4 Lifecycle Status

Lifecycle status must represent an explicit declaration from its designated owner.

Proposed values include:

- `active`
- `maintenance`
- `paused`
- `archived`
- `unknown`

These values are a proposed controlled vocabulary, not an approved list of all possible states.

A project must not be automatically assigned `archived` merely because it has not been scanned recently or its repository is inaccessible.

### 5.5 Details Status

`details_status` describes the completeness of the currently available metadata, not the quality of the project itself.

Proposed values:

- `complete`
- `partial`
- `requires_review`
- `unknown`

The rules for assigning these values must be deterministic and documented.

---

## 6. Repository Entity

### 6.1 Purpose

The Repository entity represents a source-control repository independently of any particular local checkout.

### 6.2 Logical Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `repository_id` | String | Yes | Stable Vyasa repository identifier. |
| `display_name` | String or unknown | No | Repository name. |
| `repository_type` | Enum | Yes | Git or another explicitly supported repository type. |
| `primary_remote_url` | String or unknown | No | Resolved primary repository URL. |
| `provider_type` | Enum | Yes | Local-only, GitHub, Bitbucket Cloud, or another supported provider. |
| `provider_repository_id` | String or unknown | No | Stable identifier assigned by an external provider, if available. |
| `default_branch` | String or unknown | No | Provider-reported or otherwise explicitly observed default branch. |
| `repository_status` | Enum | Yes | Current knowledge of repository availability and access. |
| `created_at` | Timestamp | Yes | Time first registered locally. |
| `updated_at` | Timestamp | Yes | Time the repository record was last updated. |

`provider_type` and `repository_status` must use defined values. Provider-specific status must not be confused with a project's lifecycle status.

### 6.3 Repository Status

Proposed values:

- `available`
- `inaccessible`
- `missing`
- `unknown`

These values describe the evidence available to Vyasa. They do not necessarily establish the actual state of the remote provider.

For example, a timeout must not set the repository to `missing`.

### 6.4 Repository Associations

A repository association connects a logical project to a repository.

It may include:

- `project_id`
- `repository_id`
- `association_type`
- `association_source`
- `created_at`

Proposed association types include:

- `primary`
- `component`
- `documentation`
- `related`
- `unknown`

The association source distinguishes human-declared relationships from deterministic matches.

Vyasa must not group repositories into one project solely because their names are similar or their directories share a parent.
