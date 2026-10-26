---
type: Architecture
title: "Vyasa (व्यास) — MCP Interface"
description: MCP tools, parameters, response conventions, error codes, and limits exposed to coding agents.
tags: [mcp, interface, contracts]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
---
# Vyasa (व्यास) — MCP Interface

Related architecture:

- [system-architecture](/architecture/system-architecture.md)
- [data-model](/architecture/data-model.md)
- [scanning-and-evidence](/architecture/scanning-and-evidence.md)

## Summary

This document defines the MCP interface through which OpenCode, Claude Code, and other MCP-compatible agents access Vyasa's workspace intelligence.

## Parts

This concept is split into parts so each can be read on its own. Section numbers in the table are those of the original document, so references such as "§9.11" resolve to the part that contains them.

| Part | Sections | What it answers |
|---|---|---|
| [Purpose, Principles, Transport, and Tool Inventory](mcp-interface/purpose-and-principles.md) | §1–5 | Why the interface exists, its design principles, server responsibilities, transport, and the tool list. |
| [Shared Response Conventions](mcp-interface/response-conventions.md) | §6 | The response envelope, identifiers, missing values, evidence objects, observation status, and freshness. |
| [Search and Project Details Tools](mcp-interface/search-and-details.md) | §7–8 | Contracts for search_projects and get_project. |
| [Project Context and Related Projects Tools](mcp-interface/context-and-related.md) | §9–10 | Contracts for get_project_context and find_related_projects. |
| [Dependencies, Index Status, and Refresh Tools](mcp-interface/dependencies-status-refresh.md) | §11–13 | Contracts for get_project_dependencies, get_index_status, and the optional refresh_index. |
| [Errors, Pagination, and Security](mcp-interface/errors-pagination-security.md) | §14–16 | Error codes and shape, validation, pagination, response limits, and the MCP security rules. |
| [Later Phases and Client Configuration](mcp-interface/phases-and-client-config.md) | §17–19 | How Sheets and remote operations attach later, and how MCP clients launch the server. |
| [Testing, Package Layout, and Decisions](mcp-interface/testing-and-decisions.md) | §20–24 | Contract and compatibility testing, the proposed package layout, open decisions, and acceptance. |
