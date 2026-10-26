---
type: Architecture
title: "Security Views"
description: Trust zones and what may cross them, and how each documented threat is met by a control.
tags: [security, trust-boundary, threats, controls]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: sec
    resource: /architecture/security-and-privacy.md
    title: Security and Privacy
  - id: thr
    resource: /architecture/security-and-privacy/objectives-scope-threats.md
    title: Objectives, Scope, and Threat Model
  - id: dat
    resource: /architecture/security-and-privacy/data-and-boundaries.md
    title: Data Classification, Filesystem, and Local Storage
---

# Question

Which inputs are untrusted, which data may leave the machine, and which control answers each documented threat?

# Trust zones

```mermaid
flowchart TB
  subgraph UT["Untrusted input"]
    REPO[Repository files, manifests, profiles]
    RESP[Provider responses and remote files]
    CELLS[Spreadsheet values]
  end
  subgraph TZ["Trusted local zone: current user only"]
    SCAN[Scanner<br/>read-only, bounded, nothing executed]
    IDX[(Project index<br/>no credentials)]
    SRV[MCP server<br/>validated, read-only, stdio]
    CRED[Credential store]
    LOG[Logs<br/>redacted]
  end
  subgraph AG["Agent boundary"]
    CL[MCP client]
  end
  subgraph CLD["Cloud boundary: explicit and configured"]
    GS[Google Sheets]
    API[GitHub and Bitbucket]
  end
  REPO -->|bounded reads| SCAN
  RESP -->|size-capped, validated| SCAN
  CELLS -->|schema-validated| SCAN
  SCAN --> IDX
  IDX --> SRV
  SRV -->|typed, capped, sanitized| CL
  CRED -->|at call time| SCAN
  SCAN -->|allowlist only| GS
  SCAN -->|read-only requests| API
  SCAN --> LOG
  SRV --> LOG
```

Everything entering the trusted zone is data. Everything leaving it is allowlisted, minimized, or sanitized. A connection
shown here is permitted only when its phase, configuration, and access policy allow it.

# Data classes and where each may go

```mermaid
flowchart LR
  P[Public: public repository URL, project name] --> SH[May be shared]
  I[Internal project metadata: purpose, technologies, documentation status] --> LS[Local by default; approved fields may be shared]
  S[Sensitive operational: local paths, internal URLs, private relationships] --> LR[Local by default; review before sharing]
  X[Secret: tokens, keys, passwords] --> NV[Never stored as values, logged, or exported]
  C[Repository content: configuration, documents, source] --> IN[Inspect when needed; keep no raw content]
```

# Threats and controls

```mermaid
flowchart LR
  T1[Crafted repository: symlinks, paths, hostile text] --> C1[Roots and path checks, no symlink following by default, nothing executed, text returned as inert data]
  T2[Over-permissioned or compromised MCP client] --> C2[Schema validation, no path arguments, read-only tools, no implicit external effects]
  T3[Malicious or unexpected API response] --> C3[Size and time limits, schema validation, treated as data]
  T4[Leaked or over-scoped credentials] --> C4[Least-privilege scopes, credential store, redaction, never in the index or logs]
  T5[Wrong spreadsheet sharing] --> C5[Explicit allowlist, minimal sharing, documented access and revocation]
  T6[Path or serialization bugs] --> C6[Canonicalization, parameterized SQL, fixture tests]
  T7[Backups, logs, or shared folders exposing data] --> C7[User-only permissions, same classification for backups and diagnostics]
```

# Related

- [Security and Privacy](/architecture/security-and-privacy.md)
- [Deployment View](/architecture/views/deployment-view.md)
