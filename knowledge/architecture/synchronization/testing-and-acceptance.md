---
type: Architecture
title: "Synchronization: Testing, Sequence, and Acceptance"
description: Test strategy, implementation order, open decisions, and acceptance criteria.
tags: [sync, google-sheets, phase-2]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/synchronization.md
    title: Synchronization
---

# Synchronization: Testing, Sequence, and Acceptance

*Sections 19–23 of [Synchronization](/architecture/synchronization.md).*

## 19. Testing Strategy

### 19.1 Unit Tests

Test:

- Field ownership decisions.
- Export allowlist enforcement.
- Canonical field normalization.
- Fingerprint stability.
- Conflict classification.
- Stable ID matching.
- Retry classification.
- Empty-value handling.

### 19.2 Fake Adapter Tests

Use a fake Google Sheets adapter to simulate:

- Successful reads and writes.
- Duplicate IDs.
- Missing tabs.
- Unexpected columns.
- Permission errors.
- Timeouts.
- Rate limits.
- Partial batch failures.
- Concurrent edits.
- Ambiguous write outcomes.

These tests must not require production credentials.

### 19.3 Integration Tests

Use a dedicated test spreadsheet or isolated test environment to verify:

- Initial pull.
- Initial push.
- Bidirectional synchronization.
- Read-back verification.
- Cross-device identity matching.
- Schema validation.
- Conflict reporting.
- Recovery after interrupted synchronization.

### 19.4 Data Preservation Tests

Verify that:

- Human-managed fields survive scanner updates.
- Local-only paths never appear in exported records.
- Secrets cannot enter the export payload.
- A failed scan does not clear valid shared metadata.
- A failed sync does not corrupt SQLite.
- Duplicate project IDs do not result in arbitrary row overwrites.
- Local disappearance does not automatically delete a shared project.

### 19.5 Idempotency Tests

Running the same synchronization twice with unchanged sources should produce no duplicate projects and no unnecessary updates.

A repeated operation after an uncertain write should reconcile the actual shared state before retrying.

---

## 20. Implementation Sequence

The recommended Phase 2 order is:

1. Finalize the field ownership and export/import matrix.
2. Finalize the Google Sheets schema and version marker.
3. Choose the authentication model.
4. Implement the Google Sheets adapter behind a provider-neutral interface.
5. Add local synchronization state and migrations to SQLite.
6. Implement schema validation and registry reads.
7. Implement stable identity matching.
8. Implement dry-run change planning.
9. Implement field-level ownership and conflict detection.
10. Implement safe upserts and write verification.
11. Implement bounded retries and partial-failure recovery.
12. Implement synchronization history and status reporting.
13. Integrate explicit synchronization with the application interface.
14. Add cross-device, privacy, idempotency, and failure-recovery tests.
15. Validate against a dedicated test spreadsheet before enabling the integration for normal use.

Phase 2 is complete only when a project discovered on one device can be represented in the shared registry and safely discovered on another device without a local checkout.

---

## 21. Decisions Required Before Implementation

| ID | Decision | Recommendation |
|---|---|---|
| SY-001 | Authentication model | Choose OAuth or service account based on registry ownership |
| SY-002 | Spreadsheet ownership | Explicitly configure the shared registry |
| SY-003 | Field ownership matrix | Finalize before enabling writes |
| SY-004 | Project ID generation | Reuse the approved identity policy |
| SY-005 | Multiple repositories per project | Define representation before schema freeze |
| SY-006 | Enum values for portfolio fields | Define and validate allowed values |
| SY-007 | Empty-field semantics | Distinguish blank, unknown, not detected, and intentional clearing |
| SY-008 | Conflict resolution | Field-specific; no universal last-write-wins |
| SY-009 | Delete and retirement workflow | Preserve records by default |
| SY-010 | Write verification | Read back ambiguous or critical updates |
| SY-011 | Retry policy | Bounded backoff and safe reconciliation |
| SY-012 | Sync scheduling | Explicit/manual initially; automation can be added later |
| SY-013 | Shared scan-history semantics | Define whether rows represent scans or sync operations |
| SY-014 | Registry schema version | Controlled version marker and validation |
| SY-015 | Conflict resolution interface | Manual review initially |
| SY-016 | Sync tool enablement | Explicit configuration; disabled in strict read-only mode |

These decisions must be resolved or explicitly accepted as implementation defaults before the corresponding functionality is built.

---

## 22. Acceptance Criteria

The synchronization implementation is ready when:

1. Google Sheets acts as a shared project registry across devices.
2. The initial spreadsheet contains the three approved tabs.
3. `CI/CD Present` and `Standards Review` are excluded from the initial schema.
4. Projects are matched using stable identity rather than names or local paths.
5. Synchronization follows an explicit field ownership matrix.
6. Scanner updates preserve human-managed registry fields.
7. Local paths, database paths, credentials, and machine-specific state never enter shared exports.
8. Upserts are idempotent.
9. Duplicate identities and ambiguous writes are handled safely.
10. Conflicts are visible and do not cause silent data loss.
11. A missing local project does not automatically delete the shared record.
12. Failed or partial synchronization does not corrupt the local index.
13. Retries are bounded and safe.
14. Local scan freshness and synchronization freshness are tracked independently.
15. Shared-only projects can be queried on a device without a local checkout.
16. Authentication and permissions are validated before writes.
17. Synchronization has dry-run, integration, and recovery tests.
18. The local index remains useful when Google Sheets is unavailable.

## 23. Governing Principle

Vyasa synchronization connects independent local indexes to a shared portfolio registry without collapsing their different responsibilities.

Repositories remain the source for repository-owned information. SQLite remains the local index. Google Sheets provides shared portfolio visibility and shared human-managed metadata.

**Synchronize approved knowledge, preserve ownership, and never let a failed or ambiguous sync destroy information.**

---

## Proposed resolutions

These are drafts, not approvals.

| Decision | Proposed in |
|---|---|
| SY-001 authentication model | [Credential Storage and Registry Identity](/decisions/credential-storage-and-sheets-identity.md) |
| SY-003, SY-008 field ownership and conflict resolution | [Ownership-Based Conflict Resolution](/decisions/ownership-based-conflict-resolution.md) |
| SY-016 sync tool enablement | [Refresh and Integration Tools Are Disabled by Default](/decisions/explicit-tools-disabled-by-default.md) |
