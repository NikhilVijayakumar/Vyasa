---
type: Architecture
title: "Vyasa (व्यास): Google Sheets and Remote Repository Security"
description: Security of the shared registry and of provider access.
tags: [security, privacy, trust-boundary]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/security-and-privacy.md
    title: Vyasa (व्यास)
---

# Vyasa (व्यास): Google Sheets and Remote Repository Security

*Sections 9–10 of [Vyasa (व्यास)](/architecture/security-and-privacy.md).*

## 9. Google Sheets security — Phase 2

Google Sheets is the shared cross-device project registry. Synchronization therefore creates an intentional boundary across the local machine, Google's service, and any users who can access the spreadsheet.

### 9.2 Export allowlist

The following information is generally suitable for consideration for synchronization, subject to owner approval and classification:

- Stable project ID.
- Project name and approved description.
- Approved repository URL.
- Languages and technologies.
- Lifecycle and tracking status.
- Documentation and standards detection results.
- Last-scanned timestamp.
- Approved portfolio notes and priorities.

The following must remain local unless a separately reviewed requirement explicitly permits an exception:

- Local repository paths and workspace roots.
- Local usernames and machine identifiers.
- SQLite database locations and internal database contents.
- Credentials, tokens, private keys, and authentication headers.
- Raw source files and document contents.
- Local cache state, temporary files, and detailed environment information.
- Local-only evidence that may expose sensitive paths or content.

Private repository URLs and internal project names can themselves be sensitive. Their presence on the proposed export list is not automatic authorization to share them.

### 9.3 Synchronization integrity

- Synchronization must be explicit and report its intended direction and scope.
- Support dry-run or preview behaviour before applying potentially destructive changes.
- Validate values read from the spreadsheet as untrusted external input.
- Never interpret spreadsheet cells as executable code, file paths, shell commands, or instructions.
- Preserve human-managed fields according to the field-ownership rules.
- Detect conflicts instead of silently overwriting human-owned values.
- Treat missing rows, API failures, and incomplete pagination as distinct from confirmed deletion.
- Keep local indexing usable if synchronization fails.
- Do not report synchronization as successful unless the relevant writes and verification steps have succeeded.

### 9.4 Google-side exposure

The shared registry may be visible to spreadsheet collaborators, administrators, or other parties according to the Google account and sharing configuration. Vyasa cannot guarantee confidentiality beyond the permissions and controls of the external service.

Users must review the spreadsheet's sharing settings and organizational policies before synchronizing internal project metadata.

---

## 10. Remote repository security — Phase 3

Remote discovery uses provider APIs without cloning repositories or checking out files.

### 10.2 API and content handling

- Use official provider APIs over authenticated HTTPS where authentication is required.
- Validate TLS certificates through standard client-library behaviour.
- Set request timeouts, pagination limits, response-size limits, and bounded retries.
- Handle rate limits without aggressive repeated requests.
- Validate response schemas and treat unexpected values as untrusted.
- Do not execute downloaded content.
- Inspect only selected files required by approved deterministic detectors.
- Do not fall back to cloning or downloading an entire repository when API inspection fails.
- Do not retain raw file contents by default.
- Record the remote revision or equivalent provenance where the provider supports it.

### 10.3 Access failures and visibility

A repository not returned by an API does not necessarily mean it has been deleted. It may be private, inaccessible, excluded by scope, hidden by permissions, or omitted because discovery was incomplete.

Vyasa must distinguish:

- Confirmed visible.
- Confirmed archived, where the provider reports it.
- Inaccessible due to authorization.
- Discovery scope incomplete.
- Provider request failed.
- Not found within a completed, appropriately scoped query.
- Deletion confirmed by reliable provider evidence, where available.

Never mark a repository obsolete or deleted solely because an API request failed.

### 10.4 Remote-only repositories

A remote repository may be indexed even when it is not cloned on the current device. Its remote metadata must not be presented as evidence that a local checkout exists or that the full source tree has been inspected.
