---
type: Decision
title: "Scan Limits and Symlink Defaults"
description: Conservative, configurable limits bound every scan, and directory symlinks are not followed by default.
tags: [adr, scanning, limits, symlinks]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: disc
    resource: /architecture/scanning-and-evidence/discovery-and-inspection.md
    title: Workspace Discovery and Repository Inspection
  - id: sec
    resource: /architecture/security-and-privacy/data-and-boundaries.md
    title: Data Classification, Filesystem, and Local Storage
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Unbounded traversal and parsing let one large or hostile directory consume time and memory, and symlinks can lead out of the configured roots.

# Decision

Defaults, all configurable: traversal depth 8; 1 MiB per file (256 KiB for profiles); 5,000 inventory entries per project; 60 seconds per project. Hitting a limit gives a skipped-by-policy outcome naming the limit, never a claim that something is absent. Directory symlinks are not followed; when enabled, each target is resolved and rejected if it leaves the configured roots, and cycles are broken. The numbers are starting points to validate against representative workspaces.

# Alternatives considered

- **No limits.** Simple, but unsafe.
- **Follow symlinks by default.** Convenient, but allows escape and cycles.

# Consequences

- Very large files and deep trees are skipped and reported.
- Limits must be validated and may change.
- Tests need symlink-escape and cycle fixtures.

# Related

- [Workspace Discovery and Repository Inspection](/architecture/scanning-and-evidence/discovery-and-inspection.md)
