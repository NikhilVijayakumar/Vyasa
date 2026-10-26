---
type: Architecture
title: "Remote Repository Discovery: Incremental Discovery, Limits, and Untrusted Content"
description: Caching and refresh, rate limits and failures, and handling untrusted remote content.
tags: [github, bitbucket, phase-3]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/remote-repositories.md
    title: Remote Repository Discovery
---

# Remote Repository Discovery: Incremental Discovery, Limits, and Untrusted Content

*Sections 15–17 of [Remote Repository Discovery](/architecture/remote-repositories.md).*

## 15. Incremental Discovery and Caching

### 15.1 Objectives

Incremental discovery should minimize unnecessary API calls while keeping the index accurate.

It must not trade correctness for a misleading claim of freshness.

### 15.2 Repository-Level Cache

Cache relevant repository metadata such as:

- Provider repository ID.
- Last observed metadata.
- Default branch.
- Latest known revision.
- Last successful discovery time.
- Last error state.

The adapter should refresh fields according to a documented freshness policy.

### 15.3 File-Level Cache

A remote file inspection cache may be reused when all relevant inputs remain unchanged:

- Provider repository identity.
- Target revision.
- File path.
- File content fingerprint or equivalent reliable revision reference.
- Detector version.
- Detector configuration.

A cache hit must not be reused if the detector version or supported schema rules have changed.

### 15.4 Branch Changes

When the default branch advances, the inspector should determine which observations need refreshing.

If the provider supplies a commit identifier, use it to establish the source revision.

Do not assume that a stable branch name means stable content.

### 15.5 Deleted Files

A previously detected file may be considered absent only when the provider successfully establishes that the file is not present at the inspected revision.

An authorization failure or incomplete API request must not invalidate the previous positive observation as a confirmed deletion.

### 15.6 Repository Changes

If the repository is renamed or transferred, update mutable metadata associated with the stable provider identity.

If the repository is archived, preserve its record and update its observed status.

### 15.7 Refresh Policy

The implementation should support explicit refresh operations and may add scheduled discovery later.

The initial implementation should not require continuous polling.

The freshness interval, refresh scope, and treatment of archived repositories must be configurable or documented.

---

## 16. API Rate Limits and Failure Handling

### 16.1 Rate Limits

Each provider adapter must follow its provider's current rate-limit and retry guidance.

The implementation must not assume identical quotas or rate-limit headers across GitHub and Bitbucket Cloud.

### 16.2 Retryable Errors

Potentially retryable failures include:

- Temporary network failures.
- Provider service errors.
- Rate limiting.
- Transient request timeouts.

Retries must be bounded and use appropriate backoff.

### 16.3 Non-Retryable Errors

Examples include:

- Invalid credentials.
- Insufficient permissions.
- Invalid repository identifiers.
- Unsupported API operations.
- Invalid configuration.

These require corrective action rather than indefinite retries.

### 16.4 Partial Discovery

If some repositories are discovered but later pages fail:

- Retain confirmed discoveries.
- Record the run as partial.
- Preserve previous repository records.
- Mark discovery coverage as incomplete.
- Retry the missing scope when safe.

### 16.5 Access Revocation

If a previously accessible repository becomes inaccessible, preserve its last known metadata and update its access or freshness status.

Do not automatically delete it or erase its project association.

### 16.6 Provider Outage

A provider outage must not prevent local scanning or local MCP queries.

The last valid remote observations may remain available, marked with appropriate freshness warnings.

---

## 17. Security and Untrusted Repository Content

### 17.1 No Repository Execution

Remote discovery must not execute repository scripts, workflows, build files, package lifecycle hooks, or agent instructions.

All retrieved repository content is treated as untrusted data.

### 17.2 Resource Limits

The implementation must enforce limits on:

- API request duration.
- Retrieved file size.
- Total files inspected per repository.
- Total repositories processed per run, where configured.
- Memory use during parsing.
- Retry counts.
- Total run duration, where applicable.

Exceeding a limit must produce an explicit skipped or incomplete result.

### 17.3 Secret Redaction

The adapter must sanitize remote URLs that embed credentials or tokens.

Error responses must not include authentication headers or raw secret-bearing request details.

### 17.4 Permission Boundaries

The adapter must only access repositories authorized by the configured credentials and scope.

It must not attempt to bypass repository access restrictions or use an alternate identity to circumvent denied access.

### 17.5 Minimal Data Collection

Only metadata needed for discovery, indexing, and approved evidence should be retained.

The implementation must not download entire repositories simply to determine basic project identity or technology.

### 17.6 Provider Data Exposure

Remote repository metadata returned through MCP must be limited to the configured user and authorized scope.

The system must not treat data obtained through one provider connection as globally available to every unrelated user or deployment.
