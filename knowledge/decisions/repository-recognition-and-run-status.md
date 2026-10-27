---
type: Decision
title: "Repository Recognition and Discovery Run Status"
description: A Git repository is recognized from its marker without running Git, every candidate gets one closed outcome, and a run is partial whenever anything was not fully assessed.
tags: [adr, discovery, git, status]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T18:00:00Z }
sources:
  - id: disc
    resource: /architecture/scanning-and-evidence/discovery-and-inspection.md
    title: Workspace Discovery and Repository Inspection
  - id: partial
    resource: /decisions/partial-results-never-imply-absence.md
    title: Partial Results Never Imply Absence
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Discovery walks directories that contain repository-controlled content. It must recognize Git repositories without executing anything, tell ordinary repositories from submodules and linked worktrees, say what could not be assessed, and never present a scan that skipped something as complete.

# Decision

A directory is a Git repository candidate when it contains a `.git` entry.

- A `.git` directory with a `HEAD` file is a repository. Without `HEAD` it is malformed.
- A `.git` file must start with a `gitdir:` line, read from at most the first kilobyte. If the target path contains a `worktrees` segment the candidate is a linked worktree; if it contains a `modules` segment, a submodule; otherwise a repository whose Git directory lives elsewhere. A file without that line is malformed, and one that cannot be read is inaccessible.
- A `.git` entry that is a symbolic link or junction is skipped by policy.

Each candidate has exactly one outcome from the closed set: eligible, excluded, inaccessible, malformed, or skipped by policy. Ordinary directories are not candidates and are not listed. Excluded directories are counted, not listed. Nothing is run and no repository file other than a `.git` pointer file is opened.

A run is complete when every directory in scope was assessed, partial when any candidate is inaccessible, malformed, or skipped by policy (including a directory not entered because of the depth limit or because it is a link), and failed when the root itself is missing, not a directory, or unreadable. Issues are listed up to a fixed bound; counts always cover all of them.

A repository found inside another is a separate candidate. Submodules and linked worktrees are reported with their kind and are neither merged into nor counted as separate projects by discovery; that is decided by identity resolution.

# Alternatives considered

- **Ask Git (`git rev-parse`).** Authoritative, but it runs repository-influenced code paths and needs Git installed.
- **Treat any directory with a manifest as a project.** Out of scope here; it needs an agreed marker list.
- **Count a link or depth skip as complete.** Quieter output, but it would present an unassessed area as scanned.
- **List every non-repository directory.** Complete, but unbounded and of no use to a reader.

# Consequences

- A tree containing links or deeper directories reports partial every time; the counts say why.
- Recognition does not prove a repository is intact; it proves a plausible marker.
- Identity resolution must decide what to do with submodules and linked worktrees.

# Related

- [Workspace Discovery and Repository Inspection](/architecture/scanning-and-evidence/discovery-and-inspection.md)
- [Scan Limits and Symlink Defaults](/decisions/scan-limits-and-symlink-defaults.md)
- [Read-Only Repository Access and Git Policy](/decisions/read-only-access-and-git-policy.md)
- [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md)
- [Untrusted Content](/concepts/untrusted-content.md)
