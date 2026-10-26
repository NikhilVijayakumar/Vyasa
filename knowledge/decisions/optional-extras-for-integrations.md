---
type: Decision
title: "Optional Extras for Integrations"
description: Libraries for Sheets, providers, and credential stores install as optional extras, so the core runs without them.
tags: [adr, dependencies, packaging]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: dep
    resource: /practices/dependency-policy.md
    title: Dependency Policy
  - id: py
    resource: /technologies/python-stack.md
    title: Python Stack
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Phase 1 is offline and should be small. Later integrations pull in larger libraries that most installations do not need.

# Decision

Package the integrations as extras. Their code sits behind adapters and imports its libraries lazily. The core imports no network library, and a test runs the phase 1 suite with network access refused and the extras absent.

# Alternatives considered

- **Everything in the core install.** Simpler to describe, but larger and weaker offline guarantees.

# Consequences

- Packaging has extras to document and test.
- An enabled integration with a missing extra must produce a clear error.

# Related

- [Dependency Policy](/practices/dependency-policy.md)
- [Local-First Operation](/concepts/local-first.md)
