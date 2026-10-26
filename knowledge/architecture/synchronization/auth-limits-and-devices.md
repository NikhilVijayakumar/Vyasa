---
type: Architecture
title: "Synchronization: Authentication, API Limits, and Cross-Device Behaviour"
description: Google authentication options, quotas and retries, and behaviour across devices.
tags: [sync, google-sheets, phase-2]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/synchronization.md
    title: Synchronization
---

# Synchronization: Authentication, API Limits, and Cross-Device Behaviour

*Sections 13–15 of [Synchronization](/architecture/synchronization.md).*

## 13. Authentication and Google API Access

### 13.1 Authentication Strategy

The implementation must choose an authentication approach appropriate for the intended user and deployment model.

Possible approaches include:

- OAuth authorization for an individual Google account.
- A service account for a deliberately shared, organization-managed registry.

The choice must be made before implementation because the required setup, ownership model, and access permissions differ.

### 13.2 Least Privilege

Credentials must have only the access required for the selected spreadsheet and operations.

If the application writes to the registry, the credential must support those writes. A read-only credential must not be treated as sufficient for bidirectional synchronization.

### 13.3 Credential Storage

Credentials must be stored outside the project repository and outside Google Sheets.

Use approved local configuration or operating-system secret storage where available.

Do not:

- Commit tokens or client secrets.
- Include credentials in debug logs.
- Persist tokens as project metadata.
- Export authentication state to shared registry tabs.

### 13.4 Spreadsheet Selection

The spreadsheet ID must be explicitly configured or securely selected during setup.

The adapter must not discover and modify arbitrary spreadsheets simply because the account can access them.

### 13.5 Access Failure

Authentication or authorization failure must be reported clearly.

The system should preserve the local index and provide actionable setup guidance without exposing secret values.

---

## 14. API Limits, Retries, and Resilience

### 14.1 Batching

The adapter should batch reads and writes where supported and safe.

Batching must not undermine field-level ownership or make partial failures impossible to identify.

### 14.2 Retryable Errors

Potentially retryable errors include transient network failures, rate limiting, and temporary provider errors.

Retries should use bounded exponential backoff with jitter where appropriate.

### 14.3 Non-Retryable Errors

Invalid credentials, missing permissions, invalid schema, and malformed records generally require configuration or data correction rather than endless retries.

The adapter must distinguish retryable from non-retryable failures.

### 14.4 Rate Limiting

The implementation must respect provider quotas and avoid repeated full-sheet reads when a smaller operation is sufficient.

It should report when a synchronization run was limited by API quota.

### 14.5 Partial Failures

If some records synchronize and others fail:

- Preserve confirmed successful writes.
- Record failed records and fields.
- Keep unresolved changes pending.
- Return a partial result.
- Retry only work that remains outstanding when safe.

### 14.6 Local Independence

No synchronization failure may corrupt or disable local project queries.

The application must remain useful offline using the last available local index.

---

## 15. Cross-Device Behaviour

### 15.1 Device A Discovers a Project

1. Device A scans a local repository.
2. Vyasa extracts supported metadata.
3. The local index stores observations and evidence.
4. The synchronization planner exports approved fields.
5. The shared registry records the project and summary.

### 15.2 Device B Has Not Cloned the Project

1. Device B pulls the shared registry.
2. The logical project appears in its local index.
3. The project is identified as shared-known.
4. Its local checkout status indicates that a local checkout has not been established, if this was verified.
5. The agent can query the project summary and decide whether to access the repository separately.

Device B must not claim to have inspected the project's local files.

### 15.3 Device B Later Clones the Project

1. The scanner discovers the local repository.
2. Identity resolution attempts to match it to the existing logical project.
3. If identity is unambiguous, the local checkout is associated with the existing project.
4. Fresh observations are generated.
5. Approved scanner-owned fields are synchronized.
6. Shared human-managed fields remain intact.

### 15.4 Concurrent Updates

If two devices update different scanner-owned fields or observations, the system should merge the approved field changes where safe.

If they attempt to change the same shared human-managed field, the configured ownership and conflict policy determines the result.

The system must not assume a global, atomic ordering of all operations across devices.
