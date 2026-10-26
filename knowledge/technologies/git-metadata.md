---
type: Technology
title: "Reading Git Metadata Safely"
description: What Vyasa can learn from a repository's Git data without running code, and why running Git inside an untrusted repository is risky.
tags: [git, metadata, worktrees, submodules, security]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
stale_after: 2027-01-26T00:00:00Z
sources:
  - id: disc
    resource: /architecture/scanning-and-evidence/discovery-and-inspection.md
    title: Workspace Discovery and Repository Inspection
  - id: sec
    resource: /architecture/security-and-privacy/data-and-boundaries.md
    title: Data Classification, Filesystem, and Local Storage
---

# What can be read as files

| Data | Where | Notes |
|---|---|---|
| Remotes | `.git/config` | INI-style. Do not follow `include` directives; they pull in other files. |
| Current branch | `.git/HEAD` | A symbolic ref, or a commit id when detached. |
| Packed references | `.git/packed-refs` | Refs may be loose files or packed. |
| Shallow clone | `.git/shallow` | Present when history is truncated; the root commit may be unavailable. |
| Worktrees and submodules | a `.git` *file* | Contains `gitdir:` pointing elsewhere instead of a directory. |

Reading these needs no Git program and cannot trigger anything in the repository.[^disc]

# Why not just run git

Git reads the repository's own configuration. Some settings name programs to run (for example a file-system monitor or a
helper command), and hooks run on certain commands. A hostile repository can therefore turn an innocent-looking command
into code execution. Newer Git versions also refuse repositories owned by another user unless told otherwise.

# If a command is unavoidable

Allow only a fixed set of read-only plumbing commands, run with a sanitized environment (no system or global
configuration, no pager, no prompts), overrides that disable monitor and hook features, a timeout, and fixed argument
lists. Never build a command from repository content.[^sec]

# Related

- [Scanning and Evidence](/architecture/scanning-and-evidence.md)
- [Project Identity](/concepts/project-identity.md)

[^disc]: Workspace Discovery and Repository Inspection
[^sec]: Data Classification, Filesystem, and Local Storage
