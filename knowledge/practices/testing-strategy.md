---
type: Practice
title: "Testing Strategy"
description: Which test layer owns which behaviour, and the fixtures and checks each layer relies on.
tags: [testing, fixtures, contracts, golden-files]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: ops
    resource: /architecture/system-architecture/operations.md
    title: Error Handling, Testing, and Technology Choices
  - id: det
    resource: /architecture/scanning-and-evidence/testing-and-acceptance.md
    title: Detector Testing, Maintenance, and Acceptance
---

# Layers

| Layer | Owns | Typical fixture |
|---|---|---|
| Domain | Identity normalization, precedence, status rules | Parametrized tables; no I/O |
| Detector | One detector's output for given files | Small repository trees compared with stored expected output |
| Adapter | SQLite, MCP, Sheets, provider behaviour at the boundary | Real temporary databases; a fake Sheets gateway; fake provider responses |
| Integration | A scan end to end | Real `git init` repositories in a temporary directory |
| Failure | Behaviour under errors | Injected faults mid-scan, locked database, unreadable files, schema mismatch |
| Contract | MCP tool lists and schemas | A committed snapshot compared in CI |

# Practices

- **Real repositories where Git matters.** Mocking Git configuration misses what real repositories do.
- **Determinism checks.** Scan twice, and with shuffled directory order, and compare outputs byte for byte.
- **Absence needs a test.** Claims such as read-only, no network, and no secret in an export are proven by tests that try
  to make them fail: a tree hash before and after, blocked sockets, sentinel values.
- **Failures are first-class.** Every guarantee about partial results and recovery has a fault-injection test.
- **Live services opt in.** Tests against real providers or a real spreadsheet run only when an environment variable
  supplies scoped credentials.[^ops]

# Related

- [Vertical Slices](/practices/vertical-slices.md)
- [Deterministic Extraction](/concepts/deterministic-extraction.md)

[^ops]: Error Handling, Testing, and Technology Choices
[^det]: Detector Testing, Maintenance, and Acceptance
