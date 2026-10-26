---
type: Architecture
title: "System Architecture: Decisions, Evolution, and Acceptance"
description: Mandatory constraints, undecided items, how the architecture grows by phase, and its acceptance criteria.
tags: [architecture, components, python, mcp]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/system-architecture.md
    title: System Architecture
---

# System Architecture: Decisions, Evolution, and Acceptance

*Sections 19–22 of [System Architecture](/architecture/system-architecture.md).*

## 19. Architectural Decisions and Constraints

The following constraints are part of the proposed architecture.

### Mandatory constraints

1. The core domain model must remain independent of external integrations.
2. Phase 1 must operate without Google Sheets or remote provider APIs.
3. Routine metadata extraction must be deterministic and evidence-backed.
4. Repository source files and canonical project profiles must not be modified during ordinary scanning.
5. Local paths and secrets must never be exported by default.
6. Google Sheets must not become the sole source for locally scanned evidence.
7. Remote discovery must not require repository cloning.
8. External integration failures must not invalidate unrelated local functionality.
9. Uncertain identities must not be silently merged.
10. Human-owned fields must not be overwritten by automated synchronization.

### Decisions still requiring approval

- Canonical project profile format and location.
- Exact package and module layout.
- Local MCP transport.
- SQLite concurrency and migration approach.
- Supported detector inventory.
- Project identity normalization and grouping rules.
- Google Sheets conflict and field-ownership policy.
- GitHub and Bitbucket discovery scope.
- Retention of historical observations and evidence.

These decisions should be captured in architecture decision records when resolved.

## 20. Architecture Evolution by Phase

### Phase 1

Implement:

- Domain model and core rules.
- Configuration.
- Workspace discovery.
- Git inspection.
- Metadata detectors.
- Identity resolution.
- SQLite persistence.
- Application query services.
- MCP adapter.
- Automated tests and local setup documentation.

Do not implement unused Google Sheets or remote provider adapters merely to populate the package structure.

### Phase 2

Add:

- Shared registry synchronization service.
- Google Sheets adapter.
- Export and import mapping.
- Conflict detection.
- Synchronization history.
- Cross-device registry-only project handling.

Reuse the domain model and local persistence interfaces.

### Phase 3

Add:

- Remote repository provider contract.
- GitHub adapter.
- Bitbucket Cloud adapter.
- Remote metadata inspection.
- Remote identity and reconciliation logic.
- Provider-specific error and rate-limit handling.

Reuse existing detectors wherever remote file evidence can be normalized into the same input model.

## 21. Architecture Acceptance Criteria

The architecture is sufficiently defined for Phase 1 implementation when:

1. Core domain concepts and ownership boundaries are documented.
2. Filesystem discovery, metadata extraction, identity resolution, persistence, and MCP have separate responsibilities.
3. Application services depend on defined ports rather than concrete external providers.
4. Project and repository identity are distinct concepts.
5. Metadata observations retain provenance and freshness.
6. Ordinary scanning is read-only with respect to project-owned content.
7. SQLite can be used without external services.
8. Query services do not require a full rescan for every request.
9. Failure handling preserves valid previously indexed state.
10. Critical domain rules can be tested independently of infrastructure.
11. Future integrations can be added without coupling the domain model to provider-specific structures.
12. Open decisions are recorded and resolved before they affect implementation.

## 22. Governing Architectural Principle

Vyasa should be built as a **deterministic domain core surrounded by replaceable adapters**.

Local repositories provide evidence. The domain layer establishes meaning and ownership. SQLite maintains the local index. MCP exposes the capabilities to AI agents. Google Sheets provides shared metadata, and remote repository providers extend discovery.

No adapter should become the owner of the entire system's knowledge model.

**The core remains stable; integrations evolve around it.**

---

## Proposed resolutions

The items above that still require approval have draft decision records. See [Decisions](/decisions/) for the full list;
the ones that address them directly are [Local-First SQLite Index](/decisions/local-first-sqlite-index.md),
[stdio-Only MCP Transport](/decisions/stdio-only-mcp-transport.md),
[Stored Identity With Aliases](/decisions/stored-identity-with-aliases.md),
[Canonical Profile and Draft Handling](/decisions/canonical-profile-and-draft.md), and
[Ownership-Based Conflict Resolution](/decisions/ownership-based-conflict-resolution.md).
