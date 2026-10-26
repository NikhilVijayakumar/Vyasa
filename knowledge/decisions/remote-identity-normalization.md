---
type: Decision
title: "Remote Identity Normalization"
description: Remote URLs are reduced to host/organization/repository so equivalent forms compare equal.
tags: [adr, identity, git, normalization]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: id
    resource: /concepts/project-identity.md
    title: Project Identity
  - id: git
    resource: /technologies/git-metadata.md
    title: Reading Git Metadata Safely
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

The same repository appears as ssh and https URLs, with or without a `.git` suffix, sometimes with credentials embedded. Comparing raw strings would create duplicates and could persist secrets.

# Decision

Drop the scheme, user information, default port, a trailing `.git`, and a trailing slash; rewrite `git@host:org/repo` as `host/org/repo`. Lowercase the whole identity for hosts known to be case-insensitive (GitHub, Bitbucket Cloud) and keep path case elsewhere. Use the remote named `origin`; if absent and exactly one remote exists use it; otherwise the identity is provisional. Local paths and file URLs are not remote identities. The normalizer is a pure function.

# Alternatives considered

- **Compare raw URLs.** Duplicates and secrets.
- **Always lowercase.** Wrong for hosts with case-sensitive paths.

# Consequences

- Credentials never reach storage.
- Unusual remotes degrade to provisional identity instead of being guessed.
- A parametrized test table can pin every accepted form.

# Related

- [Stored Identity With Aliases](/decisions/stored-identity-with-aliases.md)
