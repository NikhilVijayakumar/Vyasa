---
type: Architecture
title: "Vyasa (व्यास): Logging, Configuration, Incident Response, and References"
description: Safe logging, secure defaults, incident response, and references.
tags: [security, privacy, trust-boundary]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/security-and-privacy.md
    title: Vyasa (व्यास)
---

# Vyasa (व्यास): Logging, Configuration, Incident Response, and References

*Sections 11– of [Vyasa (व्यास)](/architecture/security-and-privacy.md).*

## 11. Logging, diagnostics, and auditability

Logs are a potential data-leakage channel and must follow the same minimization principles as the index.

### 11.1 Safe logging

Log operational facts such as:

- Scan or synchronization run ID.
- Operation type and duration.
- Number of projects processed.
- Outcome and failure category.
- Provider name and relevant HTTP status category.
- Detector identifier and version.
- Retry count and rate-limit state.

Do not log:

- Access tokens, refresh tokens, passwords, private keys, or authorization headers.
- Complete configuration files or repository documents.
- Raw file contents or matched secret values.
- Full environment-variable dumps.
- Full provider responses when they may contain sensitive information.
- Unnecessary absolute filesystem paths or user-identifying details.

### 11.2 Error handling

- Sanitize exception messages before logging or returning them.
- Keep detailed local diagnostics separate from MCP responses.
- Avoid leaking SQL statements, authentication details, or stack traces to clients.
- Use stable error categories so callers can respond without parsing sensitive free-text messages.
- Ensure failure reporting does not itself trigger a broader scan or additional network request.

### 11.3 Audit trail

Record the occurrence and outcome of security-relevant operations, including:

- Remote discovery.
- Shared-registry synchronization.
- Credential validation failures.
- Configuration changes that alter scope or permissions.
- Explicit project removal or cleanup.
- Security-sensitive write operations, if draft generation is implemented.

The audit trail should record what happened, not copy the secret or sensitive payload involved.

---

## 12. Configuration and secure defaults

Security-sensitive settings must be explicit, documented, and validated.

Examples include:

- Workspace roots.
- Exclusion patterns.
- Symlink policy.
- Maximum file size and scan limits.
- Enabled provider integrations.
- Google spreadsheet identity.
- GitHub organization/user scopes.
- Bitbucket workspace scopes.
- Export allowlist version.
- Log verbosity and retention.
- Whether optional draft generation is enabled.

---

## 13. Security incident response

Vyasa should provide clear operator guidance for suspected exposure or unauthorized activity.

### 13.1 Suspected credential leak

1. Disable the affected integration or stop the relevant operation.
2. Revoke or rotate the affected credential through its provider.
3. Inspect local logs and the shared registry for accidental disclosure.
4. Remove exposed values from locations under the operator's control.
5. Review repository history if a credential was committed; deleting the latest file alone does not remove historical exposure.
6. Reauthorize using least-privilege credentials.
7. Record the incident and corrective action without reproducing the secret.

### 13.2 Suspected data leakage

1. Identify which data was exposed, to whom, and through which boundary.
2. Disable the affected export, endpoint, or integration.
3. Revoke unintended access to the shared registry where appropriate.
4. Remove or correct exposed records and local artifacts where possible.
5. Determine whether backups, logs, or repository history contain additional copies.
6. Review the cause and add a regression test.

Vyasa cannot guarantee deletion of copies already downloaded or retained by third parties. Incident guidance must state this limitation.

---

## 14. References

These references inform the proposed security principles; they do not replace a project-specific threat model or security review.

- [OWASP Developer Guide — Protect Data Everywhere](https://devguide.owasp.org/en/04-design/02-web-app-checklist/08-protect-data/)
- [OWASP — Secure by Design Framework](https://owasp.org/projects/secure-by-design-framework)
- [OWASP — Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [OWASP — Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Microsoft Learn — Best practices for protecting secrets](https://learn.microsoft.com/en-us/azure/security/fundamentals/secrets-best-practices)

---

## Final design rule

Vyasa should be conservative about what it reads, precise about what it stores, explicit about what it shares, and honest about what it could not verify. Every new capability that crosses a filesystem, agent, cloud, or repository-provider boundary must define its permissions, data exposure, failure behaviour, and tests before implementation.
