---
type: Decision
title: "stdio-Only MCP Transport"
description: The MCP server speaks over standard input and output only and opens no network listener.
tags: [adr, mcp, transport, security]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: mcp
    resource: /architecture/mcp-interface/purpose-and-principles.md
    title: Purpose, Principles, Transport, and Tool Inventory
  - id: sec
    resource: /architecture/security-and-privacy/mcp-and-credentials.md
    title: MCP Security and Credential Management
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Clients are coding agents running as the same user on the same machine. A network endpoint would add exposure that nothing in the first phases needs.

# Decision

Support the stdio transport only. The server inherits the launching user's authority and needs no authentication. Standard output carries protocol messages only; logging uses standard error and files. A network transport requires its own decision covering authentication, TLS, origin checks, and a new threat review.

# Alternatives considered

- **HTTP or SSE from the start.** Reaches more clients but adds listeners, authentication, and origin concerns immediately.

# Consequences

- No remote use of the server.
- Trust equals the local user's trust, and the documentation must say so.
- Adding a transport later is a deliberate, reviewed change.

# Related

- [MCP Interface](/architecture/mcp-interface.md)
- [MCP Protocol](/technologies/mcp-protocol.md)
