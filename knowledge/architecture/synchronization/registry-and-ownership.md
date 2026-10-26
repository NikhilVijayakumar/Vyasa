---
type: Architecture
title: "Synchronization: Registry Structure, Ownership, and Identity"
description: The three registry tabs, which side owns each field, and how projects are matched across devices.
tags: [sync, google-sheets, phase-2]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/synchronization.md
    title: Synchronization
---

# Synchronization: Registry Structure, Ownership, and Identity

*Sections 4–6 of [Synchronization](/architecture/synchronization.md).*

## 4. Shared Registry Structure

The initial spreadsheet should contain three tabs.

No additional tab should be required for the first implementation unless a concrete requirement justifies it.

### 4.1 Tab 1 — `Project Registry`

One row represents one logical project.

| Field | Description | Proposed ownership |
|---|---|---|
| `Project ID` | Stable Vyasa logical project identifier | Identity system |
| `Project Name` | Human-readable project name | Repository/profile or shared edit, subject to resolution policy |
| `Domain` | Project domain or business area | Shared human-managed or explicitly declared |
| `Project Type` | Project classification | Shared human-managed or explicitly declared |
| `Git Origin` | Provider/category for the repository origin | Repository/provider observation |
| `Repository URL` | Approved repository URL | Repository/provider observation |
| `Programming Languages` | Supported languages detected or declared | Scanner-generated, with provenance |
| `Frameworks & Technologies` | Normalized technology summary | Scanner-generated, with provenance |
| `Lifecycle Status` | Portfolio lifecycle state | Ownership to be finalized |
| `Tracking Level` | Portfolio tracking classification | Shared human-managed |
| `Last Scanned` | Last successful relevant scan time | Scanner-generated |
| `Details Status` | Completeness or review state | Derived or shared, according to the final definition |

The exact allowed values for `Domain`, `Project Type`, `Lifecycle Status`, `Tracking Level`, and `Details Status` must be documented and validated.

The shared registry must not imply that a remote repository was successfully inspected merely because a repository URL is present.

### 4.2 Tab 2 — `Documentation & Standards`

One row represents the documentation and standards summary for a logical project.

| Field | Description | Proposed ownership |
|---|---|---|
| `Project ID` | Stable logical project ID | Identity system |
| `README Present` | Whether a supported inspection detected a README | Scanner-generated |
| `README Quality` | Result of an approved deterministic checklist, or not assessed | Derived assessment |
| `Documentation Present` | Whether supported documentation indicators were detected | Scanner-generated |
| `Documentation Structure` | Summary of recognized documentation structure | Scanner-generated |
| `OpenSpec Enabled` | Whether supported OpenSpec indicators were detected | Scanner-generated |
| `OpenSpec Configuration` | Configuration detection and validation summary | Scanner-generated |
| `OKF Enabled` | Whether a declared, supported OKF bundle was detected; non-conforming bundles shown as such | Scanner-generated |
| `Agent Instructions` | Summary of recognized instruction files | Scanner-generated |
| `Tests Present` | Whether supported test indicators were detected | Scanner-generated |
| `Documentation Entry Point` | Repository-relative documentation entry point, if known | Scanner-generated |

This tab must preserve the difference between absence and incomplete assessment.

For example, if the repository was inaccessible during a scan, `README Present` must not be overwritten with `false`.

**Excluded fields:** `CI/CD Present` and `Standards Review` are not part of the initial schema.

They must not be reintroduced without an explicit requirements change.

### 4.3 Tab 3 — `Scan History`

One row represents a synchronization-relevant scan or registry operation.

| Field | Description |
|---|---|
| `Run ID` | Stable identifier for the run |
| `Timestamp` | Run timestamp |
| `Scan Scope` | Scope of the operation |
| `Projects Discovered` | Number of projects discovered |
| `Projects Added/Updated` | Number of records added or updated |
| `Projects Requiring Review` | Number of records requiring human review |
| `Skipped Projects` | Number of projects skipped |
| `Errors` | Count or concise summary of errors |
| `Synchronization Result` | Outcome of synchronization |

`Scan History` is a shared summary, not a replacement for the detailed local scan history in SQLite.

