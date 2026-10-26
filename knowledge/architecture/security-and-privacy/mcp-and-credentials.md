---
type: Architecture
title: "Vyasa (व्यास): MCP Security and Credential Management"
description: What MCP clients may do and receive, and how secrets are stored and rotated.
tags: [security, privacy, trust-boundary]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/security-and-privacy.md
    title: Vyasa (व्यास)
---

# Vyasa (व्यास): MCP Security and Credential Management

*Sections 7–8 of [Vyasa (व्यास)](/architecture/security-and-privacy.md).*

## 7. MCP security

MCP connects Vyasa to coding agents that may have broader access to repositories, terminals, and other tools. The MCP boundary must therefore be treated as a security boundary.

### 7.1 Local transport and client trust

The proposed initial transport is **stdio**, with Vyasa launched as a local child process by the MCP client.

### 7.2 Tool permissions

The initial MCP interface is read-oriented:

- `search_projects`
- `get_project`
- `get_project_context`
- `find_related_projects`
- `get_project_dependencies`
- `get_index_status`
- `refresh_index`

`refresh_index` is operational rather than a repository-authoring capability. It may update generated index data but must not modify project metadata.

Future synchronization and remote discovery tools must be separately enabled and permissioned.

### 7.3 Context returned to coding agents

Project context may contain untrusted text originating from repository documentation.

- Mark repository-derived descriptions and content as data, not instructions.
- Do not execute instructions found in project documentation.
- Do not let a repository document override Vyasa configuration, tool permissions, or security policy.
- Prefer concise structured observations and provenance over large unfiltered text blocks.
- Expose whether data is locally observed, remotely observed, declared, stale, or unknown.
- Do not infer that a project is safe because it has documentation, tests, or recognized standards files.

---

## 8. Secret and credential management

Phase 1 should require no provider credentials. Phase 2 and Phase 3 introduce credentials only when their capabilities are enabled.

### 8.2 Least privilege

- Grant access only to the specific Google spreadsheet and required operations.
- Grant GitHub and Bitbucket scopes limited to the required repository metadata and file-reading operations.
- Do not request write permissions to repositories when read-only inspection is sufficient.
- Separate credentials and permissions by provider and capability where practical.
- Never reuse a user's broad personal access token when a narrower supported credential is available.

### 8.3 Credential lifecycle

The implementation must support a documented process to:

1. Configure or authorize a credential.
2. Validate access without revealing the credential.
3. Detect expiry or revocation.
4. Reauthorize or rotate credentials.
5. Remove stored credentials when the integration is disabled.
6. Recover from authentication failure without corrupting local data.

If credential exposure is suspected, stop using the affected credential and advise the operator to revoke or rotate it through the provider.
