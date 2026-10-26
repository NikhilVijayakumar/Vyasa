---
type: Technology
title: "Python Stack"
description: The language and library baseline, and the rule of preferring the standard library and keeping integrations optional.
tags: [python, pydantic, pytest, dependencies]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
stale_after: 2027-01-26T00:00:00Z
sources:
  - id: sys
    resource: /architecture/system-architecture/operations.md
    title: Error Handling, Testing, and Technology Choices
  - id: str
    resource: /architecture/system-architecture/structure.md
    title: Dependency Direction and Package Structure
---

# Baseline

| Concern | Choice |
|---|---|
| Language | Python 3.12 or newer |
| MCP | The official Python SDK |
| Validation | Pydantic models for inputs, outputs, and configuration |
| Persistence | SQLite through the standard `sqlite3` module |
| Tests | pytest |
| Paths | `pathlib`, with POSIX-style relative paths in stored evidence |

The least complex dependency set that meets the need wins.[^sys]

# Preferences

- **Standard library first.** `tomllib` for TOML, `json`, `sqlite3`, `pathlib`, `logging`, `hashlib`, `argparse`.
- **Safe parsing only.** YAML only through a loader that constructs plain data, with a size cap.
- **Optional extras for integrations.** Code for Sheets and providers sits behind installable extras so the core installs
  and runs without them.
- **Layer rule.** Adapters depend on application code, application on the domain, and the domain on neither.[^str]

# Related

- [System Architecture](/architecture/system-architecture.md)
- [Dependency Policy](/practices/dependency-policy.md)

[^sys]: Error Handling, Testing, and Technology Choices
[^str]: Dependency Direction and Package Structure
