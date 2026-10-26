---
type: Architecture
title: "Deployment View"
description: Where Vyasa's processes, files, and external systems live on a developer machine.
tags: [c4, deployment, stdio, files]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: arch
    resource: /architecture/system-architecture/layers.md
    title: Architectural Layers
  - id: store
    resource: /architecture/local-storage/principles-and-location.md
    title: Storage Principles and Database Location
  - id: sec
    resource: /architecture/security-and-privacy/data-and-boundaries.md
    title: Data Classification, Filesystem, and Local Storage
---

# Question

Where does each part of Vyasa run, and which files and external systems does it touch on one machine?

# Deployment

```mermaid
C4Deployment
  title Vyasa on a developer machine
  Deployment_Node(machine, "Developer machine", "Linux, macOS, or Windows") {
    Deployment_Node(clientnode, "MCP client process", "Coding agent or IDE") {
      Container(client, "MCP client", "Agent", "Launches the server and calls its tools")
    }
    Deployment_Node(servernode, "Vyasa MCP server process", "Python, stdio transport") {
      Container(server, "MCP server", "Python", "Read-only query tools over the index")
    }
    Deployment_Node(clinode, "Vyasa command-line process", "Python, on demand") {
      Container(cli, "Scanner and operations", "Python", "Scans, and later sync and remote discovery")
    }
    Deployment_Node(datadir, "Per-user data directory", "Mode 0700 where supported") {
      ContainerDb(db, "Project index", "SQLite, WAL", "Observations, evidence, runs")
      Container(cfg, "Configuration", "File", "Roots, limits, enabled integrations")
      Container(logs, "Logs", "Rotating files", "Structured, redacted")
    }
    Deployment_Node(work, "Workspaces", "Local disk") {
      Container(repos, "Repositories", "Working trees", "Read-only to Vyasa")
    }
  }
  Deployment_Node(cloud, "External services", "Phases 2 and 3") {
    Container(sheets, "Google Sheets", "HTTPS API", "Shared registry")
    Container(providers, "GitHub and Bitbucket", "HTTPS APIs", "Remote repositories")
  }
  Rel(client, server, "tools/call over stdio")
  Rel(server, db, "Reads, read-only connection")
  Rel(cli, db, "Writes under a single-writer lock")
  Rel(cli, cfg, "Reads")
  Rel(cli, repos, "Reads, never writes")
  Rel(cli, sheets, "Explicit sync only")
  Rel(cli, providers, "Explicit discovery only")
  Rel(server, logs, "Writes")
  Rel(cli, logs, "Writes")
```

# What the view fixes

- The server process answers queries only; it opens the index read-only and owns no network connection.
- Anything that writes the index, reads repositories, or talks to the cloud runs in an explicit command process.
- All state lives in one per-user directory outside every scanned repository; only that directory is Vyasa's to write.
- The two processes can run at the same time because the index uses WAL with one writer; the server never blocks the writer.
- Nothing in the cloud box is required for phase 1.

# Related

- [C4 System Views](/architecture/c4-system-views.md)
- [Security Views](/architecture/views/security-views.md)
