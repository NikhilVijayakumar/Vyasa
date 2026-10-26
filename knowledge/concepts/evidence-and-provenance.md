---
type: Concept
title: Evidence and Provenance
description: Every value Vyasa reports carries the evidence it was derived from and an explicit observation status.
tags: [evidence, provenance, observation-status, scanning]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
sources:
  - id: scanning
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
  - id: mcp
    resource: /architecture/mcp-interface.md
    title: MCP Interface
---

# Definition

Vyasa never reports a fact on its own: each value is paired with the
evidence that produced it and a status saying how much is known.[^scanning]
A smaller index with honest uncertainty is preferred over a larger one with
unsupported claims.

# Evidence

An evidence record identifies, where applicable: the source category, the
repository, the repository-relative path, the field or key, the revision,
when it was observed, and the detector id and version.[^mcp] Fields that
cannot be established are left empty, never invented.

# Observation status

| Status | Meaning |
|---|---|
| `observed` | A supported detector found evidence for the value |
| `declared` | An authoritative source states the value explicitly |
| `not_detected` | A complete inspection found no matching indicator |
| `unknown` | Available evidence cannot establish the value |
| `unsupported` | The source or format is not supported |
| `inaccessible` | The source could not be inspected |
| `stale` | A prior observation may no longer match its source |
| `conflicting` | Observations disagree and cannot yet be resolved |

Missing is not false: an absent file is `not_detected` only after a complete
inspection; an unreadable one is `inaccessible`.

# Related

- [Scanning and Evidence](/architecture/scanning-and-evidence.md) — detectors and resolution rules
- [Data Model](/architecture/data-model.md) — how observations and evidence are stored

[^scanning]: Scanning and Evidence
[^mcp]: MCP Interface
