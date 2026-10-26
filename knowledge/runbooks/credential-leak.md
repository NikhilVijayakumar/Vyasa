---
type: Runbook
title: "Suspected Credential Leak"
description: What to do, in order, when a token, key, or secret may have been exposed.
tags: [incident, credentials, response]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: sec
    resource: /architecture/security-and-privacy/operations-and-response.md
    title: Logging, Configuration, Incident Response, and References
  - id: tech
    resource: /technologies/github-and-bitbucket-apis.md
    title: GitHub and Bitbucket Cloud APIs
---

# When to use

A token appeared in a log, a shared sheet, a diagnostic bundle, a commit, or anywhere it should not be.[^sec]

# Steps

1. **Stop.** Disable the affected integration or stop the operation that is using the credential.
2. **Revoke.** Revoke or rotate the credential at its provider. Deleting the file that held it does not revoke it.
3. **Find copies.** Search local logs, the index, exported diagnostics, backups, and the shared registry for the value or
   its shape.
4. **Remove.** Remove exposed values from every place under your control.
5. **Check history.** If it was committed, remember that deleting the latest file leaves it in history; rotation is the
   fix, history rewriting is only a supplement.
6. **Reauthorize.** Issue a new credential with the narrowest scope that works, stored in the credential store.
7. **Record.** Write down what happened and what changed, without repeating the secret.

# Afterwards

Add a test that would have caught the path by which it escaped, and review the redaction patterns.

# Limit

Copies already downloaded or retained by third parties cannot be recalled.

# Related

- [Data Leak](/runbooks/data-leak.md)
- [Logging and Redaction](/practices/logging-and-redaction.md)

[^sec]: Logging, Configuration, Incident Response, and References
