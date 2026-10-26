---
type: Product
title: "Scope and Roadmap: Phase 2: Shared Project Registry"
description: What phase 2 includes, excludes, and delivers.
tags: [product, roadmap, phases]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /product/scope-and-roadmap.md
    title: Scope and Roadmap
---

# Scope and Roadmap: Phase 2: Shared Project Registry

*Sections 5.1–5.4 of [Scope and Roadmap](/product/scope-and-roadmap.md).*

## 5.1 Objective

Add Google Sheets as a shared registry for project metadata, enabling project visibility across devices while preserving local indexing and project ownership.

Google Sheets is a shared registry, not merely a report or export destination.

A device must be able to discover that a project exists even if the project has not been cloned on that device.

## 5.2 In Scope

### A. Registry structure

Implement the agreed initial workbook structure.

**Project Registry**

- Project ID.
- Project name.
- Domain.
- Project type.
- Git origin/platform.
- Repository URL.
- Programming languages.
- Frameworks and technologies.
- Lifecycle status.
- Tracking level.
- Last scanned.
- Details status.

**Documentation & Standards**

- Project ID.
- README presence.
- README quality status.
- Documentation presence.
- Documentation structure.
- OpenSpec enabled.
- OpenSpec configuration status.
- OKF enabled.
- Agent instructions.
- Tests present.
- Documentation entry point.

**Scan History**

- Run ID.
- Timestamp.
- Scan scope.
- Projects discovered.
- Projects added or updated.
- Projects requiring review.
- Skipped projects.
- Errors.
- Synchronization result.

CI/CD Present and Standards Review are explicitly excluded from the initial registry design.

### B. Synchronization

- Define an explicit allowlist of shareable fields.
- Upsert records using stable project identity.
- Preserve human-managed fields.
- Detect conflicting changes.
- Record synchronization outcomes.
- Handle network errors, API limits, and partial failures.
- Avoid corrupting local state when synchronization fails.
- Define which fields can be edited in Sheets and whether those changes are imported locally.

### C. Cross-device visibility

- Load registered project metadata on a new device.
- Distinguish registered projects from projects scanned locally.
- Distinguish locally accessible repositories from repositories known only through the registry.
- Avoid presenting an unavailable local path as if it were accessible on the current device.

### D. Credentials and access

- Keep Google credentials in local secure configuration or an appropriate secret store.
- Never write credentials, local paths, or workspace roots to the shared registry.
- Document the required Google API access and minimum practical permissions.
- Provide clear handling for authentication and authorization failures.

### E. Testing

- Registry mapping tests.
- Upsert and identity tests.
- Human-field preservation tests.
- Conflict tests.
- Offline and retry tests.
- Cross-device simulation tests.
- Data export allowlist tests.

## 5.3 Out of Scope

Phase 2 will not include:

- GitHub or Bitbucket API-based discovery.
- Cloning or checking out repositories.
- A general-purpose project management workflow.
- Automatic lifecycle transitions or archival.
- Automatic overwriting of canonical project documentation.
- Synchronization of secrets, local paths, or machine-specific state.

## 5.4 Phase 2 Deliverables

1. Google Sheets adapter.
2. Versioned registry mapping and field ownership rules.
3. Explicit export allowlist.
4. Synchronization workflow and conflict handling.
5. Scan history integration.
6. Credential configuration and security documentation.
7. Automated synchronization tests.
8. Setup guide for enabling the shared registry.

---

# 6. Phase 3 — Remote Repository Discovery
