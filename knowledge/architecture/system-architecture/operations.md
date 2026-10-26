---
type: Architecture
title: "System Architecture: Error Handling, Testing, and Technology Choices"
description: Error and observability architecture, the testing architecture, and the technology baseline.
tags: [architecture, components, python, mcp]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: parent
    resource: /architecture/system-architecture.md
    title: System Architecture
---

# System Architecture: Error Handling, Testing, and Technology Choices

*Sections 16–18 of [System Architecture](/architecture/system-architecture.md).*

## 16. Error Handling and Observability

The architecture must distinguish failures at different boundaries.

Expected error categories include:

- Invalid configuration.
- Missing or inaccessible workspace.
- Repository inspection failure.
- Unsupported or malformed metadata.
- Identity conflict.
- Database failure.
- Scan interruption.
- MCP input validation failure.
- Google authentication or synchronization failure.
- Remote provider rate limiting or access failure.

Each operation should produce an outcome containing, as appropriate:

- Operation or run ID.
- Scope.
- Start and completion times.
- Success, partial success, or failure status.
- Counts of discovered, updated, skipped, and failed items.
- Structured error categories.
- Safe diagnostic details.

Logs must not corrupt stdio-based MCP protocol messages. Diagnostics should use an appropriate logging channel.

## 17. Testing Architecture

Testing should follow the same module boundaries as the implementation.

### 17.1 Domain Tests

Test:

- Project and repository identity.
- Field ownership and precedence.
- Metadata normalization.
- Evidence and freshness states.
- Deterministic relationship rules.

These tests should not require a database or network.

### 17.2 Adapter Tests

Test:

- Filesystem discovery against controlled directory fixtures.
- Detectors against representative files.
- SQLite persistence and migrations.
- MCP schemas and responses.
- Google Sheets mappings and synchronization using test doubles.
- Remote provider pagination and error handling using fixtures or mocks.

### 17.3 Integration Tests

Test the complete flow from workspace discovery through SQLite persistence to MCP retrieval.

Later phases should add separate integration suites for Sheets synchronization and remote repository discovery.

External integration tests must not require production credentials for routine local test execution.

### 17.4 Failure Tests

Include:

- Missing roots.
- Unreadable files.
- Malformed manifests.
- Duplicate identities.
- Interrupted scans.
- Database failures.
- Partial synchronization.
- Rate limits.
- Invalid authentication.
- Stale observations.

## 18. Technology Choices

The following are proposed baseline technologies, subject to validation during implementation.

| Concern | Proposed choice | Reason |
|---|---|---|
| Language | Python 3.12+ | Suitable for filesystem tooling, metadata processing, and integration adapters |
| MCP | Official Python MCP SDK / FastMCP approach | Provides the agent-facing protocol integration |
| Validation | Pydantic | Structured input and output validation |
| Local persistence | SQLite | Embedded, portable, and local-first |
| Git inspection | Git CLI or a carefully selected Python library | Repository metadata and remote inspection |
| Testing | pytest | Unit and integration testing |
| Configuration | Validated typed configuration | Explicit and predictable application settings |
| Logging | Python structured logging approach | Operational diagnostics |
| Remote APIs | Provider-specific HTTP clients or supported SDKs | Phase 3 integration |

The implementation should use the least complex dependency set that meets the requirements.

Exact package choices, version pins, CLI behaviour, and database schema are implementation decisions and should be documented separately.
