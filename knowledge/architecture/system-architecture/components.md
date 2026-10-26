---
type: Architecture
title: "System Architecture: Component Responsibilities"
description: What each component owns: configuration, discovery, inspection, detectors, identity, normalization, index, persistence, query, MCP, Sheets, providers.
tags: [architecture, components, python, mcp]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/system-architecture.md
    title: System Architecture
---

# System Architecture: Component Responsibilities

*Sections 5 of [System Architecture](/architecture/system-architecture.md).*

## 5. Component Responsibilities

### 5.1 Configuration Manager

**Purpose:** Load and validate application configuration.

Responsibilities:

- Workspace roots.
- Exclusion rules.
- Local database location.
- Scanner options.
- Enabled integrations.
- Credential references and secret-provider configuration.
- Logging and operational settings.

Configuration must distinguish ordinary settings from secrets.

Invalid configuration must produce actionable errors rather than silently falling back to unintended filesystem locations or permissions.

### 5.2 Workspace Discovery

**Purpose:** Find eligible project and repository candidates.

Responsibilities:

- Traverse configured workspace roots.
- Apply exclusions.
- Identify Git repositories and supported non-Git projects.
- Handle nested repositories according to explicit rules.
- Respect symlink policies.
- Report inaccessible and malformed directories.
- Produce repository candidates for further inspection.

Workspace discovery must not decide project ownership or invent relationships from directory proximity alone.

### 5.3 Repository Inspector

**Purpose:** Retrieve supported repository metadata.

Responsibilities:

- Read Git remotes and repository state.
- Identify relevant repository files.
- Detect the repository revision or local state where practical.
- Inspect supported files without executing repository code.
- Provide controlled access to files required by detectors.

The inspector must enforce file-size limits and safe path handling.

### 5.4 Metadata Detector Registry

**Purpose:** Extract supported facts through independent, deterministic detectors.

Potential detector groups include:

- Project profile detector.
- README detector.
- Language detector.
- Framework and dependency detector.
- Documentation structure detector.
- OpenSpec detector.
- Agent instruction detector.
- Test indicator detector.
- Other explicitly supported convention detectors.

Each detector should declare:

- Which files or evidence it consumes.
- Which fields it can produce.
- How it validates its inputs.
- How it represents unknown or unsupported information.
- How it records evidence.
- Its detector version.

A detector must not claim that a field is supported simply because a relevant directory or file exists.

### 5.5 Identity Resolver

**Purpose:** Establish stable identities and associate repository observations with logical projects.

Responsibilities:

- Normalize supported remote identities.
- Assign deterministic fallback identities when no reliable remote identity exists.
- Match local checkouts to known repositories.
- Detect duplicate and ambiguous identities.
- Support projects with multiple repositories when explicit grouping evidence exists.
- Avoid merging uncertain records automatically.

Identity rules must be deterministic, documented, and tested independently of the storage adapter.

### 5.6 Metadata Normalizer and Ownership Policy

**Purpose:** Convert detector output into a consistent representation while preserving ownership and provenance.

Responsibilities:

- Normalize supported values.
- Validate canonical profile fields.
- Distinguish detected facts from declared metadata.
- Apply field-specific precedence rules.
- Retain conflicting observations where necessary.
- Prevent generated observations from overwriting human-owned values.

Normalization must not erase evidence of the original source or imply certainty beyond what the evidence supports.

### 5.7 Project Index Service

**Purpose:** Coordinate updates to the generated local index.

Responsibilities:

- Receive scan results.
- Resolve project identity.
- Apply ownership rules.
- Persist observations and evidence.
- Update freshness and scan status.
- Maintain project-to-repository mappings.
- Preserve valid state during failed operations.

The index service owns generated index state, not project-maintained documentation.

### 5.8 SQLite Persistence Adapter

**Purpose:** Persist local index and operational state.

Responsibilities:

- Store project and repository records.
- Store metadata observations and evidence references.
- Store local checkout mappings.
- Store scan history and errors.
- Manage schema migrations.
- Support indexed search and retrieval.
- Maintain transaction boundaries.

The database must not become the only surviving authority for project-owned knowledge. It is a local index that can be rebuilt from available sources, subject to the documented retention policy.

### 5.9 Project Query Services

**Purpose:** Provide reusable read operations over the indexed domain model.

Responsibilities:

- Search projects.
- Retrieve a project.
- Build structured project context.
- Find related projects.
- Retrieve supported dependency information.
- Report index and freshness status.

Query services must operate against indexed data by default rather than rescanning every repository for every request.

### 5.10 MCP Adapter

**Purpose:** Expose application services through MCP.

Responsibilities:

- Register tools and their schemas.
- Validate inputs.
- Call application services.
- Return structured results.
- Report errors consistently.
- Enforce the read-only boundary of query tools.

MCP tools must not implement separate copies of the domain rules.

### 5.11 Google Sheets Adapter — Phase 2

**Purpose:** Synchronize approved shared project metadata.

Responsibilities:

- Validate the workbook structure.
- Map registry rows to domain records.
- Export only approved fields.
- Import only explicitly designated shared fields.
- Preserve human-owned fields.
- Detect and report conflicts.
- Record synchronization outcomes.
- Retry operations safely.

The adapter must not export local paths, credentials, or arbitrary local database fields.

### 5.12 Remote Repository Adapters — Phase 3

**Purpose:** Discover and inspect remote repositories without requiring local clones.

Separate adapters should support GitHub and Bitbucket Cloud.

Responsibilities:

- Authenticate within the configured access scope.
- Enumerate repositories.
- Handle pagination and rate limits.
- Retrieve repository metadata.
- Read supported files through provider APIs.
- Record provider identity and observation provenance.
- Convert results into the shared domain model.

Provider-specific response types must not leak into core domain rules.
