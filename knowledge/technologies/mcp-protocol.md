---
type: Technology
title: "Model Context Protocol and the stdio Transport"
description: How MCP tool calls work, why standard output is reserved, and why tool text is an injection surface.
tags: [mcp, stdio, tools, protocol]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
stale_after: 2027-01-26T00:00:00Z
sources:
  - id: mcp
    resource: /architecture/mcp-interface.md
    title: MCP Interface
  - id: pur
    resource: /architecture/mcp-interface/purpose-and-principles.md
    title: Purpose, Principles, Transport, and Tool Inventory
---

# What it is

A protocol that lets an agent host discover and call tools exposed by a server. The host lists the tools, receives each
tool's name, description, and input schema, and calls them with arguments.[^mcp]

# The stdio transport

- The host launches the server as a child process and exchanges JSON-RPC messages over its standard input and output.
- **Standard output belongs to the protocol.** Anything else printed there corrupts the stream. Logs go to standard error
  or to files.
- The server inherits the launching user's authority; there is no separate authentication, and no network listener.

# Results and errors

A tool returns a result that the host passes to the model. A tool-level failure is reported as a result marked as an
error, with content the model can read, which is different from a protocol error for a malformed request. Newer protocol
revisions also allow structured results with a declared output schema; check what the chosen SDK supports.

# Risks to design for

- Tool descriptions and results are read by a model. Text in them can try to steer it, so descriptions are written by the
  server author only, and results carry repository text as typed, bounded data.
- A host may call tools in loops. Keep tools cheap, bounded, and side-effect free.[^pur]

# Related

- [MCP Interface](/architecture/mcp-interface.md)
- [Untrusted Content](/concepts/untrusted-content.md)

[^mcp]: MCP Interface
[^pur]: Purpose, Principles, Transport, and Tool Inventory
