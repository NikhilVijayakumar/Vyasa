---
name: backend-security-review
description: >-
  Reviews Staffing backend changes for authentication, authorization, GraphQL,
  data-scope, secret-handling, abuse, and injection risks. Use only for backend
  auth/RBAC, user administration, SMTP, imports, file handling, sensitive data,
  or externally reachable API changes; do not use for frontend-only reviews.
metadata:
  scope: backend
---

# Backend Security Review

Use the approved requirements as the security contract. Inspect implementation and tests; do not assume a guard, configuration option, or safe default exists without checking the code.

## Trust boundaries and access control

- Treat every GraphQL argument, header, token, upload, and persisted value as untrusted input.
- Confirm protected queries and mutations use the authentication and permission guards required by the specification. Check object-level authorization as well as operation-level permission; a UUID is not proof of access.
- Verify permission decisions use current server-side assignments where required. Do not trust client-supplied roles or permission claims.
- Check that deactivated accounts, revoked sessions, expired tokens, replayed refresh tokens, and changed credentials invalidate access as specified.
- The current backend has no tenant boundary. Do not invent tenant semantics; do verify any approved tower/division/owner data-scope requirements before exposing staffing data.
- Review GraphQL error messages for account enumeration, authorization details, internal paths, SQL/Prisma errors, or secrets.

## Credentials, tokens, and secrets

- Passwords must be hashed with the configured password hasher; never log, return, or persist plaintext passwords.
- Invitation, refresh, and OTP tokens must be single-use or rotated as specified, expire, and be stored as cryptographic hashes/HMACs where the design requires.
- Check login lockout, OTP resend/attempt limits, generic reset acknowledgements, and session revocation for abuse and race conditions.
- Secrets belong in environment configuration or encrypted persistence, never in source control, Postman shared environments, logs, GraphQL output, or error text.
- Check encryption-key validation/rotation assumptions and ensure secret ciphertext is not accidentally mapped into DTOs.
- Review user-configurable SMTP hosts for SSRF and internal-network access; ensure required egress controls and allowlisting decisions are documented rather than assumed.

## GraphQL and browser controls

- Preserve the configured CORS origin allowlist and Apollo CSRF protection. Do not disable CSRF to make a client request succeed; fix client headers or the approved API setup.
- Inspect GraphQL nullability, argument validation, resolver guards, aliases/batching, and resource-intensive list/search fields for abuse paths.
- Avoid exposing private credential, invitation, reset, SMTP-password, or internal persistence fields through generated GraphQL types.
- Verify errors preserve useful client semantics without exposing implementation details.

## Database, imports, and email

- Review SQL/Prisma query construction for injection and authorization bypass.
- Verify database uniqueness, foreign keys, check/exclusion constraints, transaction boundaries, and concurrency behavior for security-critical invariants.
- For CSV/Excel data, check size and row bounds, encoding/parser behavior, formula injection on exports, identifier matching, and whether names are incorrectly treated as stable identities.
- Ensure email templates escape user-controlled fields and do not place passwords or reusable raw tokens in logs. Check invitation/reset recipient and expiry handling.
- Avoid logging full request bodies or sensitive GraphQL variables.

## Findings

Prioritize findings as Critical, High, Medium, or Low and identify the affected path, attacker capability, impact, and practical remediation. Separate confirmed vulnerabilities from unverified risks that need configuration or deployment evidence. State what security checks were not performed.
