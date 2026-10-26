---
type: Decision
title: "MCP Omits Local Paths by Default"
description: Tool results contain no absolute local paths unless the user enables them.
tags: [adr, mcp, privacy, paths]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: sec
    resource: /architecture/security-and-privacy/mcp-and-credentials.md
    title: MCP Security and Credential Management
  - id: mcp
    resource: /architecture/mcp-interface/errors-pagination-security.md
    title: Errors, Pagination, and Security
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

A path reveals usernames and directory structure, and agents rarely need it to answer a question. Some workflows do want it.

# Decision

Omit absolute paths from tool results by default and say whether a local checkout is available. A configuration setting enables paths for the local client. A path from another device is never shown. Evidence uses repository-relative paths.

# Alternatives considered

- **Always include paths.** Convenient, but leaks structure into every agent context.

# Consequences

- Some workflows need one configuration step.
- Results are safer to share and log.

# Related

- [MCP Interface](/architecture/mcp-interface.md)
