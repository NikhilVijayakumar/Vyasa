---
type: Technology
title: "GitHub and Bitbucket Cloud APIs"
description: How the two providers paginate, rate-limit, authenticate, and expose file contents, and what to verify before building against them.
tags: [github, bitbucket, rest, pagination, rate-limits]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
stale_after: 2027-01-26T00:00:00Z
sources:
  - id: rr
    resource: /architecture/remote-repositories.md
    title: Remote Repositories
  - id: cfg
    resource: /architecture/remote-repositories/config-and-auth.md
    title: Configuration, Scope, and Authentication
---

# Common shape

Both expose REST APIs that list repositories within an account, organization, or workspace and return file contents at a
ref. Neither requires cloning.[^rr]

# GitHub

- **Pagination.** Lists return a `Link` header whose `rel="next"` points to the next page; follow it until absent.
- **Rate limits.** Responses carry remaining-quota and reset headers; secondary limits may ask the client to wait. Honour
  both.
- **Authentication.** Fine-grained personal access tokens can be limited to selected repositories with read-only
  permissions such as metadata and contents.
- **Files.** The contents API returns a blob identifier for each file; the commit identifier of a branch head pins a set
  of reads to one revision.

# Bitbucket Cloud

- **Pagination.** Responses include a `next` URL and a page length; follow `next` until absent.
- **Authentication.** The provider is moving from app passwords to API tokens and access tokens. Confirm the current
  supported model before building.
- **Scope.** Lists are organized by workspace.

# Design consequences

- Treat a failed or rate-limited page as an incomplete listing, never as the absence of the repositories after it.
- Map each provider's errors to a small set of domain errors: authentication failure, not found, rate limited,
  transient.
- Keep tokens in a credential store; they never appear in configuration, the index, or logs.[^cfg]

# Related

- [Remote Repositories](/architecture/remote-repositories.md)
- [Remote Discovery Views](/architecture/views/remote-views.md)

[^rr]: Remote Repositories
[^cfg]: Configuration, Scope, and Authentication
