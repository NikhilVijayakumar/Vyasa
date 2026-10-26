---
type: Practice
title: "Error Handling"
description: How failures are scoped, reported, and kept from becoming silent data loss or false completeness.
tags: [errors, partial-results, codes, diagnostics]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: ops
    resource: /architecture/system-architecture/operations.md
    title: Error Handling, Testing, and Technology Choices
  - id: err
    resource: /architecture/mcp-interface/errors-pagination-security.md
    title: Errors, Pagination, and Security
---

# Scope of a failure

| Scope | Example | Effect |
|---|---|---|
| Item | One file unreadable, one detector raised | Recorded against that item; everything else continues |
| Project | A repository cannot be inspected | That project is marked and skipped; other projects continue |
| Run | Configuration invalid, no usable root | The run fails with a reason; nothing is scanned |
| Request | Invalid tool argument, unknown project | A structured error for that request only |
| Integration | Provider down, credentials expired | Reported as that integration's failure; local operation is unaffected |

# Rules

- A partial result is reported as partial, with what failed or was skipped. It is never reported as complete.
- A limit reached, a timeout, or an access failure means *not assessed*, never *absent* or *deleted*.
- Errors carry a stable code and an actionable message; they never carry credentials, stack traces, or unnecessary
  absolute paths.
- Unexpected exceptions are logged with detail locally and returned as a generic internal error.
- A failure never destroys previously valid data; writes happen in transactions and failed ones roll back.[^ops]

# Error codes at the interface

`INVALID_ARGUMENT`, `NOT_FOUND`, `INDEX_UNAVAILABLE`, `INDEX_INCONSISTENT`, `CAPABILITY_UNAVAILABLE`,
`SOURCE_UNAVAILABLE`, `SCAN_INCOMPLETE`, `OPERATION_IN_PROGRESS`, and `INTERNAL_ERROR`.[^err]

# Related

- [Evidence and Provenance](/concepts/evidence-and-provenance.md)
- [MCP Views](/architecture/views/mcp-views.md)

[^ops]: Error Handling, Testing, and Technology Choices
[^err]: Errors, Pagination, and Security
