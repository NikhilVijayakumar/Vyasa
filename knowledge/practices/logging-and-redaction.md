---
type: Practice
title: "Logging and Redaction"
description: Structured logging that is useful for diagnosis and safe to share.
tags: [logging, redaction, diagnostics, secrets]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: sec
    resource: /architecture/security-and-privacy/operations-and-response.md
    title: Logging, Configuration, Incident Response, and References
  - id: ops
    resource: /architecture/system-architecture/operations.md
    title: Error Handling, Testing, and Technology Choices
---

# What a log entry holds

A timestamp, a level, an event code, the run id, and the project id when relevant. Messages are short and structured so
logs can be filtered and compared.[^ops]

# Where logs go

Standard error and rotating files in the data directory. Standard output is never used when it carries a protocol.

# Redaction

Redact at the logging boundary so every call site is covered:

- credentials embedded in URLs;
- authorization headers and cookies;
- token shapes of the providers in use and private-key blocks;
- repository file contents and matched lines (not logged at all).

Prefer repository-relative paths. Absolute local paths may appear in local logs but are classified as sensitive, as are
exported diagnostics and backups.[^sec]

# Retention

Logs are bounded by file count and age. Detailed run history stays in the index and is bounded separately.

# Related

- [Security and Privacy](/architecture/security-and-privacy.md)
- [Error Handling](/practices/error-handling.md)

[^sec]: Logging, Configuration, Incident Response, and References
[^ops]: Error Handling, Testing, and Technology Choices
