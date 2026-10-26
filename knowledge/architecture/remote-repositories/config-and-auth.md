---
type: Architecture
title: "Remote Repository Discovery: Configuration, Scope, and Authentication"
description: How scopes are configured and how provider credentials are handled.
tags: [github, bitbucket, phase-3]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/remote-repositories.md
    title: Remote Repository Discovery
---

# Remote Repository Discovery: Configuration, Scope, and Authentication

*Sections 5–6 of [Remote Repository Discovery](/architecture/remote-repositories.md).*

## 5. Configuration and Discovery Scope

### 5.1 Explicit Provider Configuration

Each provider connection should specify:

- Provider type.
- Enabled or disabled state.
- Authentication reference.
- Discovery scope.
- Optional organization or workspace identifiers.
- Repository inclusion and exclusion rules.
- Maximum discovery or inspection limits, if configured.
- Refresh policy.
- Applicable timeout and retry settings.

The application must not silently enumerate every account or organization accessible to a credential when the configured scope is narrower.

### 5.2 GitHub Scope

The initial implementation should support explicitly configured discovery scopes, such as:

- Authenticated user's accessible repositories.
- Selected organizations.
- Selected repository owners.
- Selected repository URLs or identifiers.

The exact scopes depend on the authenticated API and the permissions granted to the connection.

An organization being configured does not guarantee access to every repository within it.

### 5.3 Bitbucket Cloud Scope

The initial implementation should support explicitly configured workspace scopes.

The adapter must distinguish:

- A configured workspace.
- A workspace that is successfully accessible.
- A workspace whose access is denied.
- A workspace whose repository enumeration is incomplete.

A failed workspace request must not be interpreted as an empty workspace.

### 5.4 Inclusion and Exclusion

Repository inclusion and exclusion rules should be evaluated against normalized provider identity and configured metadata.

Examples include:

- Include selected organizations.
- Exclude archived repositories from routine inspection while retaining their discovery records.
- Exclude selected repository names or identifiers.
- Inspect metadata only for repositories belonging to a configured portfolio.

The exact supported matching syntax must be documented. Arbitrary expressions must not be evaluated as executable configuration.

### 5.5 Discovery Run Scope

Every discovery run must record its intended scope.

A run scoped to one organization must not be presented as a complete account-wide discovery.

The system must report which scopes were successfully enumerated, skipped, or inaccessible.

---

## 6. Authentication and Credentials

### 6.1 Credential Strategy

The adapter must use supported provider authentication mechanisms.

For GitHub, the implementation may use an appropriately scoped token or supported application-based authentication.

For Bitbucket Cloud, the implementation must select an authentication mechanism currently supported for the intended account and repository access pattern, with appropriate read permissions.

The exact mechanism must be verified during implementation rather than assuming that one provider's token model applies to the other.

### 6.2 Least Privilege

Credentials should have the minimum permissions needed for the configured operation.

For read-only discovery and file inspection, write access to repository contents is unnecessary.

If organization or workspace enumeration requires additional permissions, those permissions must be documented separately from basic repository-read access.

### 6.3 Credential Storage

Credentials must be stored outside repositories and Google Sheets.

Preferred storage options are:

- Operating-system secret storage where available.
- A protected local credential configuration.
- An approved secret-management integration.

Credentials must not be stored in:

- Project profiles.
- SQLite project metadata.
- Evidence records.
- MCP responses.
- Shared registry cells.
- Debug logs.

If a credential is unavailable or expired, the provider adapter must return an authentication status without exposing the secret.

### 6.4 Authentication Failure

Authentication failures must be distinguishable from repository absence.

For example, if a token expires, Vyasa must not mark all previously discovered private repositories as deleted.

The last known repository records may be retained with an appropriate access or freshness status.

### 6.5 Credential Rotation

Credential replacement must not change repository identity.

The adapter should allow a connection to be reauthenticated without recreating all provider repository records.
