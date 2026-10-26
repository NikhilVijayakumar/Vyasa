---
type: Architecture
title: "System Architecture: Architectural Layers"
description: The domain, application, adapter, and entry-point layers and what each may depend on.
tags: [architecture, components, python, mcp]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/system-architecture.md
    title: System Architecture
---

# System Architecture: Architectural Layers

*Sections 4 of [System Architecture](/architecture/system-architecture.md).*

## 4. Architectural Layers

Vyasa uses a layered modular architecture.

### 4.1 Domain Layer

Contains the core business concepts and rules:

- Project identity.
- Repository identity.
- Project metadata.
- Evidence and provenance.
- Metadata ownership.
- Project relationships.
- Freshness and observation status.
- Search criteria and matching rules.

The domain layer must not depend on MCP, SQLite, Google Sheets, GitHub, Bitbucket, or filesystem-specific implementation details.

### 4.2 Application Layer

Coordinates use cases through explicit services.

Examples include:

- Discover workspaces.
- Scan projects.
- Refresh the local index.
- Search projects.
- Retrieve project details.
- Build project context.
- Find related projects.
- Resolve project dependencies.
- Read index status.
- Synchronize shared metadata.
- Discover remote repositories.

Application services coordinate domain rules and ports. They should not contain provider-specific API logic or database queries directly.

### 4.3 Adapter Layer

Adapters implement the interfaces required by the application layer.

Examples include:

- Filesystem discovery adapter.
- Git metadata adapter.
- Manifest and configuration detectors.
- SQLite repository adapter.
- MCP server adapter.
- Google Sheets adapter.
- GitHub adapter.
- Bitbucket Cloud adapter.

Each adapter translates external representations into the common domain model.

### 4.4 Entry Points

Entry points expose application capabilities to external callers.

The initial entry point is the MCP server. A command-line interface may be added for installation, configuration, scanning, diagnostics, and administration.

Entry points must not bypass application services to manipulate domain state directly.
