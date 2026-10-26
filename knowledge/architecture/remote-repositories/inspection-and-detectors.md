---
type: Architecture
title: "Remote Repository Discovery: Remote File Inspection and Detectors"
description: Which files are read through APIs and how the deterministic detectors apply to them.
tags: [github, bitbucket, phase-3]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/remote-repositories.md
    title: Remote Repository Discovery
---

# Remote Repository Discovery: Remote File Inspection and Detectors

*Sections 9–10 of [Remote Repository Discovery](/architecture/remote-repositories.md).*

## 9. Remote File Inspection

### 9.1 Purpose

Remote file inspection retrieves selected files needed by supported detectors.

It should reuse the deterministic detector framework defined in `scanning-and-evidence.md`.

The remote inspector must not create a checkout.

### 9.2 Initial File Categories

The initial inspection inventory may include:

- README files.
- Canonical project profiles.
- Supported project manifests.
- Recognized build configuration.
- Documentation entry points.
- OpenSpec configuration and selected artifacts.
- Recognized agent instruction files.
- Test configuration and test indicators.

The exact patterns must be maintained in the detector inventory.

### 9.3 Inspection Levels

The implementation should distinguish these levels:

1. **Repository discovery:** repository metadata only.
2. **File inventory discovery:** determine which relevant paths exist, using supported provider APIs.
3. **Selected file inspection:** retrieve content for approved detector inputs.
4. **Metadata extraction:** run deterministic detectors on retrieved content.

These levels must not be conflated.

A discovered repository may have no file inspection. A file inventory may exist without every relevant file being read.

### 9.4 File Retrieval

The provider adapter should use supported APIs to retrieve files from a specified repository revision.

It must:

- Prefer a specific revision when available.
- Respect configured file-size limits.
- Handle binary or unsupported content safely.
- Avoid retrieving unrelated files.
- Avoid executing scripts or interpreting arbitrary repository content as Vyasa configuration.
- Record when a file could not be retrieved.

### 9.5 Revision Consistency

Files inspected during one logical inspection should use a consistent revision where the provider API permits it.

For example, if the inspector retrieves a README from one commit and a manifest from a newer commit, it must not imply that both observations describe the same repository state.

The preferred approach is to resolve a revision and request selected files against that revision.

If the provider does not support the required consistency, record the limitation.

### 9.6 No Clone or Checkout

The implementation must not use a temporary clone as a fallback for unsupported API calls.

If the API cannot retrieve a required file or revision, Vyasa should report the capability limitation or inspection failure.

### 9.7 Content Retention

The remote inspector should process retrieved content in memory and persist only the metadata and evidence needed for indexing.

Raw repository files should not be stored in SQLite by default.

If future performance requirements justify a content cache, it must have explicit size limits, retention rules, privacy controls, and invalidation behaviour.

---

## 10. Remote Deterministic Detection

### 10.1 Shared Detector Framework

Where a detector accepts a file's content and path, the same detector logic should be reused for local and remote sources.

Provider-specific logic should be limited to:

- Discovering relevant paths.
- Retrieving content.
- Mapping revision and source metadata.
- Reporting provider access failures.

This avoids separate rules for interpreting identical manifests based solely on where they were read.

### 10.2 Provenance

Every remote observation should identify:

- Provider.
- Provider repository identity.
- Repository-relative path or metadata field.
- Revision or commit identifier, when available.
- Detector identifier and version.
- Observation timestamp.
- Inspection outcome.

A remote observation must never be presented as evidence from a local checkout.

### 10.3 Source Status

The inspector must preserve the distinction between:

- `observed`
- `declared`
- `not_detected`
- `unknown`
- `unsupported`
- `inaccessible`
- `stale`
- `conflicting`

For example, a README request returning a confirmed not-found result at a successfully inspected revision can support `not_detected`. An authorization error cannot.

### 10.4 Unsupported Formats

If a repository uses an unsupported manifest or configuration format, the result should identify the limitation.

It must not guess framework dependencies or architecture from filenames alone.

### 10.5 OpenSpec and OKF

OpenSpec detection must follow the same versioned validation rules as local scanning.

OKF detection follows the local rules in [Scanning and Evidence §9.11](/architecture/scanning-and-evidence.md), applied to files retrieved at a pinned revision: only `index.md` files and concept frontmatter are fetched, within the remote inspection limits.
