---
type: Architecture
title: "Remote Discovery Views"
description: The provider boundary, a discovery run with pagination and failure, remote access states, and reconciliation with local data.
tags: [remote, github, bitbucket, pagination, reconciliation]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: rr
    resource: /architecture/remote-repositories.md
    title: Remote Repositories
  - id: disc
    resource: /architecture/remote-repositories/discovery-and-pagination.md
    title: Repository Discovery and Pagination
  - id: rec
    resource: /architecture/remote-repositories/identity-and-reconciliation.md
    title: Remote Identity and Reconciliation With Local Data
---

# Question

How are remote repositories listed and read, what can fail, and how do remote facts meet local ones?

# The provider boundary

```mermaid
C4Context
  title Remote discovery boundary
  Person(dev, "Developer", "Configures scopes and credentials; starts discovery")
  System(vyasa, "Vyasa", "Provider adapters, detectors, local index")
  System_Ext(gh, "GitHub API", "Repository listing and file contents")
  System_Ext(bb, "Bitbucket Cloud API", "Repository listing and file contents")
  System_Ext(cred, "Credential store", "Provider tokens")
  Rel(dev, vyasa, "Starts discovery")
  Rel(vyasa, cred, "Reads tokens at call time")
  Rel(vyasa, gh, "Read-only requests")
  Rel(vyasa, bb, "Read-only requests")
```

# One discovery run

```mermaid
sequenceDiagram
  autonumber
  actor Dev as Developer
  participant Run as Discovery run
  participant Ad as Provider adapter
  participant Api as Provider API
  participant Db as Local index
  Dev->>Run: discover configured scope
  Run->>Ad: list repositories
  loop each page
    Ad->>Api: request page
    alt rate limited
      Api-->>Ad: limit reached
      Ad-->>Ad: wait and retry within the bound
    else unauthorized or forbidden
      Api-->>Ad: access failure
      Ad-->>Run: access failure
    else page returned
      Api-->>Ad: repositories and next page
    end
  end
  Run->>Db: save results and mark coverage complete or incomplete
  opt inspection enabled
    Run->>Ad: read selected files at a pinned revision
    Ad->>Api: request file
    Run->>Db: save observations with remote evidence
  end
  Run-->>Dev: counts, coverage, failures
```

Repositories on pages that were not retrieved are never inferred to be absent, and no repository is cloned or checked out.

# Remote access states

```mermaid
stateDiagram-v2
  [*] --> Unknown
  Unknown --> Accessible: request succeeds
  Accessible --> RateLimited: provider limit reached
  Accessible --> Unavailable: temporary provider failure
  Accessible --> Forbidden: credential lost or revoked
  Accessible --> Missing: confirmed absent under the supported scope
  RateLimited --> Accessible: limit window passes
  Unavailable --> Accessible: provider recovers
  Forbidden --> Accessible: access restored
  Missing --> Accessible: reappears
```

These states are never collapsed into a single exists flag, and authorization or partial failures never produce `Missing`.

# Meeting local data

```mermaid
flowchart TD
  R[Remote observation] --> I{Matches a known project or repository?}
  I -- yes --> K[Attach as a separate remote observation with its revision]
  I -- no --> N[Create a remote-only record; no local path]
  I -- ambiguous --> U[Keep the ambiguity; flag for review]
  K --> D{Differs from the local observation?}
  D -- no --> S[Both stand]
  D -- yes --> O[Apply the field ownership policy; keep both observations]
  N --> V[Searchable; local checkout state reflects what was verified]
```

A newer remote observation never overwrites a local working-tree observation, and neither overwrites a shared human-managed field.

# Related

- [Remote Repositories](/architecture/remote-repositories.md)
- [Project Identity](/concepts/project-identity.md)
