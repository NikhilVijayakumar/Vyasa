---
type: Decision
title: "A Long-Form Project Report Lives in the Repository, Is Indexed as a Bounded Copy, and Is Written by a Coding Agent"
description: A markdown report at a fixed path, split into fixed sections, is read by the scan with size limits and served from the index; Vyasa supplies the template and never writes the report or calls a model.
tags: [adr, report, mcp, agents, profile]
status: stable
generated: { by: claude-code/sonnet-5.5, at: 2026-10-28T14:00:00Z }
---

# Status

Accepted. Implemented and verified.

# Context

The profile is short, structured, and bounded on purpose. A coding agent can understand much more about a repository than those fields hold, and that understanding is lost when the session ends. Vyasa must stay deterministic and must not call a model, so the reading has to be done by the agent that is already working in the repository, and the result has to be durable, queryable from another repository, and safe to treat as untrusted text.

# Decision

The report is one markdown file at `.vyasa/project-report.md`, beside the profile. Vyasa serves a template over MCP that names the path, the fixed second-level sections, their purpose, the limits, and the rules for the writer. The agent combines the deterministic context Vyasa already provides with its own inspection and writes the file. The scan reads it as text only, never through a link, at most the file limit (default 256 KiB), keeps sections whose headings are in the template up to the section limit (default 16 KiB) each, drops and reports the rest, and stores the sections with the checkout, the content hash, and the scan time. MCP serves the stored copy, marked as declared by the repository and as untrusted text, whole or by section; `get_project` shows only the status and section sizes. A missing report is ordinary, and a failed read never removes other stored data.

The two limits are settings in `config.toml` under `report`, validated against fixed bounds (file 16 to 4096 KiB, section 1 to 1024 KiB and not above the file limit). They are per installation; the scan records the limits it applied so the MCP server, which reads no configuration, can show them in the template.

# Alternatives considered

- **Raise the profile limits.** Rejected: it weakens the bounded, validated profile and mixes summary and detail.
- **Serve only the path and hash and let the agent read the file.** Rejected: a project could not be understood from another repository.
- **Have Vyasa call a model to write the report.** Rejected: it contradicts deterministic extraction and adds credentials and network access.
- **A free-form report with no fixed sections.** Rejected: nothing could be fetched in part, and the scan would have to parse prose.

# Consequences

- A failed or invalid read keeps the earlier sections and says which read they came from; a missing file removes them.

- A project can be described in depth without a second source of truth for what the scanner owns.
- The report can be wrong or stale; it is labelled declared, and a staleness check is a later change.
- The index grows by at most the configured file limit per checkout, never more than 4096 KiB.
- The configuration gains its first tunable setting beyond workspace roots; its bounds are explicit and enforced.
- Report text is returned as data and never as instructions.

# Related

- [Profile Schema Version 2 Is the Full Template](profile-schema-v2-full-template.md)
- [Coding Agents Get Observed Facts and Differences as Context](profile-context-for-agents.md)
- [Deterministic Extraction Without a Language Model](deterministic-extraction-without-llm.md)
