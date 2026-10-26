---
type: Decision
title: "Credential Storage and Registry Identity"
description: Credentials live in the operating system's credential store, and the shared registry is accessed by a service account by default.
tags: [adr, credentials, google-sheets, security]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: sec
    resource: /architecture/security-and-privacy/mcp-and-credentials.md
    title: MCP Security and Credential Management
  - id: gs
    resource: /technologies/google-sheets-api.md
    title: Google Sheets API for the Registry
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Phases 2 and 3 need secrets for Google and for repository providers. Secrets must never sit in configuration, the index, logs, or repositories, and access should be as narrow as the platform allows.

# Decision

Store credentials through the platform credential store, installed as an optional extra; allow environment variables as a controlled fallback that is never logged; allow a user-only file outside any repository only by explicit choice. For the shared registry, default to a service account with the one spreadsheet shared to it; offer an installed-application OAuth flow for individuals. Request the narrowest provider scopes (read-only on selected repositories).

# Alternatives considered

- **Credentials in the configuration file.** Easy, but leaks through backups and commits.
- **Broad personal OAuth scopes.** Convenient, but over-permissive.

# Consequences

- The credential library is optional and absent from phase 1.
- Each provider's current token model must be verified when integrating.
- Revocation and rotation are runbook-driven.

# Related

- [Suspected Credential Leak](/runbooks/credential-leak.md)
- [GitHub and Bitbucket APIs](/technologies/github-and-bitbucket-apis.md)