The implementation must define whether a row records a scan, a synchronization, or a combined workflow. The selected meaning must remain consistent across all producers.

### 4.4 Sheet Schema Version

The spreadsheet should have a documented schema version, preferably in controlled metadata such as a designated configuration cell or developer-managed schema record.

The adapter must validate the expected tabs, headers, and version before writing.

It must not silently create a different schema or reinterpret unknown columns.

---

## 5. Field Ownership and Direction

### 5.1 Ownership Categories

The synchronization planner must classify every exported or imported field into an ownership category.

| Category | Authoritative source | Typical direction |
|---|---|---|
| Repository-owned | Canonical project profile or repository source | Repository observation to local index; approved summary to Sheets |
| Scanner-generated | Deterministic scanner | Local index to Sheets |
| Shared human-managed | Google Sheets registry | Sheets to local cache |
| Machine-local | Current device | Local only |
| Provider-owned | Git provider | Provider observation to local index; approved summary to Sheets |
| Derived | Documented deterministic rule | Recomputed from eligible source data |
| Unresolved | Conflicting or insufficient evidence | No automatic overwrite |

The final field-by-field mapping must be maintained as a versioned export/import specification.

### 5.2 Scanner-Generated Fields

Scanner-generated fields include supported observations such as:

- Detected programming languages.
- Detected technologies.
- README presence.
- Documentation indicators.
- OpenSpec detection.
- Agent instruction indicators.
- Test indicators.
- Last successful scan timestamp.

These fields may be published to Sheets only through the approved export mapping.

They must not overwrite unrelated human-managed fields.

### 5.3 Shared Human-Managed Fields

Examples include:

- Tracking level.
- Portfolio notes, if added through an approved schema change.
- Portfolio priority, if added through an approved schema change.
- Business domain, when maintained centrally.
- Project classification, when maintained centrally.

A device that pulls these fields must preserve them in its local cache without changing their ownership.

If a scanner produces a value that conflicts with a shared human-managed value, the system must apply the agreed field policy rather than automatically replacing either value.

### 5.4 Mixed-Ownership Fields

Some fields may have multiple potential sources.

For example, a project name may be declared in the canonical profile, derived from a manifest, or edited in the shared registry.

Before implementation, the ownership specification must decide whether the field is repository-owned, shared human-managed, or resolved by a specific precedence rule.

The synchronizer must not treat a mixed-ownership field as a generic last-write-wins value.

### 5.5 No Universal Last-Write-Wins

A newer timestamp does not automatically establish authority.

A later local scan may provide fresh evidence for a scanner-owned field, while a later spreadsheet edit may be authoritative for a human-managed field.

Conflict resolution must be based on ownership, not timestamp alone.

---

## 6. Stable Identity and Record Matching

### 6.1 Project ID

Every logical project must have a stable `Project ID`.

The ID is the primary key for matching shared project records across devices.

Project names, repository directory names, and local paths must not be used as the sole matching key.

### 6.2 Identity Creation

When a local project is first discovered:

1. Resolve its identity using the approved identity algorithm.
2. Check for an existing local logical project.
3. Check the shared registry for the same stable project ID.
4. If identity is unambiguous, associate the local observation with the existing project.
5. If identity is ambiguous, preserve the candidate and require review.

The exact project ID generation and reconciliation algorithm must be defined in `identity-and-resolution.md`.

### 6.3 Existing Registry Records

If the same `Project ID` already exists in Sheets, synchronization updates the approved fields for that record rather than creating a second row.

A duplicate project name with a different ID must not be automatically merged.

### 6.4 Multiple Repositories

A logical project may contain multiple repositories.

The initial registry schema has one `Repository URL` field per project, so the ownership and representation policy must define which repository is shown.

If multiple repositories need independent registry records, the spreadsheet schema will require a dedicated repositories tab or another approved representation.

The synchronizer must not silently concatenate multiple repository identities into one field and treat the result as a canonical identity.

### 6.5 Projects Without Git Remotes

A project without a remote may still be included in the shared registry if its identity is stable and the owner permits sharing.

It must not receive a fabricated repository URL.

The identity policy must define how such projects remain recognizable across devices.
