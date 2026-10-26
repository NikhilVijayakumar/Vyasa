---
type: Architecture
title: "MCP Interface: Testing, Package Layout, and Decisions"
description: Contract and compatibility testing, the proposed package layout, open decisions, and acceptance.
tags: [mcp, interface, contracts]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/mcp-interface.md
    title: MCP Interface
---

# MCP Interface: Testing, Package Layout, and Decisions

*Sections 20–24 of [MCP Interface](/architecture/mcp-interface.md).*

## 20. Testing and Compatibility

### 20.1 Contract Tests

Each public tool must have tests for:

- Valid inputs.
- Missing required inputs.
- Invalid enums.
- Unknown IDs.
- Empty results.
- Pagination.
- Stale observations.
- Incomplete source coverage.
- Conflicting metadata.
- Index unavailability.
- Capability unavailable.
- Sensitive-field redaction.

### 20.2 MCP Integration Tests

Integration tests must verify:

- Server initialization.
- Tool registration.
- Schema visibility.
- Request validation.
- Structured responses.
- Error mapping.
- stdio protocol integrity.
- Graceful shutdown.

### 20.3 Read-Only Tests

Tests must demonstrate that query tools do not:

- Write to the local index.
- Trigger repository scanning.
- Modify repository files.
- Call external providers.

Operational tools must be tested separately to verify that their writes are limited to their explicitly documented effects.

### 20.4 Client Compatibility

Test with at least one supported MCP client and add further clients as part of the compatibility matrix.

The implementation must verify actual support for structured content, pagination patterns, progress notifications, and cancellation before relying on those capabilities.

### 20.5 Contract Versioning

The server should expose a schema or contract version through documentation and, where appropriate, status responses.

Changes must be classified as:

- Additive and backward-compatible.
- Behavioural but compatible.
- Breaking.

Breaking changes require a documented migration path and an intentional version change.

---

## 21. Proposed Python Package Boundaries

The MCP adapter should remain thin.

```text
src/vyasa/
├── domain/
│   ├── project.py
│   ├── repository.py
│   ├── observation.py
│   ├── evidence.py
│   └── relationship.py
├── application/
│   ├── search_projects.py
│   ├── get_project.py
│   ├── get_project_context.py
│   ├── find_related_projects.py
│   ├── get_project_dependencies.py
│   ├── get_index_status.py
│   └── refresh_index.py
├── infrastructure/
│   ├── persistence/
│   ├── scanning/
│   ├── configuration/
│   └── providers/
└── interfaces/
    └── mcp/
        ├── server.py
        ├── schemas.py
        ├── handlers.py
        └── errors.py
```

This is a proposed organization, not a mandatory final directory structure.

The essential dependency rule is that application services and domain models must not depend on MCP-specific types. MCP handlers translate between protocol inputs and application calls.

---

## 22. Decisions Required Before Implementation

| ID | Decision | Recommendation |
|---|---|---|
| MCP-001 | Initial transport | stdio |
| MCP-002 | MCP SDK and FastMCP version | Pin a supported version after compatibility testing |
| MCP-003 | Structured response mechanism | Use the SDK's supported structured-content interface |
| MCP-004 | Error mapping | Stable application error codes mapped to MCP-compatible errors |
| MCP-005 | Default page size | 20, maximum 100 |
| MCP-006 | Query freshness policy | Return indexed results with explicit freshness; do not silently scan |
| MCP-007 | Refresh tool availability | Disabled unless enabled in configuration; always disabled in strict query-only deployments |
| MCP-008 | Cursor consistency | Deterministic ordering; document snapshot guarantees |
| MCP-009 | Local path exposure | Omit absolute paths by default |
| MCP-010 | Future registry sync tool | Separate explicit operation |
| MCP-011 | Future remote discovery tool | Separate explicit operation |
| MCP-012 | Contract versioning | Version schemas and preserve backward compatibility |

These are proposed defaults. Implementation should verify SDK and client capabilities rather than assuming all protocol features are universally supported.

---

## 23. Acceptance Criteria

The MCP interface is ready for Phase 1 implementation when:

1. The seven proposed tools have documented inputs, outputs, and error behaviour.
2. Query tools use the generated index and do not trigger scans implicitly.
3. Project details and context preserve evidence and uncertainty.
4. Related-project results distinguish confirmed relationships from candidates.
5. Dependency results distinguish declared dependencies from resolved internal relationships.
6. Index status reports scan coverage and freshness accurately.
7. Refresh is explicitly scoped, configurable, and limited to Vyasa-owned generated state.
8. Responses are bounded and pagination is deterministic.
9. The server does not expose secrets or unnecessary absolute paths.
10. MCP handlers delegate to application services.
11. Contract and integration tests validate schemas, errors, and read-only behaviour.
12. The interface supports later shared-registry and remote-provider integrations without falsely claiming that remote information was locally verified.

## 24. Governing Principle

Vyasa's MCP interface must make project knowledge easy for coding agents to discover while preserving the distinction between what a project declares, what the scanner observes, what a shared registry records, and what remains unknown.

**The MCP server exposes evidence-backed knowledge; it does not become the owner of that knowledge.**

---

## Proposed resolutions

These are drafts, not approvals.

| Decision | Proposed in |
|---|---|
| MCP-001 transport | [stdio-Only MCP Transport](/decisions/stdio-only-mcp-transport.md) |
| MCP-006 freshness policy | [Observation Freshness Without Query-Time I/O](/decisions/observation-freshness-without-query-time-io.md) |
| MCP-007, MCP-010, MCP-011 refresh, sync, and discovery tools | [Refresh and Integration Tools Are Disabled by Default](/decisions/explicit-tools-disabled-by-default.md) |
| MCP-009 local path exposure | [MCP Omits Local Paths by Default](/decisions/mcp-local-paths-omitted-by-default.md) |
