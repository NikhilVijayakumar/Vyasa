---
type: Practice
title: Vertical Slices
description: Implementation tasks deliver small, independently verifiable increments of behaviour.
tags: [delivery, tasks, testing, tdd]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
---

# Rule

A task is a vertical slice: it delivers one observable behaviour through
every layer it needs, ships with its automated checks, and leaves the
codebase working. A layer-by-layer plan (models, then repository, then tool,
then tests) is not a slice: every intermediate step is unusable and
verification is deferred to the end.

# Shape of a slice

- **Outcome:** one behaviour a caller can observe, stated as acceptance criteria.
- **Path:** the minimum code through each layer to make that behaviour real.
- **Checks:** tests written first (Red–Green–Refactor) that fail if the behaviour breaks.
- **Evidence:** the command run and its result, recorded when the slice is marked done.

A task that is pure enabling infrastructure is labelled **prerequisite**, not
presented as a slice.

# Examples

1. **Discover one project.** Given a workspace root containing one Git
   repository, the scan identifies it and records its identity with evidence.
   Checks cover a missing root and an unreadable directory.
2. **Detect documentation.** Given an indexed repository, README presence is
   recorded with provenance, distinguishing `not_detected` from
   `inaccessible`.
3. **Query through MCP.** Given indexed metadata, an agent requests the
   project and receives structured results with evidence and status.

# Related

- [Evidence and Provenance](/concepts/evidence-and-provenance.md)
- [MCP Interface](/architecture/mcp-interface.md)
