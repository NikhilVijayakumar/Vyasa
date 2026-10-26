---
type: Decision
title: "Read-Only Repository Access and Git Policy"
description: Scanning never changes a repository, and Git is read from files; a closed set of sanitized read-only commands is the only exception.
tags: [adr, security, git, read-only]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: git
    resource: /technologies/git-metadata.md
    title: Reading Git Metadata Safely
  - id: sec
    resource: /architecture/security-and-privacy/data-and-boundaries.md
    title: Data Classification, Filesystem, and Local Storage
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Repositories may be hostile. Running Git inside one can execute programs named in its configuration or hooks, and any write would violate the promise that scanning is read-only.

# Decision

Read remotes, HEAD, and refs by parsing `.git` files directly, without following includes. Permit a closed set of read-only plumbing commands only where files are not enough (for example reading the root commit), run with no system or global configuration, monitor and hook features disabled, a timeout, no pager or prompts, and fixed argument lists. Nothing from repository content is placed in a command. The only operation that writes into a repository is explicit draft generation, limited to one named file.

# Alternatives considered

- **Use the Git program freely.** Convenient, but an execution risk.
- **Embed a Git library for everything.** Avoids the program but adds a dependency and a large surface.

# Consequences

- A small amount of parsing code to maintain.
- A test proves a scan leaves a repository tree byte-identical.
- Commands that could fetch or change state are never used.

# Related

- [Reading Git Metadata Safely](/technologies/git-metadata.md)
- [Untrusted Content](/concepts/untrusted-content.md)
