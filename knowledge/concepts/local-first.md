---
type: Concept
title: "Local-First Operation"
description: The core works entirely on the local machine and offline; integrations extend it without becoming required.
tags: [principle, offline, phases, isolation]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: sys
    resource: /architecture/system-architecture/context-and-vision.md
    title: Context and Vision
  - id: evo
    resource: /architecture/system-architecture/decisions-and-evolution.md
    title: Decisions, Evolution, and Acceptance
---

# Definition

Everything in the first phase works without a network: scanning, indexing, queries, migrations, and status. Google
Sheets and remote providers are later additions that attach to the same core through adapters.[^sys]

# Rules

- The domain model and the index do not depend on any integration.
- An integration is optional to install, disabled until configured, and isolated: its failure does not stop local
  scanning or local queries.
- Local data stays local by default; sharing is an explicit, allowlisted act.
- Startup opens the existing index and does not scan or contact anyone.
- A later phase may add tables and adapters but must keep earlier data valid through migration.[^evo]

# Related

- [Explicit Operations](/concepts/explicit-operations.md)
- [Deployment View](/architecture/views/deployment-view.md)

[^sys]: Context and Vision
[^evo]: Decisions, Evolution, and Acceptance
