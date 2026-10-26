---
type: Product
title: "Scope and Roadmap"
description: The three delivery phases, what each includes and excludes, and their deliverables.
tags: [product, roadmap, phases]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
---

# Vyasa (व्यास) — Scope and Roadmap

## 1. Purpose

This document describes the scope and sequencing of Vyasa.

Vyasa will be developed in three phases:

1. **Phase 1 — Local Workspace Intelligence:** Discover local projects, extract metadata deterministically, maintain a SQLite index, and expose project information through MCP.
2. **Phase 2 — Shared Project Registry:** Synchronize approved project metadata through Google Sheets to provide cross-device visibility.
3. **Phase 3 — Remote Repository Discovery:** Discover and inspect GitHub and Bitbucket repositories through their APIs without cloning or checking them out.

Each phase must deliver independently useful functionality while preserving the architecture needed for subsequent phases.

## 2. Scope Principles

All implementation decisions must follow these principles.

### 2.1 Incremental Delivery

Implement and validate local discovery before adding external synchronization or remote repository providers.

Later phases must not be required for Phase 1 to work.

### 2.2 Deterministic Metadata

Routine scanning and metadata extraction must use defined rules and recognized repository evidence. LLM-based interpretation is outside the scope of the indexing pipeline.

If a fact cannot be established from an available source, report it as unknown or not documented.

### 2.3 Project-Owned Knowledge

Vyasa indexes project information but does not become the authoring authority for project-specific documentation.

A generated initial draft profile may be supported, subject to explicit draft and canonical-profile rules. Vyasa must not overwrite human-maintained project metadata.

### 2.4 Local and Shared Data Separation

Local filesystem paths, workspace configuration, machine-specific state, credentials, and secrets must remain outside the shared registry.

Only explicitly approved fields may be synchronized.

### 2.5 Non-Destructive Behaviour

Scanning, synchronization, and remote discovery must not modify repository source files or automatically delete, archive, or declare projects obsolete.

Potential duplicates, incomplete records, and obsolete-project candidates are reported for human review.

### 2.6 Provider Independence

The core project model must not depend on Google Sheets, GitHub, or Bitbucket-specific data structures.

Provider-specific adapters translate between external systems and the shared domain model.

## 3. Overall Roadmap

| Phase | Focus | Primary outcome |
|---|---|---|
| Phase 1 | Local scanner, SQLite, MCP | Queryable local project portfolio |
| Phase 2 | Google Sheets registry and synchronization | Shared project visibility across devices |
| Phase 3 | GitHub and Bitbucket APIs | Discovery of remote repositories without cloning |

The roadmap is capability-based rather than tied to calendar dates. A phase advances only when its acceptance criteria, maintained with the requirements, are satisfied.

---

# 4. Phase 1 — Local Workspace Intelligence

## 4.1 Objective

Build a deterministic local service that discovers projects across configured workspace roots, extracts supported metadata, indexes the results in SQLite, and exposes them through MCP.

The system must operate without Google Sheets, GitHub API access, Bitbucket API access, or an LLM.

## 4.2 In Scope

### A. Workspace discovery

- Configure one or more local workspace roots.
- Discover candidate project directories and Git repositories.
- Support configurable directory exclusions.
- Avoid repeatedly scanning excluded or irrelevant directories.
- Handle inaccessible paths and malformed repositories without terminating the entire scan.
- Distinguish a logical project from an individual repository where the available evidence supports that distinction.

### B. Project identity

- Generate stable project identifiers.
- Prefer normalized repository identity when a usable Git remote is available.
- Provide a deterministic local fallback identity for repositories without remotes.
- Avoid treating a filesystem rename as a new project when identity evidence remains unchanged.
- Detect potential duplicates and ambiguous identity mappings for review.

Identity resolution rules must be documented before implementation is considered complete.

### C. Deterministic metadata extraction

Extract supported facts from recognized repository evidence, including:

- Project name.
- Explicitly documented project purpose, when available.
- Git remote and repository URL.
- Programming languages.
- Frameworks and technologies supported by recognized manifests and configuration files.
- README presence and location.
- Documentation presence and recognizable structure.
- OpenSpec presence, configuration validity, and meaningful specification or change files.
- Recognized agent instruction files.
- Test-related files and configuration.
- Project-maintained status and other declared fields, when available.

The initial detector set must be documented and tested against representative repository fixtures.

OKF means Google Cloud's [Open Knowledge Format](/technologies/okf.md); its detector rules are in [Scanning and Evidence §9.11](/architecture/scanning-and-evidence.md).

### D. Local index

- Store project records and extracted metadata in SQLite.
- Store machine-specific paths and local repository mappings locally.
- Track scan timestamps, freshness, and outcomes.
- Maintain evidence references for extracted facts.
- Support incremental rescanning where practical.
- Handle schema migrations.
- Recover from interrupted or failed scans without corrupting previously valid records.

