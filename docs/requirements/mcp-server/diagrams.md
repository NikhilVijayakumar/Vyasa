# Diagrams: MCP Server and Tool Contracts

C4 vocabulary: `knowledge/architecture/c4-system-views.md`. The question here is where the protocol boundary sits.

## Where does the protocol end and the application begin? (container view)

```mermaid
C4Container
  title MCP server boundary
  System_Ext(agent, "Coding agent", "MCP client over stdio")
  System_Boundary(v, "Vyasa process") {
    Container(adapter, "MCP Adapter", "Python, MCP SDK", "Schemas, validation, size cap, error mapping, snapshot-tested")
    Container(query, "Project Query Services", "Python", "Read-only application services")
    ContainerDb(db, "Project index", "SQLite, opened read-only", "Source of every answer")
  }
  Rel(agent, adapter, "tools/list, tools/call over stdio")
  Rel(adapter, query, "Validated requests")
  Rel(query, db, "Reads")
```

The adapter never opens a network listener, never passes a path through, and never writes to stdout except
protocol messages.
