---
type: Architecture
title: "Scan Pipeline Views"
description: Component, dynamic, and decision views of workspace discovery, inspection, detection, and incremental reuse.
tags: [c4, scanning, pipeline, incremental]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: scan
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
  - id: disc
    resource: /architecture/scanning-and-evidence/discovery-and-inspection.md
    title: Workspace Discovery and Repository Inspection
  - id: inc
    resource: /architecture/scanning-and-evidence/incremental-and-partial.md
    title: Incremental, Full, and Partial Scans
---

# Question

How do repository files become stored observations, what can go wrong along the way, and when may earlier results be reused?

# Components of the scanner

```mermaid
C4Component
  title Scanner components
  Container_Boundary(scanner, "Scanner") {
    Component(cfg, "Configuration Manager", "Application", "Validated roots, exclusions, limits, enabled detectors")
    Component(disc, "Workspace Discovery", "Application", "Candidates and per-candidate outcomes")
    Component(insp, "Repository Inspector", "Application", "Bounded file inventory and safe reads")
    Component(reg, "Detector Registry", "Application", "Versioned deterministic detectors")
    Component(ident, "Identity Resolver", "Domain", "Project and repository identity")
    Component(norm, "Normalizer and Ownership Policy", "Domain", "Statuses, precedence, conflicts")
    Component(idx, "Project Index Service", "Application", "Run lifecycle, transactions, freshness")
  }
  ContainerDb(db, "Project index", "SQLite")
  System_Ext(repos, "Repositories", "Read-only")
  Rel(idx, cfg, "Loads")
  Rel(idx, disc, "Starts")
  Rel(disc, repos, "Lists directories")
  Rel(idx, insp, "Inspects each eligible candidate")
  Rel(insp, repos, "Reads recognized files")
  Rel(insp, reg, "Feeds inventory and bytes")
  Rel(reg, norm, "Observations with evidence")
  Rel(idx, ident, "Resolves identity")
  Rel(norm, db, "Resolved values, history, conflicts")
  Rel(ident, db, "Identity mappings and events")
  Rel(idx, db, "Runs and item results")
```

# One full scan

```mermaid
sequenceDiagram
  autonumber
  participant Idx as Project Index Service
  participant Disc as Workspace Discovery
  participant Insp as Repository Inspector
  participant Reg as Detector Registry
  participant Id as Identity Resolver
  participant Norm as Normalizer and Ownership Policy
  participant Db as SQLite Persistence Adapter
  Idx->>Db: record run as running
  Idx->>Disc: discover candidates
  Disc-->>Idx: candidates with outcomes
  loop each eligible candidate
    Idx->>Insp: inspect within limits
    Insp-->>Idx: inventory
    Idx->>Reg: run detectors
    Reg-->>Idx: observations or item errors
    Idx->>Id: resolve identity from evidence
    Idx->>Norm: apply precedence and ownership
    Idx->>Db: commit this project in one transaction
  end
  Idx->>Db: close run with status and counts
```

A failure in one candidate becomes an item result; the loop continues and the run ends `partial`.

# What may a candidate become?

```mermaid
flowchart TD
  A[Directory under a configured root] --> B{Excluded?}
  B -- yes --> X1[excluded]
  B -- no --> C{Symlink or outside roots?}
  C -- yes --> X2[skipped by policy]
  C -- no --> D{Readable?}
  D -- no --> X3[inaccessible]
  D -- yes --> E{Git root or recognized marker?}
  E -- no --> X4[not a recognized project]
  E -- yes --> F{Metadata well formed?}
  F -- no --> X5[malformed]
  F -- yes --> G{Identity decidable?}
  G -- no --> X6[identity unresolved]
  G -- yes --> X7[discovered and eligible]
```

# When may earlier results be reused?

```mermaid
flowchart TD
  S[Project and detector] --> V{Detector version and options unchanged?}
  V -- no --> R[Recompute]
  V -- yes --> I{Declared input files unchanged?}
  I -- no --> R
  I -- yes --> H{Git HEAD, remote, or identity changed?}
  H -- yes --> R
  H -- no --> P{Profile changed?}
  P -- yes --> R
  P -- no --> U[Reuse prior result]
  R --> W[Write new observation and keep the previous one]
```

Reuse is never justified by an unchanged timestamp alone when any other invalidation evidence disagrees.

# Related

- [Scanning and Evidence](/architecture/scanning-and-evidence.md)
- [C4 System Views](/architecture/c4-system-views.md)
