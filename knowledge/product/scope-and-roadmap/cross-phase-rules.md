---
type: Product
title: "Scope and Roadmap: Cross-Phase Rules and Completion Principle"
description: Rules that hold in every phase: domain model, identity, evidence, ownership, observability, testability, security, documentation.
tags: [product, roadmap, phases]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /product/scope-and-roadmap.md
    title: Scope and Roadmap
---

# Scope and Roadmap: Cross-Phase Rules and Completion Principle

*Sections 7.1–11 of [Scope and Roadmap](/product/scope-and-roadmap.md).*

## 7.1 Shared Domain Model

The core project model must be independent of local storage, Google Sheets, and individual Git hosting providers.

Provider-specific adapters must translate data into and out of this model.

## 7.2 Stable Identity

Project identity must not depend solely on a local directory path or display name.

Identity resolution must account for local repositories without remotes, renamed directories, multiple repositories, forks, and uncertain matches.

## 7.3 Evidence and Freshness

Metadata must retain its source and relevant observation time wherever practical.

The system must distinguish:

- Never scanned.
- Successfully scanned.
- Partially scanned.
- Failed scan.
- Stale metadata.
- Remote source unavailable.
- Explicitly unknown information.

The exact states and transition rules will be defined in the architecture and requirements documents.

## 7.4 Data Ownership

Every mutable field must have an explicitly defined owner.

At minimum, the design must distinguish:

- Repository-detected facts.
- Project-maintained metadata.
- Shared human-managed registry fields.
- Local operational state.
- Remote-provider metadata.

No adapter may silently overwrite a field owned by another source.

## 7.5 Observability

Every scan and synchronization operation must produce enough structured information to explain its outcome, including relevant errors and skipped items.

Sensitive information must be excluded from logs.

## 7.6 Testability

Core business rules must be testable without external services.

Filesystem scanners, SQLite persistence, MCP interfaces, registry synchronization, and remote providers must have clear test boundaries.

External integrations should support deterministic tests using fixtures or controlled test doubles.

## 7.7 Security

- No secrets in source control or shared project metadata.
- No implicit write access to project repositories.
- Explicit configuration of workspace roots and exclusions.
- Safe handling of malformed files and inaccessible paths.
- Clear separation between trusted configuration and repository-supplied content.

## 7.8 Documentation

Each delivered capability must have appropriate requirements, tests, configuration guidance, and documented limitations.

Documentation should evolve alongside implementation rather than being deferred entirely until the end.

---

# 8. Dependencies and Phase Gates

| Gate | Required before proceeding |
|---|---|
| Phase 1 design baseline | Project identity, metadata schema, profile lifecycle, scan rules, MCP contracts, and local/shared boundaries are defined. |
| Phase 1 completion | Local discovery, indexing, MCP queries, evidence, error handling, and tests satisfy acceptance criteria. |
| Phase 2 implementation | Stable identity, shared-field ownership, export allowlist, and registry schema are agreed. |
| Phase 2 completion | Cross-device registry and synchronization pass conflict, privacy, and recovery tests. |
| Phase 3 implementation | Unified repository model, provider contracts, authentication approach, and matching rules are defined. |
| Phase 3 completion | Supported remote discovery works without cloning and passes provider and security tests. |

A later phase may refine the shared domain model, but any change must preserve compatibility or include an explicit migration.

---

# 9. Open Decisions and Deferred Items

The following items must be resolved before the affected capability is implemented.

| Item | Decision needed | Target |
|---|---|---|
| README quality | Choose a deterministic checklist or leave quality unassessed. | Phase 1 metadata rules |
| Project profile | Finalize the ignored draft versus committed canonical profile lifecycle. | Phase 1 |
| Multi-repository projects | Define grouping and identity rules for logical projects with multiple repositories. | Phase 1 model; Phase 3 matching |
| Related-project detection | Define the deterministic criteria used to identify related projects. | Phase 1 |
| Shared-field ownership | Define which registry fields are editable in Sheets and how edits are imported. | Phase 2 |
| Google authentication | Select the supported authentication and permission model. | Phase 2 |
| Remote repository scope | Confirm the exact GitHub and Bitbucket Cloud account/organization scope. | Phase 3 |
| Remote matching | Define the matching and conflict policy for local, shared, and remote records. | Phase 3 |

These decisions must not be silently filled with assumptions. Where a decision is not needed for the current phase, it may remain explicitly deferred.

---

# 10. Change Control

Changes to the scope of a phase must be documented through the project's normal change process.

A proposed change should identify:

- The requirement or capability being changed.
- The reason for the change.
- The affected phase and components.
- Compatibility and migration implications.
- Security and privacy implications.
- New or modified acceptance criteria.
- Tests required to validate the change.

OpenSpec should be used to manage implementation changes and their testable specifications. This roadmap establishes the intended product boundaries; it does not replace detailed OpenSpec requirements.

## 11. Roadmap Completion Principle

Each phase must leave Vyasa in a working, testable state.

Phase 1 establishes trusted local intelligence. Phase 2 makes project metadata available across devices. Phase 3 extends discovery to remote repositories.

The guiding principle is:

**Build a dependable local foundation first, add shared visibility second, and extend discovery to remote repositories only after the common model and ownership rules are stable.**
