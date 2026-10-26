---
type: Architecture
title: "Data Model: Local Checkout and External Identity"
description: Where a repository lives on a device, and how identities from other systems attach.
tags: [data-model, index, evidence]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/data-model.md
    title: Data Model
---

# Data Model: Local Checkout and External Identity

*Sections 7–8 of [Data Model](/architecture/data-model.md).*

## 7. Local Checkout Entity

### 7.1 Purpose

A Local Checkout represents a repository instance accessible from the current device.

This entity is necessary because the same repository may be checked out more than once or stored at different locations across devices.

### 7.2 Logical Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `checkout_id` | String | Yes | Stable identifier for this local checkout mapping. |
| `repository_id` | String | Yes | Associated repository. |
| `local_path` | Path | Yes | Absolute path on the current device. |
| `workspace_root_id` | String | No | Configured workspace root containing the checkout. |
| `checkout_status` | Enum | Yes | Current local accessibility state. |
| `last_scan_run_id` | String | No | Most recent scan run that examined this checkout. |
| `last_successful_scan_at` | Timestamp | No | Time of its most recent successful scan. |
| `observed_revision` | String or unknown | No | Locally observed commit identifier when available. |
| `created_at` | Timestamp | Yes | Time first registered locally. |
| `updated_at` | Timestamp | Yes | Time the local mapping was last updated. |

### 7.3 Checkout Status

Proposed values:

- `available`
- `inaccessible`
- `missing`
- `unknown`

A missing checkout path must not cause its logical project or repository record to be deleted automatically.

### 7.4 Privacy Rule

`local_path`, workspace roots, and machine-specific checkout mappings are strictly local by default.

They must never be included in Google Sheets exports or shared registry records.

---

## 8. External Identity Entity

### 8.1 Purpose

External Identity associates a project or repository with identifiers maintained by another system.

Examples include:

- GitHub repository ID.
- Bitbucket Cloud repository UUID.
- A normalized remote repository identity.
- A future external project identifier.

### 8.2 Logical Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `external_identity_id` | String | Yes | Internal identifier for the external identity record. |
| `entity_type` | Enum | Yes | Project or repository. |
| `entity_id` | String | Yes | Associated internal project or repository ID. |
| `provider` | String | Yes | External system or identity namespace. |
| `external_id` | String | Yes | Identifier assigned by that system. |
| `normalized_value` | String or unknown | No | Normalized URL or other comparable identity value. |
| `verified_at` | Timestamp | No | Last successful verification time. |
| `verification_status` | Enum | Yes | Verified, unverified, stale, or unavailable. |

The implementation must enforce uniqueness within the relevant provider and identity namespace.

### 8.3 Identity Rules

1. Prefer stable provider identifiers when available and verified.
2. Use normalized remote identities when no stronger identity exists.
3. Use a deterministic local fallback when no reliable remote identity exists.
4. Keep identity separate from mutable display names and filesystem paths.
5. Treat forks, mirrors, renamed repositories, and ambiguous matches according to explicit policies.
6. Never merge records solely because their names match.
7. Preserve an audit trail when identity mappings change.

### 8.4 Stable Identifier Strategy

The exact project ID and repository ID generation algorithm remains an implementation decision.

The selected strategy must meet these requirements:

- Repeated processing of the same established identity returns the same ID.
- Local directory renames do not automatically create new logical projects.
- IDs are safe for storage and use in MCP requests.
- Collisions are detected and handled.
- Identity changes are explicit and recoverable.

A hash of a normalized identity is one possible implementation, but the normalization rules and treatment of identity changes must be settled first.
