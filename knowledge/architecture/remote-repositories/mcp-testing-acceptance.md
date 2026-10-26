---
type: Architecture
title: "Remote Repository Discovery: MCP Interface, Testing, and Acceptance"
description: Remote operations in MCP, test strategy, implementation sequence, decisions, and acceptance.
tags: [github, bitbucket, phase-3]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/remote-repositories.md
    title: Remote Repository Discovery
---

# Remote Repository Discovery: MCP Interface, Testing, and Acceptance

*Sections 18–23 of [Remote Repository Discovery](/architecture/remote-repositories.md).*

## 18. MCP Interface

Remote discovery should extend the existing MCP contract without changing the semantics of the core query tools.

### 18.1 Existing Tools

The following tools should be able to return remote-derived information once it is indexed:

- `search_projects`
- `get_project`
- `get_project_context`
- `find_related_projects`
- `get_project_dependencies`
- `get_index_status`

They must identify source provenance and freshness where relevant.

### 18.2 Explicit Remote Operations

The following are proposed operational tools, subject to the final MCP interface decision:

- `discover_remote_repositories`
- `inspect_remote_repository`

`discover_remote_repositories` should accept a configured provider and supported scope, then return a bounded summary of discovery outcomes.

`inspect_remote_repository` should accept a stable repository identifier and a bounded inspection scope. It must not accept an arbitrary URL as permission to access any network resource.

The implementation must validate repository identity against configured providers and enforce access boundaries.

### 18.3 Discovery Input

The final discovery tool may accept:

- Provider connection ID.
- Configured scope identifier.
- Optional inclusion filters.
- Dry-run option, where useful.
- Explicit inspection mode.

It should not accept raw credentials or arbitrary API headers as tool arguments.

### 18.4 Inspection Input

The final inspection tool may accept:

- Stable repository ID.
- Optional target revision.
- Optional detector subset.
- Maximum inspection scope.

The repository must belong to an enabled, configured provider connection.

### 18.5 Results

Operational results should include:

- Run ID.
- Provider.
- Scope.
- Status.
- Repositories discovered or inspected.
- Records added or updated.
- Records skipped.
- Errors and warnings.
- Coverage and freshness.
- Whether inspection was complete.

### 18.6 No Implicit Remote Calls

Ordinary project queries must not unexpectedly call GitHub or Bitbucket APIs.

Remote discovery and inspection must be explicit operations or part of a separately configured scheduled workflow.

This keeps query latency predictable and avoids unexpected API usage.

---

## 19. Testing Strategy

### 19.1 Provider Adapter Unit Tests

Use mocked provider responses to test:

- Authentication outcomes.
- Repository normalization.
- Pagination.
- Duplicate repository IDs.
- Renamed repositories.
- Archived repositories.
- Missing metadata.
- Rate limits.
- Transient failures.
- Permission errors.

### 19.2 Remote Inspection Tests

Test:

- README retrieval.
- Manifest retrieval.
- Revision-pinned file inspection.
- Missing files.
- Unsupported formats.
- Oversized files.
- Binary files.
- Invalid content.
- Partial inspection.
- Cache reuse and invalidation.

### 19.3 Identity Tests

Test:

- Remote repository matching an existing local project.
- Remote-only project discovery.
- A local checkout matching a previously remote-only repository.
- Repository rename or transfer.
- Fork and upstream separation.
- Multiple repositories belonging to one logical project.
- Ambiguous matches and duplicate candidates.

### 19.4 Failure Isolation

Verify that:

- A failed provider does not prevent local queries.
- A failed organization does not invalidate other successfully inspected scopes.
- Partial pagination does not imply complete discovery.
- Authentication failure does not imply repository deletion.
- Remote inspection failure does not invalidate unrelated observations.

### 19.5 Security Tests

Verify that:

- Credentials are not persisted in metadata records.
- Secret-bearing URLs are sanitized.
- Remote content is never executed.
- Arbitrary URLs cannot bypass configured provider scope.
- Oversized responses are rejected safely.
- Untrusted repository text cannot alter scanner configuration.

### 19.6 Integration Tests

Use dedicated test repositories and scoped credentials.

Integration tests should verify repository enumeration, file inspection, revision tracking, provider errors, and safe reauthentication.

Tests must not depend on production repositories being permanently available.

---

## 20. Implementation Sequence

The recommended Phase 3 implementation order is:

