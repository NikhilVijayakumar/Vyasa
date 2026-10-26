---
type: Architecture
title: "C4 System Views"
description: Context, container, and component views of Vyasa, the shared vocabulary for diagrams elsewhere.
tags: [c4, diagrams, context, containers, components]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T00:00:00Z }
sources:
  - id: arch
    resource: /architecture/system-architecture.md
    title: System Architecture
---

# Purpose

These views fix the names and boundaries other diagrams reuse. Each answers
one question; they are the only C4 views drawn for the whole system.[^arch]
Diagrams are Mermaid text and are unverified by a renderer in this repository.

# Context: who and what does Vyasa talk to?

```mermaid
C4Context
  title Vyasa system context
  Person(dev, "Developer", "Configures Vyasa and reviews its findings")
  System_Ext(agent, "Coding agent (MCP client)", "Asks which projects exist and what they contain")
  System(vyasa, "Vyasa", "Local-first workspace intelligence MCP server")
  System_Ext(fs, "Local workspaces", "Git repositories and project directories on this machine")
  System_Ext(sheets, "Google Sheets", "Shared project registry (phase 2)")
  System_Ext(gh, "GitHub API", "Remote repository discovery (phase 3)")
  System_Ext(bb, "Bitbucket Cloud API", "Remote repository discovery (phase 3)")
  Rel(dev, vyasa, "Configures, refreshes, reviews")
  Rel(agent, vyasa, "Queries over MCP (stdio)")
  Rel(vyasa, fs, "Reads repository metadata, read-only")
  Rel(vyasa, sheets, "Synchronizes approved fields, on request")
  Rel(vyasa, gh, "Lists and inspects repositories, on request")
  Rel(vyasa, bb, "Lists and inspects repositories, on request")
```

# Container: what runs and what stores state?

```mermaid
C4Container
  title Vyasa containers
  Person(dev, "Developer")
  System_Ext(agent, "Coding agent")
  System_Boundary(v, "Vyasa") {
    Container(mcp, "MCP server", "Python 3.12+, MCP SDK", "Tools, validation, error mapping")
    Container(scan, "Scanner", "Python", "Discovery, inspection, detectors, resolution")
    ContainerDb(db, "Project index", "SQLite", "Projects, observations, evidence, scan history")
    Container(cfg, "Configuration", "Typed file", "Workspace roots, limits, enabled integrations")
    Container(sync, "Registry sync", "Python, phase 2", "Export allowlist, conflict handling")
    Container(prov, "Provider adapters", "Python, phase 3", "GitHub and Bitbucket clients")
  }
  System_Ext(fs, "Local workspaces")
  System_Ext(sheets, "Google Sheets")
  System_Ext(gh, "GitHub / Bitbucket APIs")
  Rel(agent, mcp, "MCP over stdio")
  Rel(dev, cfg, "Edits")
  Rel(mcp, db, "Reads; refresh writes generated state")
  Rel(scan, fs, "Reads, never writes")
  Rel(scan, db, "Writes observations and scan runs")
  Rel(scan, cfg, "Reads roots and limits")
  Rel(sync, db, "Reads allowlisted fields; imports owned fields")
  Rel(sync, sheets, "Reads and writes registry rows")
  Rel(prov, gh, "Reads repositories and files")
  Rel(prov, db, "Writes remote observations")
```

Queries touch only the index. Scanner, sync, and providers run only on an
explicit operation and never as a side effect of a query.

# Component: how is the server organized?

```mermaid
C4Component
  title Vyasa server components
  Container_Boundary(app, "Vyasa process") {
    Component(mcpa, "MCP Adapter", "Entry point", "Schemas, validation, structured results and errors")
    Component(query, "Project Query Services", "Application", "Search, details, context, related, dependencies, status")
    Component(idx, "Project Index Service", "Application", "Scan orchestration, run lifecycle, freshness")
    Component(conf, "Configuration Manager", "Application", "Validated settings")
    Component(disc, "Workspace Discovery", "Application", "Roots, exclusions, candidates, outcomes")
    Component(insp, "Repository Inspector", "Application", "Bounded file inventory and safe reads")
    Component(det, "Metadata Detector Registry", "Application", "Versioned deterministic detectors")
    Component(ident, "Identity Resolver", "Domain", "Stable project and repository identity")
    Component(own, "Metadata Normalizer and Ownership Policy", "Domain", "Precedence, conflicts, observation status")
    Component(repo, "SQLite Persistence Adapter", "Adapter", "Migrations, transactions, locking")
  }
  Rel(mcpa, query, "Calls")
  Rel(query, repo, "Reads")
  Rel(idx, disc, "Runs")
  Rel(disc, conf, "Uses roots and limits")
  Rel(idx, insp, "Inspects candidates")
  Rel(insp, det, "Feeds files")
  Rel(det, own, "Emits observations")
  Rel(idx, ident, "Resolves identity")
  Rel(own, repo, "Persists resolved values")
  Rel(ident, repo, "Persists identity mappings")
```

Dependencies point inward: adapters depend on application services, which
depend on the domain; the domain depends on neither.

# Related

- [System Architecture](/architecture/system-architecture.md)
- [Scanning and Evidence](/architecture/scanning-and-evidence.md)
- [MCP Interface](/architecture/mcp-interface.md)

[^arch]: System Architecture
