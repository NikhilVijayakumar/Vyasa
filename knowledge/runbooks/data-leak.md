---
type: Runbook
title: "Suspected Data Leak"
description: What to do when project metadata or local information may have reached someone it should not have.
tags: [incident, privacy, response]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: sec
    resource: /architecture/security-and-privacy/operations-and-response.md
    title: Logging, Configuration, Incident Response, and References
  - id: cls
    resource: /architecture/security-and-privacy/data-and-boundaries.md
    title: Data Classification, Filesystem, and Local Storage
---

# When to use

Local paths, private repository names, internal URLs, or other non-exportable data appeared in a shared registry, an
export, a log shared with others, or an MCP response to a client that should not see it.[^sec]

# Steps

1. **Scope it.** Identify what was exposed, to whom, and through which boundary.
2. **Contain.** Disable the export, endpoint, or integration involved.
3. **Revoke access.** Remove unintended access to the shared registry where appropriate.
4. **Clean.** Remove or correct exposed records and local artifacts where possible.
5. **Look for copies.** Check backups, logs, and history for further copies.
6. **Find the cause.** Identify why the field was exportable: a missing classification, an allowlist gap, a logging path.
7. **Prevent.** Add a regression test, for example a sentinel value in that field that must never appear in an export.

# Limit

Copies already downloaded or retained by third parties cannot be recalled; say so in the report.[^cls]

# Related

- [Credential Leak](/runbooks/credential-leak.md)
- [Security Views](/architecture/views/security-views.md)

[^sec]: Logging, Configuration, Incident Response, and References
[^cls]: Data Classification, Filesystem, and Local Storage
