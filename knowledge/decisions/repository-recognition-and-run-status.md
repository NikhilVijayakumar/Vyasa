---
type: Decision
title: "Repository Recognition and Discovery Run Status"
description: A project is recognized from Git or a manifest, without running anything; it is a boundary Vyasa does not enter; every candidate gets one closed outcome.
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

Discovery walks directories that contain repository-controlled content. Not every project has Git (an Unreal project keeps it in a source folder), and most projects hold no other project, so walking inside them only finds noise: on one real workspace it produced 868 depth skips and 310 link skips. Discovery must recognize projects without executing anything, tell ordinary repositories from submodules and linked worktrees, say what could not be assessed, and never present a scan that skipped something as complete.

# Decision

A directory is a project when it has either of these, checked in this order:

1. **A `.git` entry.** Recognized as below. Manifests found beside it are recorded.
2. **A manifest:** `pyproject.toml`, `requirements.txt`, `setup.py`, `package.json`, `Cargo.toml`, `go.mod`, or any file ending in `.uproject`, compared without regard to case. The project has no Git at its root; Git is looked for in its immediate child directories (Unreal keeps it in `Source`) and recorded as that child's name, or as none.
Source files, a README, or documentation alone are not enough. A documentation-only repository is tracked when it has Git (item 1), and ignored otherwise.

A project is a boundary: Vyasa recognizes it and does not walk inside it, unless nested repositories are explicitly enabled. Folders that are not projects are searched, down to a depth limit.

How a `.git` entry is read:

- A `.git` directory with a `HEAD` file is a repository. Without `HEAD` it is malformed.
- A `.git` file must start with a `gitdir:` line, read from at most the first kilobyte. If the target ends in `<git directory>/worktrees/<name>` the candidate is a linked worktree; if the target contains `.git/modules` it is a submodule; otherwise it is a repository whose Git directory lives elsewhere. A directory merely named `modules` or `worktrees` elsewhere in the path proves nothing. A file without that line is malformed, and one that cannot be read is inaccessible.
- A `.git` entry that is a symbolic link or junction is skipped by policy.

Each candidate has exactly one outcome from the closed set: eligible, excluded, inaccessible, malformed, or skipped by policy. Ordinary directories are not candidates and are not listed. Excluded directories are counted, not listed. Nothing is run and no repository file other than a `.git` pointer file is opened.

A run is failed when the root itself is missing, not a directory, or unreadable; partial when any candidate is inaccessible or malformed; and complete otherwise. A directory skipped by policy, because of the depth limit or because it is a link, never changes the status. It is reported in a warning for its reason, with the number skipped, a few examples, and advice, so the person decides whether to add an ignore entry to the repository, raise the limit, or accept it. Failures are listed up to a fixed bound; counts always cover all of them.

When nested repositories are enabled, a project found inside another is a separate candidate and the two are never merged. A submodule is found only in that mode; a linked worktree is a sibling directory and is found normally. Both are reported with their kind; identity resolution decides what they mean.

# Alternatives considered

- **Ask Git (`git rev-parse`).** Authoritative, but it runs repository-influenced code paths and needs Git installed.
- **Git only.** Simple, but it misses Unreal projects with Git in a child folder and every project that is not under version control.
- **Source files, or a README with docs, as evidence of a project.** A scripts folder or a folder of notes would become a project; a manifest or Git is a clearer signal.
- **Walk inside every project to find nested ones.** Complete, but most projects hold none, and it costs time and produces noise.
- **Mark the run partial for every skip.** Honest, but deeper directories exist in every real workspace (3,132 at depth 6 on one), so the status would always read partial and stop meaning anything.
- **List every non-repository directory.** Complete, but unbounded and of no use to a reader.

# Consequences

- Skipped directories are visible in warnings and counts but cannot hide behind a complete status without being reported.
- Recognition does not prove a repository is intact; it proves a plausible marker.
- A documentation-only folder that is not under Git is not tracked, by the owner's choice.
- Projects nested inside projects, and submodules, are invisible by default and appear only when enabled.
- Identity resolution must decide what to do with submodules and linked worktrees.

# Related

- [Workspace Discovery and Repository Inspection](/architecture/scanning-and-evidence/discovery-and-inspection.md)
- [Scan Limits and Symlink Defaults](/decisions/scan-limits-and-symlink-defaults.md)
- [Read-Only Repository Access and Git Policy](/decisions/read-only-access-and-git-policy.md)
- [Partial Results Never Imply Absence](/decisions/partial-results-never-imply-absence.md)
- [Untrusted Content](/concepts/untrusted-content.md)
