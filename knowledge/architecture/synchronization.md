---
type: Architecture
title: "Vyasa (व्यास) — Synchronization"
description: How shared project metadata is synchronized through the Google Sheets registry.
tags: [sync, google-sheets, phase-2]
status: draft
generated: { by: human:nikhil-vijayakumar, at: 2026-10-26T00:00:00Z }
---
# Vyasa (व्यास) — Synchronization

Related architecture:

- [system-architecture](/architecture/system-architecture.md)
- [data-model](/architecture/data-model.md)
- [scanning-and-evidence](/architecture/scanning-and-evidence.md)
- [mcp-interface](/architecture/mcp-interface.md)
- [local-storage](/architecture/local-storage.md)

## Summary

This document defines how Vyasa synchronizes project metadata between a local SQLite index and a shared Google Sheets registry.

## Parts

This concept is split into parts so each can be read on its own. Section numbers in the table are those of the original document, so references such as "§9.11" resolve to the part that contains them.

| Part | Sections | What it answers |
|---|---|---|
| [Principles and Architecture](synchronization/principles-and-architecture.md) | §1–3 | Why and how the registry is synchronized, its design principles, and its components. |
| [Registry Structure, Ownership, and Identity](synchronization/registry-and-ownership.md) | §4–6 | The three registry tabs, which side owns each field, and how projects are matched across devices. |
| [Synchronization Modes and Workflow](synchronization/modes-and-workflow.md) | §7–8 | Export, import, and bidirectional modes and the step-by-step synchronization workflow. |
| [Conflicts, Upserts, and Idempotency](synchronization/conflicts-and-idempotency.md) | §9–10 | Detecting and resolving conflicts, and making repeated runs converge. |
| [Change Detection and Deletion](synchronization/change-detection-and-deletion.md) | §11–12 | Detecting what changed since the last sync, and why records are retired rather than deleted. |
| [Authentication, API Limits, and Cross-Device Behaviour](synchronization/auth-limits-and-devices.md) | §13–15 | Google authentication options, quotas and retries, and behaviour across devices. |
| [Results, MCP Interaction, and Observability](synchronization/results-and-mcp.md) | §16–18 | Run result reporting, how sync relates to MCP, and diagnostics. |
| [Testing, Sequence, and Acceptance](synchronization/testing-and-acceptance.md) | §19–23 | Test strategy, implementation order, open decisions, and acceptance criteria. |
