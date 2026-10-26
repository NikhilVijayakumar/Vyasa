---
type: Concept
title: Field Ownership
description: Every mutable field has one authoritative owner; other processes read or cache it but never overwrite it silently.
tags: [ownership, source-of-truth, synchronization, precedence]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T00:00:00Z }
sources:
  - id: scan
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
  - id: sync
    resource: /architecture/synchronization.md
    title: Synchronization
---

# Definition

Four kinds of statement are kept apart: what a **project declares**, what a
**scanner observes**, what a **person manages centrally**, and what Vyasa
**calculates** for convenience. Each field belongs to exactly one owner
category, and the owner decides the value.[^scan]

# Owner categories

| Category | Owner | Typical content |
|---|---|---|
| Repository-owned | Project maintainers | Declared purpose, conventions, canonical profile |
| Repository-observed | The repository, seen by Vyasa | Manifests, README presence, Git remote |
| Vyasa-generated | Vyasa | Index, scan results, evidence inventory |
| Portfolio-owned | A portfolio maintainer | Tracking level, priority, notes |
| Provider-owned | An external platform | Provider repository ID, visibility |
| Machine-local | This device or installation | Clone paths, workspace roots, configuration |
| Derived | A deterministic rule | Related-project matches, completeness indicators |

# Rules

- A process never overwrites a field owned by another source without an
  explicit, documented authorization rule.
- Conflicts are decided by ownership, not by timestamp alone; an unresolved
  conflict stays visible as `conflicting`.
- Machine-local fields never leave the device.
- A generated draft stays separate from the canonical value until a person
  promotes it.
- Derived values are reproducible and are not presented as authored facts.
- A failed scan or sync never destroys previously valid information.

**Synchronization shares information; it does not transfer ownership.**[^sync]

# Related

- [Evidence and Provenance](/concepts/evidence-and-provenance.md)
- [Synchronization](/architecture/synchronization.md)

[^scan]: Scanning and Evidence
[^sync]: Synchronization
