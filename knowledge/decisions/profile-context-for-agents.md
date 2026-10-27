---
type: Decision
title: "Coding Agents Get Observed Facts and Differences as Context and Write the Profile Themselves"
description: A read-only context bundle gives a coding agent the deterministic facts, the profile as read, and the differences between them; Vyasa never launches an agent or writes the profile.
tags: [adr, profile, mcp, agents]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-28T12:00:00Z }
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

A coding agent working in a repository can write a good project profile if it has the facts the scanner already collected: languages, file counts, markers, frameworks, and repository identity. Without them it must rediscover everything. The agent must also be told what is already declared and where the declaration disagrees with what was observed. Vyasa is read-only, takes no part in language-model work, and starts nothing on its own.

# Decision

Vyasa returns one context bundle per project: the source and time of the observation, the checkout facts exactly as project details show them, the profile as read with its problems, a list of differences between the declared profile and the observations, and a short writer workflow that points to the profile guide. It is offered as an MCP tool, served from the stored observation, and as a command-line command that runs a live read-only scan of one checkout into a temporary in-memory index that is discarded, so a repository need not be indexed and nothing is written to disk. The bundle contains no absolute path and no file text. The differences compare only where the observation supports a claim: something declared is reported as not detected only after a complete assessment, declared names the registry cannot match are reported as not comparable, and detected items are reported as undeclared only when the profile declares that category. Each difference is a finding for a person to review; it never changes the profile. The agent decides what to write and writes the file; Vyasa reads it on the next scan.

# Alternatives considered

- **Vyasa launches an agent in the repository.** Rejected: it breaks read-only scanning, explicit operations, and the rule that no model is part of the pipeline, adds cost, and gives repository content a path to an agent's instructions.
- **Command reads only the stored index.** Rejected: it forces a scan first and writes to the index.
- **Command scans and updates the real index.** Rejected: an unexpected index write from a context command.
- **Automatic correction of the profile from the differences.** Rejected: the profile is declared by its owner.
- **Compare paths declared in the profile with the file system.** Rejected for the stored context: it would need query-time file access.

# Consequences

- An agent starts from evidence instead of rediscovering it, and sees what is already declared.
- The two entry points show the same shape, with the source named, so fresh and stored facts are never confused.
- The temporary index means the command reuses the whole scan pipeline without writing anywhere.
- The profile remains declared by its owner and reviewed by people.

# Related

- [Profile Schema Version 2 Declares the Project in Depth as Nested Tables](/decisions/profile-schema-v2-full-template.md)
- [Canonical Profile and Draft Handling](/decisions/canonical-profile-and-draft.md)
- [Observation Freshness Without Query-Time I/O](/decisions/observation-freshness-without-query-time-io.md)
- [Read-Only Access and Git Policy](/decisions/read-only-access-and-git-policy.md)