1. Finalize provider identity and repository-to-project resolution rules.
2. Define the provider adapter interface.
3. Implement provider connection configuration and secret handling.
4. Implement GitHub repository discovery.
5. Implement Bitbucket Cloud repository discovery.
6. Add pagination and partial-discovery reporting.
7. Add remote repository persistence and SQLite migrations.
8. Implement selected-file retrieval at known revisions.
9. Reuse the existing deterministic detector framework.
10. Add remote evidence and freshness handling.
11. Implement incremental discovery and file inspection caches.
12. Integrate remote-only projects with the local query index.
13. Extend approved Google Sheets synchronization fields.
14. Add explicit MCP discovery and inspection operations.
15. Validate rate limits, permission boundaries, recovery, and cross-provider identity.
16. Test with repositories that have no local checkout.
17. Document setup and supported provider capabilities.

GitHub and Bitbucket Cloud should share the same domain-level contract, but their adapters should be implemented and tested independently.

---

## 21. Decisions Required Before Implementation

| ID | Decision | Recommendation |
|---|---|---|
| RR-001 | GitHub authentication mechanism | Use a supported least-privilege read-access model |
| RR-002 | Bitbucket Cloud authentication mechanism | Verify the current supported token and permission model |
| RR-003 | Discovery scope | Explicitly configure accounts, organizations, and workspaces |
| RR-004 | Provider identity | Use provider-scoped stable repository identifiers |
| RR-005 | Repository grouping | Support multiple repositories per logical project |
| RR-006 | Remote inspection defaults | Metadata-only discovery; inspect selected files explicitly |
| RR-007 | Revision consistency | Pin selected file inspections to a known revision where possible |
| RR-008 | Cache freshness policy | Define repository- and file-level refresh rules |
| RR-009 | Archived repositories | Preserve records; configure inspection policy |
| RR-010 | Missing repository policy | Preserve records unless deletion is established reliably |
| RR-011 | Remote-only project status | Distinguish remote discovery from local checkout |
| RR-012 | Multiple-repository Sheets representation | Decide whether a `Repositories` tab is required |
| RR-013 | MCP operational tools | Finalize discovery and inspection schemas |
| RR-014 | Remote request limits | Set and test file, repository, and duration limits |
| RR-015 | Provider rate limits | Implement provider-specific backoff and error handling |
| RR-016 | OKF detection | Resolved: Google Cloud OKF; reuse the local detector at a pinned revision (§10.5) |

These decisions must be resolved or explicitly accepted as implementation defaults before the corresponding functionality is built.

---

## 22. Acceptance Criteria

Remote repository discovery is ready when:

1. GitHub and Bitbucket Cloud repositories can be discovered through their supported APIs.
2. Authorized private repositories can be accessed within configured permissions.
3. Discovery respects configured provider and organization/workspace scopes.
4. Repository enumeration handles pagination and reports incomplete coverage accurately.
5. Stable provider identity prevents duplicate repository records during ordinary refreshes.
6. Remote file inspection works without cloning or checking out repositories.
7. Selected file inspections use revision-specific evidence where supported.
8. Remote observations remain distinguishable from local checkout observations.
9. Deterministic detectors are reused for compatible local and remote inputs.
10. Remote-only projects can be queried without inventing local paths.
11. Authentication failures and provider outages do not imply repository deletion.
12. Incremental discovery avoids unnecessary work while respecting detector and content invalidation.
13. Credentials remain outside the database's ordinary metadata records, MCP responses, and Google Sheets.
14. Repository content is never executed by the scanner.
15. Remote discovery failures do not break local indexing or querying.
16. Duplicate candidates and ambiguous project associations are surfaced for review.
17. The MCP interface exposes remote operations explicitly without making ordinary queries trigger API calls.
18. Provider-specific integration tests validate authentication, pagination, inspection, and recovery.

## 23. Governing Principle

Remote repository discovery extends Vyasa's visibility beyond the current machine without changing who owns project knowledge.

The provider remains authoritative for remote repository identity and state. The repository remains authoritative for its maintained content. SQLite remains the local index, and Google Sheets remains the shared project registry.

**Discover remotely, inspect selectively, preserve provenance, and never confuse remote visibility with a local checkout or complete verification.**

---

## Proposed resolutions

These are drafts, not approvals.

| Decision | Proposed in |
|---|---|
| RR-001, RR-002 authentication | [Credential Storage and Registry Identity](/decisions/credential-storage-and-sheets-identity.md) |
| RR-004 provider identity | [Stored Identity With Aliases](/decisions/stored-identity-with-aliases.md) |
| RR-009, RR-010 archived and missing repositories | [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md) |
| Provider libraries | [Optional Extras for Integrations](/decisions/optional-extras-for-integrations.md) |
