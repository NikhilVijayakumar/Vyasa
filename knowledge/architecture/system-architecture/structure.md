---
type: Architecture
title: "System Architecture: Dependency Direction and Package Structure"
description: The allowed dependency direction and the proposed Python package layout.
tags: [architecture, components, python, mcp]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/system-architecture.md
    title: System Architecture
---

# System Architecture: Dependency Direction and Package Structure

*Sections 6–7 of [System Architecture](/architecture/system-architecture.md).*

## 6. Dependency Direction

Dependencies must point toward stable domain concepts rather than external infrastructure.

```mermaid
flowchart TB
    Entry["MCP / CLI Entry Points"]
    App["Application Services"]
    Domain["Domain Models and Rules"]

    FS["Filesystem and Git Adapters"]
    DB["SQLite Adapter"]
    GS["Google Sheets Adapter"]
    GH["GitHub Adapter"]
    BB["Bitbucket Adapter"]

    Entry --> App
    App --> Domain
    App -. uses ports .-> FS
    App -. uses ports .-> DB
    App -. uses ports .-> GS
    App -. uses ports .-> GH
    App -. uses ports .-> BB
    FS --> Domain
    DB --> Domain
    GS --> Domain
    GH --> Domain
    BB --> Domain
```

The arrows to infrastructure adapters represent application services using defined ports; they do not require the domain layer to import those adapters.

The intended dependency rules are:

1. Domain modules do not import infrastructure modules.
2. Application services depend on domain concepts and abstract ports.
3. Adapters implement the ports defined for the application.
4. Entry points call application services.
5. External integrations remain optional unless explicitly enabled.
6. Provider-specific logic is confined to its adapter and mapping code.

## 7. Proposed Package Structure

The following is a proposed Python package layout. Exact module names can be refined during implementation without changing the architectural boundaries.

```text
vyasa/
├── pyproject.toml
├── README.md
├── docs/
├── tests/
└── src/
    └── vyasa/
        ├── domain/
        │   ├── models/
        │   ├── identity/
        │   ├── metadata/
        │   ├── evidence/
        │   ├── ownership/
        │   └── relationships/
        ├── application/
        │   ├── ports/
        │   ├── discovery/
        │   ├── scanning/
        │   ├── indexing/
        │   ├── projects/
        │   ├── search/
        │   ├── synchronization/
        │   └── remote_discovery/
        ├── adapters/
        │   ├── filesystem/
        │   ├── git/
        │   ├── detectors/
        │   ├── persistence/
        │   │   └── sqlite/
        │   ├── mcp/
        │   ├── google_sheets/
        │   └── repositories/
        │       ├── github/
        │       └── bitbucket/
        ├── configuration/
        ├── observability/
        └── bootstrap/
```

This structure is illustrative, not a requirement to create empty packages for every future capability in Phase 1.

Only implement modules needed for the active phase. Reserve extension points where they provide real architectural value, without prematurely implementing future integrations.