### E. MCP interface

Provide read-oriented MCP tools for:

- `search_projects`
- `get_project`
- `get_project_context`
- `find_related_projects`
- `get_project_dependencies`
- `get_index_status`

The final tool contracts, parameter schemas, response structures, and error behaviour will be defined in [mcp-interface](/architecture/mcp-interface.md).

An optional refresh operation may trigger a deterministic rescan and update the generated index. It must not be used to edit maintained project metadata.

### F. Project profile lifecycle

Define how Vyasa handles repositories without a canonical project profile.

The initial design must distinguish:

- Detected repository metadata.
- Human-declared project information.
- Generated draft information.
- Local indexing and scan state.

If a generated profile draft is implemented, it must follow the agreed git-ignored draft policy. Any committed canonical profile must remain project-owned and must not be silently replaced by the scanner.

### G. Quality and verification

- Unit tests for identity and extraction rules.
- Fixture-based scanner tests.
- SQLite persistence and migration tests.
- MCP contract tests.
- Error-handling and exclusion tests.
- End-to-end tests using temporary workspace directories.
- Documentation for local setup and MCP client configuration.

## 4.3 Out of Scope

Phase 1 will not include:

- Google Sheets integration.
- GitHub or Bitbucket API-based repository enumeration.
- Remote repository scanning without a local checkout.
- Cloud-hosted databases or mandatory cloud services.
- LLM-based project summarization, classification, or relationship inference.
- Automatic source-code modification or canonical profile maintenance.
- Automatic deletion, archival, or lifecycle changes.
- A dedicated graphical dashboard unless separately approved.
- Full semantic code search or indexing of every source-code symbol.

## 4.4 Phase 1 Deliverables

1. Python package and application entry point.
2. Configuration model and workspace discovery.
3. Project identity and metadata extraction modules.
4. Local SQLite schema and migration mechanism.
5. Deterministic scanner and index-refresh workflow.
6. MCP server and documented tool contracts.
7. Automated test suite.
8. Installation and configuration guide.
9. Example configuration and representative test fixtures.
10. Documented limitations and unsupported detection patterns.

---

# 5. Phase 2 — Shared Project Registry

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

## 6.1 Objective

Extend Vyasa to discover repositories on GitHub and Bitbucket using their APIs, without cloning or checking out repositories merely to enumerate them or inspect supported metadata.

## 6.2 In Scope

### A. GitHub discovery

- Enumerate repositories available through configured public or authenticated access.
- Support pagination.
- Retrieve repository metadata.
- Inspect supported files through API access where permissions allow.
- Respect API rate limits and report access failures.

### B. Bitbucket discovery

- Enumerate accessible Bitbucket Cloud repositories.
- Support authenticated access to private repositories using appropriately scoped credentials.
- Retrieve repository metadata and inspect supported files through APIs.
- Handle pagination, permission failures, and rate limits.

Bitbucket support initially targets Bitbucket Cloud. Other Bitbucket deployment types require separate validation and scope approval.

### C. Unified repository model

- Map remote records into the shared project and repository model.
- Match remote repositories to existing local or registered projects.
- Distinguish a project from its individual repositories.
- Handle multiple repositories belonging to one logical project.
- Flag uncertain matches and potential duplicates for human review.

### D. Remote metadata

Where supported by the provider and available permissions, extract:

- Repository name and URL.
- Description when explicitly provided.
- Default branch and repository status.
- Supported languages and technologies when evidence can be obtained.
- README and selected documentation metadata.
- Recognized manifests, instruction files, and project configuration.

Metadata unavailable through the provider API must remain unknown rather than being inferred.

### E. Authentication and reliability

- Store credentials outside the repository registry.
- Use the minimum permissions practical for discovery.
- Handle token expiration and authorization failures.
- Respect API rate limits.
- Record discovery timestamps and outcomes.
- Make failures distinguishable from empty results.

## 6.3 Out of Scope

Phase 3 will not include:

- Automatic repository cloning or checkout.
- Pushing commits or modifying remote repository content.
- Automatic deletion or archival.
- Unrestricted source-code crawling.
- Full semantic code search across remote repositories.
- Support for every Git hosting platform in the initial implementation.
- Treating a failed API request as proof that a repository no longer exists.

## 6.4 Phase 3 Deliverables

1. GitHub provider adapter.
2. Bitbucket Cloud provider adapter.
3. Remote repository discovery workflow.
4. Remote file inspection for supported metadata.
5. Cross-source identity and matching logic.
6. Credential and permission documentation.
7. API rate-limit and error-recovery behaviour.
8. Automated provider and integration tests.
9. Documentation for configuring remote discovery.

---

# 7. Cross-Phase Requirements

The following requirements apply throughout the roadmap.

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
