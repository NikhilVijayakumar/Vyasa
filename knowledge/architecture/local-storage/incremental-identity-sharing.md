---
type: Architecture
title: "Local Storage: Incremental State, Identity, and Local-Only Data"
description: What incremental scanning stores, deduplication, and the line between local and shareable data.
tags: [sqlite, storage, index]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/local-storage.md
    title: Local Storage
---

# Local Storage: Incremental State, Identity, and Local-Only Data

*Sections 10–12 of [Local Storage](/architecture/local-storage.md).*

## 10. Incremental Scanning State

### 10.1 Purpose

Incremental scanning avoids unnecessary reprocessing while preserving correct results.

The database must retain enough information to determine whether cached detector output is reusable.

### 10.2 Cache Dependencies

Cache validity may depend on:

- File path and content fingerprint.
- Detector ID and version.
- Detector configuration.
- Relevant profile schema.
- Repository identity.
- Source revision.
- Relevant discovery configuration.

A detector must declare the inputs that can affect its output.

### 10.3 Invalidation

Invalidate or re-evaluate observations when:

- A relevant file changes.
- A relevant file is added or deleted.
- A previously inaccessible file becomes readable.
- A detector version changes.
- A profile schema changes.
- Repository identity changes.
- A scan was incomplete.
- Configuration changes affect detector behaviour.

### 10.4 Stale Observations

When an observation becomes stale, Vyasa may preserve the last known value for diagnostic or fallback purposes, but it must mark it stale and must not present it as freshly verified.

The public query interface must make stale state visible.

### 10.5 Cache Rebuild

The index must support rebuilding generated observations and projections.

A rebuild must not overwrite canonical project profiles or shared human-managed fields.

Historical scan records may be retained according to the approved retention policy, even when current observations are regenerated.

---

## 11. Identity and Deduplication Constraints

### 11.1 Project Identity

The database must enforce uniqueness for stable project IDs.

Project display names need not be unique.

### 11.2 Repository Identity

Repository uniqueness should use an approved normalized identity strategy, considering provider identity when available.

Remote URLs can change, and one logical repository may have multiple URL forms. The implementation must not assume that URL text alone is always a permanent identity.

### 11.3 Checkout Identity

A local checkout must be associated with a repository through repository identity where possible.

The same repository may have more than one checkout.

### 11.4 Duplicate Candidates

Potential duplicates should be represented as candidate relationships until the identity-resolution policy has sufficient evidence.

Storage constraints must prevent duplicate records where identity is established, without preventing legitimate forks, mirrors, or multiple repositories belonging to one project.

### 11.5 Missing Projects

If a project is no longer found during a complete local scan, the database may update its local visibility or discovery status.

It must not automatically delete the logical project, erase its shared record, or classify it as obsolete solely because it was not found in one workspace scan.

---

## 12. Local-Only and Shareable Data

The storage model must make data boundaries explicit.

| Data | Local SQLite | Google Sheets | Notes |
|---|---|---|---|
| Stable logical project ID | Yes | Yes, approved form | Shared identity |
| Project display name | Yes | Yes | Subject to ownership rules |
| Project purpose | Yes | If approved | Preserve source ownership |
| Languages and technologies | Yes | Approved summary | Evidence remains local unless explicitly designed otherwise |
| Documentation indicators | Yes | Approved summary | Include last verified time |
| Local checkout path | Yes | No | Machine-specific |
| Workspace root | Yes | No | Machine-specific |
| Database path | Yes | No | Machine-specific |
| File fingerprints | Yes | Normally no | Local scan state |
| Evidence references | Yes | Normally summary only | Avoid local paths |
| Scan history | Yes | Aggregated history only, if needed | Separate local and sync events |
| Human portfolio fields | Local cache as applicable | Yes | Preserve shared ownership |
| API credentials | Secure local configuration | No | Never export |
| Raw repository contents | No by default | No | Avoid unnecessary retention |
| Remote provider identity | Yes | Approved identifiers | Provider-specific |
| Draft profile state | Local only | No | Never automatically promoted |

The final export policy must use an explicit allowlist. It must not export every column merely because it exists in SQLite.
