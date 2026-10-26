---
type: Architecture
title: "MCP Views"
description: Components of the MCP adapter, and the success and failure paths of one tool call.
tags: [c4, mcp, sequence, errors]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: mcp
    resource: /architecture/mcp-interface.md
    title: MCP Interface
  - id: err
    resource: /architecture/mcp-interface/errors-pagination-security.md
    title: Errors, Pagination, and Security

---

# Question

What is inside the MCP adapter, and what exactly happens to a tool call that succeeds and one that fails?

# Components of the adapter

```mermaid
C4Component
  title MCP adapter components
  Container_Boundary(adapter, "MCP Adapter") {
    Component(tools, "Tool handlers", "SDK registrations", "One thin handler per tool")
    Component(valid, "Input validation", "Typed models", "Schemas, bounds, no unknown fields")
    Component(build, "Response builder", "Application", "Envelope, evidence, freshness, pagination")
    Component(errmap, "Error mapper", "Application", "Stable error codes, no internals")
  }
  Container(query, "Project Query Services", "Python", "Application services")
  ContainerDb(db, "Project index", "SQLite, read-only")
  System_Ext(client, "MCP client")
  Rel(client, tools, "tools/list, tools/call over stdio")
  Rel(tools, valid, "Validates arguments")
  Rel(tools, query, "Calls with validated input")
  Rel(query, db, "Reads")
  Rel(query, build, "Results")
  Rel(tools, errmap, "Failures")
  Rel(build, client, "Structured result")
  Rel(errmap, client, "Structured error")
```

# A successful call

```mermaid
sequenceDiagram
  autonumber
  participant C as MCP client
  participant T as Tool handler
  participant V as Validation
  participant Q as Query service
  participant D as Index (read-only)
  C->>T: tools/call search_projects
  T->>V: validate arguments
  V-->>T: typed request
  T->>Q: search
  Q->>D: indexed read
  D-->>Q: rows with evidence
  Q-->>T: results, freshness, next cursor
  T-->>C: structured response with schema version
```

# A failed call

```mermaid
sequenceDiagram
  autonumber
  participant C as MCP client
  participant T as Tool handler
  participant V as Validation
  participant Q as Query service
  participant E as Error mapper
  C->>T: tools/call get_project
  T->>V: validate arguments
  alt invalid argument
    V-->>E: INVALID_ARGUMENT
  else valid
    T->>Q: fetch
    alt unknown project
      Q-->>E: NOT_FOUND
    else index cannot be read
      Q-->>E: INDEX_UNAVAILABLE
    else unexpected failure
      Q-->>E: INTERNAL_ERROR (details logged, not returned)
    end
  end
  E-->>C: structured error with stable code
```

# What the views fix

- Validation happens before any service or storage call; unknown arguments and path-like values are rejected there.
- Query services and the database connection are read-only, so a tool cannot change repositories or maintained metadata.
- Errors leave the adapter only through the mapper, which strips internals, secrets, and unnecessary absolute paths.
- Log output goes to stderr or files; standard output carries protocol messages only.

# Related

- [MCP Interface](/architecture/mcp-interface.md)
- [C4 System Views](/architecture/c4-system-views.md)
