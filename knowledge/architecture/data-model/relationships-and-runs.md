---
type: Architecture
title: "Data Model: Relationships, Scan Runs, and Item Results"
description: Project relationships, scan run fields and status rules, and per-item outcomes.
tags: [data-model, index, evidence]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/data-model.md
    title: Data Model
---

# Data Model: Relationships, Scan Runs, and Item Results

*Sections 11–12 of [Data Model](/architecture/data-model.md).*

## 11. Project Relationship Entity

### 11.1 Purpose

Project Relationship records relationships between projects and, where appropriate, repositories.

Relationships may be explicitly declared or derived using deterministic rules.

### 11.2 Logical Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `relationship_id` | String | Yes | Unique relationship identifier. |
| `source_project_id` | String | Yes | Source project. |
| `target_project_id` | String | Yes | Target project. |
| `relationship_type` | Enum | Yes | Type of relationship. |
| `relationship_status` | Enum | Yes | Confirmed, candidate, rejected, or unknown. |
| `source_type` | Enum | Yes | Human declaration or deterministic rule. |
| `evidence_refs` | Collection | No | Evidence supporting the relationship. |
| `rule_id` | String or unknown | No | Rule that produced the relationship, if derived. |
| `rule_version` | String or unknown | No | Version of the derivation rule. |
| `observed_at` | Timestamp | Yes | Time the relationship was established or evaluated. |

### 11.3 Relationship Types

Initial supported types may include:

- `depends_on`
- `uses_library`
- `shared_technology`
- `related_project`
- `same_logical_project`
- `potential_duplicate`

The final vocabulary must distinguish direct evidence from weaker indicators.

### 11.4 Relationship Status

- `confirmed`: Supported by explicit or sufficiently strong defined evidence.
- `candidate`: A deterministic rule identifies a possible relationship requiring further verification.
- `rejected`: A previously considered relationship has been explicitly rejected or invalidated.
- `unknown`: Available evidence is insufficient to establish the relationship.

A shared programming language alone may establish a `shared_technology` relationship, but it must not establish a dependency or prove that code can be reused.

### 11.5 Derived Relationship Rules

Every derived relationship must identify its basis.

For example:

- A manifest explicitly references another internal package.
- Two projects declare use of the same library.
- A configured rule finds a common technology.
- Repository metadata explicitly links two repositories.

Similarity-based or semantic relationships requiring LLM inference are outside the initial deterministic model.

---

## 12. Scan Run and Scan Item Result

### 12.1 Scan Run

A Scan Run represents one workspace discovery or index-refresh operation.

| Field | Type | Required | Description |
|---|---|---|---|
| `scan_run_id` | String | Yes | Unique run identifier. |
| `scan_type` | Enum | Yes | Initial, full, incremental, or targeted scan. |
| `started_at` | Timestamp | Yes | Run start time. |
| `completed_at` | Timestamp or unknown | No | Completion time. |
| `run_status` | Enum | Yes | Pending, running, completed, partial, failed, cancelled, or interrupted. |
| `scan_scope` | Structured value | Yes | Workspace roots or selected project scope. |
| `scanner_version` | String | Yes | Scanner version. |
| `configuration_fingerprint` | String or unknown | No | Identifier for the effective relevant configuration. |
| `discovered_count` | Integer | Yes | Number of discovered candidates. |
| `processed_count` | Integer | Yes | Number processed. |
| `updated_count` | Integer | Yes | Number of records updated. |
| `skipped_count` | Integer | Yes | Number skipped. |
| `error_count` | Integer | Yes | Number of errors. |

The exact count semantics must be documented so that counts remain meaningful across full and incremental scans.

### 12.2 Scan Item Result

A Scan Item Result records an individual item's outcome within a run.

It should identify:

- Scan run.
- Project, repository, or candidate identifier, where known.
- Outcome status.
- Relevant error category.
- Detector or inspection stage.
- Start or completion information where useful.

This allows partial failures to be reported without marking the entire run as a success.

### 12.3 Scan Status Rules

A scan is `completed` only when its defined scope completes successfully.

A scan is `partial` when some required items fail or remain incomplete but useful results were produced.

A scan is `failed` when the operation cannot complete its essential purpose.

An interrupted operation must not be reported as a successful complete scan.
