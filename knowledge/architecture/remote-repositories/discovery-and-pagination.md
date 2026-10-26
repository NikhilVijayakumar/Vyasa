---
type: Architecture
title: "Remote Repository Discovery: Repository Discovery and Pagination"
description: How repositories are enumerated and how pages and partial coverage are tracked.
tags: [github, bitbucket, phase-3]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/remote-repositories.md
    title: Remote Repository Discovery
---

# Remote Repository Discovery: Repository Discovery and Pagination

*Sections 7–8 of [Remote Repository Discovery](/architecture/remote-repositories.md).*

## 7. Repository Discovery

### 7.1 Discovery Process

The discovery workflow is:

1. Load and validate provider configuration.
2. Validate the configured credential.
3. Resolve the configured discovery scope.
4. Enumerate repositories using provider pagination.
5. Normalize repository metadata.
6. Identify each repository using provider identity.
7. Compare discovered repositories with the existing index.
8. Record new, changed, unchanged, and inaccessible records.
9. Optionally inspect selected metadata files.
10. Record run completion and coverage.

Repository discovery and file inspection may be separate operations. The implementation must make their statuses distinguishable.

### 7.2 Minimum Repository Metadata

Where provided by the API, the normalized record should include:

- Provider type.
- Provider repository ID.
- Repository name.
- Repository owner or workspace.
- Canonical web URL.
- Clone URL, if useful for identification, without using it to clone.
- Default branch.
- Visibility.
- Archived status.
- Fork or mirror indicators, where available.
- Creation and update timestamps, where available.
- Latest observed commit or default-branch revision, where available.
- Last successful discovery time.

Fields that are not available from the provider must remain unknown rather than being inferred.

### 7.3 Stable Provider Identity

Each remote repository should have a provider-scoped identity.

Conceptually:

`provider + provider_repository_id`

The provider's stable repository identifier is preferred over repository name or URL text.

URLs may change because repositories are renamed or transferred. Vyasa should update the URL associated with a stable provider identity without treating the repository as an unrelated new entity.

### 7.4 New Repositories

A newly discovered remote repository should be recorded independently of whether it can be associated with an existing logical project.

If identity resolution cannot establish a match, the repository should remain a remote repository record awaiting association or review.

### 7.5 Renamed or Transferred Repositories

When the provider returns a known stable repository ID with a new name or owner:

- Preserve the provider repository identity.
- Update observed mutable metadata.
- Retain relevant historical observations if required.
- Re-evaluate the logical project association if the transfer changes ownership or identity evidence.
- Do not automatically merge the repository with another project merely because its name changed.

### 7.6 Archived Repositories

Archived repositories may remain valuable for project history and reuse.

The system must preserve their discovery record and expose their archived status.

Whether archived repositories are inspected during every refresh should be configurable or defined by the discovery policy.

### 7.7 Deleted or Inaccessible Repositories

If a previously discovered repository disappears from an API response, Vyasa must not immediately conclude that it was deleted.

Possible explanations include:

- Repository deletion.
- Permission changes.
- Authentication failure.
- Organization membership changes.
- Discovery-scope changes.
- Incomplete pagination.
- Temporary provider failure.

The implementation must distinguish confirmed deletion, inaccessible repository, and not observed in the latest completed scope where the provider can supply sufficient evidence.

If deletion cannot be established reliably, preserve the record and mark its state or freshness appropriately.

---

## 8. Pagination and Discovery Completeness

### 8.1 Complete Enumeration

A repository discovery run is complete only when all pages required for its declared scope have been processed successfully.

If a page fails after earlier pages succeeded, the run must report partial completion.

### 8.2 Pagination Strategy

Each provider adapter must follow the provider's documented pagination mechanism.

The adapter must not assume identical page sizes, cursor formats, continuation URLs, or response structures across providers.

### 8.3 Duplicate Results

Some provider responses may overlap due to changing repository lists or pagination behaviour.

Duplicate provider repository IDs within a discovery run must be deduplicated deterministically.

The same repository must not be inserted twice merely because it appeared in multiple responses.

### 8.4 Changing Repository Lists

A repository list may change during enumeration.

Where possible, the adapter should use stable pagination mechanisms and provider revisions or continuation tokens.

If the API cannot guarantee a snapshot, Vyasa must document that limitation and avoid claiming a globally atomic view of the repository inventory.

### 8.5 Partial Scope

If only some configured organizations or workspaces were inspected successfully, the discovery result must include per-scope outcomes.

The aggregate run must not be reported as fully complete.
