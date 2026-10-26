---
type: Architecture
title: "Vyasa (व्यास) — Remote Repository Discovery"
description: Discovery of GitHub and Bitbucket repositories through provider APIs without cloning.
tags: [github, bitbucket, phase-3]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
---
# Vyasa (व्यास) — Remote Repository Discovery

Related architecture:

- [system-architecture](/architecture/system-architecture.md)
- [data-model](/architecture/data-model.md)
- [scanning-and-evidence](/architecture/scanning-and-evidence.md)
- [mcp-interface](/architecture/mcp-interface.md)
- [local-storage](/architecture/local-storage.md)
- [synchronization](/architecture/synchronization.md)

## Summary

This document defines how Vyasa discovers repositories and inspects supported metadata directly from remote Git providers without cloning or checking out repositories.

## Parts

This concept is split into parts so each can be read on its own. Section numbers in the table are those of the original document, so references such as "§9.11" resolve to the part that contains them.

| Part | Sections | What it answers |
|---|---|---|
| [Purpose, Goals, Position, and Providers](remote-repositories/purpose-and-position.md) | §1–4 | Why remote discovery exists, its goals and non-goals, where it sits in the architecture, and provider support. |
| [Configuration, Scope, and Authentication](remote-repositories/config-and-auth.md) | §5–6 | How scopes are configured and how provider credentials are handled. |
| [Repository Discovery and Pagination](remote-repositories/discovery-and-pagination.md) | §7–8 | How repositories are enumerated and how pages and partial coverage are tracked. |
| [Remote File Inspection and Detectors](remote-repositories/inspection-and-detectors.md) | §9–10 | Which files are read through APIs and how the deterministic detectors apply to them. |
| [Remote Identity and Reconciliation With Local Data](remote-repositories/identity-and-reconciliation.md) | §11–12 | Matching remote repositories to projects, and reconciling remote with local observations. |
| [Sheets Integration and SQLite Persistence](remote-repositories/sheets-and-persistence.md) | §13–14 | What remote data may reach the registry and how it is stored locally. |
| [Incremental Discovery, Limits, and Untrusted Content](remote-repositories/caching-limits-security.md) | §15–17 | Caching and refresh, rate limits and failures, and handling untrusted remote content. |
| [MCP Interface, Testing, and Acceptance](remote-repositories/mcp-testing-acceptance.md) | §18–23 | Remote operations in MCP, test strategy, implementation sequence, decisions, and acceptance. |
