---
type: Concept
title: "Explicit Operations"
description: Queries only read the index; anything that scans, writes, or contacts another system is a separate operation the user chose.
tags: [principle, side-effects, queries, mcp]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: mcp
    resource: /architecture/mcp-interface/purpose-and-principles.md
    title: Purpose, Principles, Transport, and Tool Inventory
  - id: sys
    resource: /architecture/system-architecture/context-and-vision.md
    title: Context and Vision
---

# Definition

Vyasa separates **queries** from **operations**. A query reads the local index and reports how fresh it is. An operation
(a scan, a synchronization, a remote discovery, a profile draft) changes state or contacts another system, and runs only
when someone starts it.[^mcp]

# Rules

- A query never triggers a scan, a synchronization, a provider call, or a write, not even a usage counter.
- An operation states what it will do before it does it and reports counts, errors, and coverage afterwards.
- An operation that writes outside Vyasa's own data directory is rare, explicit, and limited to a named file.
- Integrations are off until configured; a failing integration never changes how queries behave.
- Operations that reach the cloud are not offered to agents by default.

# Why

Hidden work makes latency unpredictable, breaks offline use, spends API quota, and changes the trust model without the
user noticing.[^sys]

# Related

- [Local-First Operation](/concepts/local-first.md)
- [MCP Views](/architecture/views/mcp-views.md)

[^mcp]: Purpose, Principles, Transport, and Tool Inventory
[^sys]: Context and Vision
