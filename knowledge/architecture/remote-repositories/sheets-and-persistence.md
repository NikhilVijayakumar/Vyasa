---
type: Architecture
title: "Remote Repository Discovery: Sheets Integration and SQLite Persistence"
description: What remote data may reach the registry and how it is stored locally.
tags: [github, bitbucket, phase-3]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/remote-repositories.md
    title: Remote Repository Discovery
---

# Remote Repository Discovery: Sheets Integration and SQLite Persistence

*Sections 13–14 of [Remote Repository Discovery](/architecture/remote-repositories.md).*

## 13. Google Sheets Integration

Google Sheets remains the shared registry introduced in Phase 2.

Remote discovery must not create a second competing portfolio registry.

### 13.1 Exported Metadata

Approved remote repository metadata may be summarized in the existing registry fields, including:

- Repository URL.
- Git origin.
- Programming languages.
- Frameworks and technologies.
- Documentation indicators.
- Last scanned timestamp.
- Details status.

Only fields allowed by the export/import ownership matrix may be synchronized.

### 13.2 Multiple Repositories

The current `Project Registry` schema contains one `Repository URL` field.

If one logical project needs multiple independently tracked repositories, a dedicated `Repositories` tab may be required.

Before adding it, the implementation must establish whether the existing schema can represent the required relationship without ambiguity.

The system must not silently truncate a multi-repository association or use a single arbitrary URL as though it represented the entire project.

### 13.3 Registry Does Not Prove Current Remote State

A spreadsheet record may describe a repository that has since changed or become inaccessible.

The registry must preserve the last successful observation time and must not imply that the repository was freshly inspected merely because its metadata was synchronized.

### 13.4 Credentials

Provider credentials must never be exported to Google Sheets.

The registry may contain public repository URLs and approved metadata, but not authentication tokens or local credential references.

---

## 14. SQLite Persistence

Remote discovery should extend the local storage model rather than replacing it.

Proposed additional logical entities include:

- `provider_connections`
- `remote_discovery_runs`
- `remote_discovery_scope_results`
- `remote_repository_observations`
- `remote_file_observations`
- `provider_sync_state`

These are logical entities; the final implementation may normalize or combine tables as appropriate.

### 14.1 Provider Connection

Store non-secret connection metadata such as:

- Connection identifier.
- Provider type.
- Configured scope.
- Enabled state.
- Last successful access time.
- Last error category.

Do not store raw credentials in these records.

### 14.2 Remote Discovery Run

Record:

- Run ID.
- Provider.
- Scope.
- Start and completion timestamps.
- Status.
- Pagination completeness.
- Repositories discovered.
- Repositories added or updated.
- Repositories skipped.
- Errors and warnings.

### 14.3 Remote Observations

Remote metadata observations must record source type and revision.

They must not be merged into local observations without preserving provenance.

### 14.4 Cache State

Cache records should identify the repository revision, file fingerprint, and detector version used to produce a result.

The cache must be invalidated when relevant source revisions, file content, or detector behaviour change.

### 14.5 Migration

Adding remote discovery state requires a versioned SQLite migration.

Existing local projects, observations, evidence, and scan history must remain valid after the migration.
