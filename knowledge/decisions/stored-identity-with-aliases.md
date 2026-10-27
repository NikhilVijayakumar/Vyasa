---
type: Decision
title: "Stored Identity With Aliases"
description: A project's identifier is created once from the strongest evidence and stored; later evidence adds aliases that resolve to it.
tags: [adr, identity, aliases]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: id
    resource: /concepts/project-identity.md
    title: Project Identity
  - id: dm
    resource: /architecture/data-model/checkout-and-identity.md
    title: Local Checkout and External Identity
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Identifiers must survive directory moves, remote renames, and transfers, and must be matchable across devices. A pure function of the remote changes when the remote does; a function of the path changes when the directory moves.

# Decision

Create the identifier once, from the first strongest evidence: a verified provider id, else a normalized remote, else a provisional path-based identity for a repository with no usable remote (a local project). Store it and never recompute it. Later evidence (a renamed remote, a provider id) is stored as an alias that resolves to the same identifier. Lookup order on rediscovery: alias, then known checkout path. Every change to a mapping is recorded as an identity event. A project may hold several checkouts, and its state follows them: active while any checkout is, else inaccessible while any is, else missing. When the alias and the checkout path point at different projects, nothing is merged or moved; an `identity_conflict` event is recorded, the project becomes `ambiguous`, and an `identity_unresolved` review flag is raised with both pieces of evidence. A project with more than one active checkout at the end of a run gets a `duplicate_checkout` flag. Flags are generated state: one per project and kind, opened and cleared by scans (each change an identity event), never resolved by merging or deleting. A repository with no usable remote (none, ambiguous, a local path, or an unreadable Git entry) is a local project: provisional, matched by path only, not flagged. Moving it creates a new project and leaves the old one missing. No Git program is run and no root commit is read.

# Alternatives considered

- **Pure function of the normalized remote.** Stateless, but a rename creates a new project.
- **Hash of the path.** Breaks on any move.
- **An identifier file written into the repository.** Stable, but writes into repositories.
- **Random identifier only.** Stable locally, impossible to match across devices.

# Consequences

- An alias table and an identity event log are needed.
- Cross-device matching uses aliases, not identifiers alone.
- Forks stay distinct because they have different remotes.
- Local projects do not match across devices or survive a move; this is accepted.

# Related

- [Project Identity](/concepts/project-identity.md)
- [Remote Identity Normalization](/decisions/remote-identity-normalization.md)
