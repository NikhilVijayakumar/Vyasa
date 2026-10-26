---
type: Practice
title: "Dependency Policy"
description: Keep the dependency set small, optional where possible, pinned, and audited.
tags: [dependencies, supply-chain, extras, audit]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: sys
    resource: /architecture/system-architecture/operations.md
    title: Error Handling, Testing, and Technology Choices
  - id: py
    resource: /technologies/python-stack.md
    title: Python Stack
---

# Rules

- **Need before dependency.** Use the standard library unless a dependency removes real complexity or risk.
- **Core stays small.** The core runtime depends only on what every installation needs.
- **Integrations are optional.** Sheets, provider, and credential-store libraries are installable extras, so the core
  runs offline without them.
- **Bounded and locked.** Declare lower bounds and commit a lockfile so builds are reproducible.
- **Audited.** Check dependencies for known vulnerabilities and licenses on every change, and when a new one is added.
- **Isolated.** A third-party library appears behind an adapter; the domain never imports one that does I/O.[^sys]

# Adding a dependency

State what it replaces, what it costs (size, transitive dependencies, maintenance), and why the standard library is not
enough. Record a durable choice as a decision.[^py]

# Related

- [Python Stack](/technologies/python-stack.md)
- [Local-First Operation](/concepts/local-first.md)

[^sys]: Error Handling, Testing, and Technology Choices
[^py]: Python Stack
