---
type: Decision
title: "Refresh and Integration Tools Are Disabled by Default"
description: The refresh tool and any later synchronization or discovery tools are not offered to agents unless configured.
tags: [adr, mcp, tools, side-effects]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: exp
    resource: /concepts/explicit-operations.md
    title: Explicit Operations
  - id: mcp
    resource: /architecture/mcp-interface/dependencies-status-refresh.md
    title: Dependencies, Index Status, and Refresh Tools
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

An agent that can start scans or push data to a cloud service can cause expense, writes, and exposure the user did not choose.

# Decision

The six query tools are always available. `refresh_index` and any later synchronization or discovery tool are registered only when the configuration enables them; strict query-only deployments leave them off. The same operations remain available as explicit commands for the user.

# Alternatives considered

- **Always expose refresh.** Convenient, but agent-triggered work and writes.

# Consequences

- Agents must be told to ask the user for a refresh.
- Enabling is a visible, deliberate act.

# Related

- [Explicit Operations](/concepts/explicit-operations.md)
