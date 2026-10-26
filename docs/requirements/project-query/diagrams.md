# Diagrams: Project Search, Context, Relations and Dependencies

C4 vocabulary: `knowledge/architecture/c4-system-views.md`.

## What does a query touch? (dynamic view)

```mermaid
sequenceDiagram
  autonumber
  actor Agent as Coding agent
  participant Mcp as MCP Adapter
  participant Qry as Project Query Services
  participant Db as SQLite Persistence Adapter (read-only)
  Agent->>Mcp: search_projects(filters, limit, cursor)
  Mcp->>Mcp: validate and bound input
  Mcp->>Qry: query
  Qry->>Db: read indexed rows
  Db-->>Qry: rows with observations and evidence
  Qry-->>Mcp: results, match provenance, coverage, freshness
  Mcp-->>Agent: structured response
  Note over Qry,Db: No scan, no synchronization, no provider call, no write
```

## How is a related project explained?

```mermaid
flowchart LR
  A[Project A] -- declares dependency on --> B[Project B]
  A -- profile-declared relation --> C[Project C]
  A -- shares 2+ recognized technologies --> D[Project D]
  B --> R1[rank 1: explicit dependency]
  C --> R2[rank 2: profile-declared]
  D --> R3[rank 3: shared-technology count, then name]
```
