---
type: Decision
title: "Review Decisions Stay Local"
description: A reviewer's decision about a flagged candidate is local, generated state: it is stored only in the local index, never changes a repository or project, and is never synchronized or shown in a shared registry.
tags: [adr, review, local-only, sync]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T23:50:00Z }
sources:
  - id: own
    resource: /concepts/field-ownership.md
    title: Field Ownership
  - id: id
    resource: /concepts/project-identity.md
    title: Project Identity
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Vyasa raises review flags (duplicate checkouts, unresolved identity) for a person to judge. Where the person's judgment lives decides what can be shared and what a scan may touch. A decision recorded in a repository would write into it; one recorded in a shared sheet would expose one person's review to others and tie the local index to a service.

# Decision

A reviewer's decision (`open`, `dismissed`, `confirmed`, with an optional short note) is stored only in the local index, next to the flag it concerns. It is generated state owned by Vyasa on this machine. It is never written to a repository, never changes a project or its checkouts, and is never sent to or shown in a shared registry. Everything Vyasa stores in phase 1 is local; synchronization of any shared metadata is introduced only with the shared registry, and review decisions are excluded from it.

A decision applies to the evidence it was made on. If the flag's evidence later changes, the candidate is presented as `open` again.

# Alternatives considered

- **Sync decisions through the shared registry.** Shares judgment across devices, but exposes personal review notes and couples review to a service.
- **Store decisions in the repository.** Travels with the project, but writes into repositories.
- **Do not store decisions.** Flags would return unchanged after every scan.

# Consequences

- Another device does not see this device's decisions.
- The index stays usable offline and without any shared service.
- Rebuilding the index loses decisions unless they are preserved with the other durable state.

# Related

- [Project Identity](/concepts/project-identity.md)
- [Field Ownership](/concepts/field-ownership.md)
- [Stored Identity With Aliases](/decisions/stored-identity-with-aliases.md)
- [Local-First SQLite Index](/decisions/local-first-sqlite-index.md)
