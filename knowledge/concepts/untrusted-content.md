---
type: Concept
title: "Untrusted Content"
description: Anything read from a repository, provider, or spreadsheet is data to be bounded and sanitized, never instructions or code.
tags: [security, untrusted, injection, principle]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: sec
    resource: /architecture/security-and-privacy/objectives-scope-threats.md
    title: Objectives, Scope, and Threat Model
  - id: mcp
    resource: /architecture/security-and-privacy/mcp-and-credentials.md
    title: MCP Security and Credential Management
---

# Definition

Repository files, manifests, profiles, README text, provider responses, and spreadsheet cell values come from outside the
trust boundary. A repository may be malicious or simply wrong; a provider may return something unexpected.[^sec]

# Rules

- **Never execute.** No script, build file, package hook, workflow, or agent instruction found in content is run.
- **Never follow as authority.** A path or URL named in content grants no access beyond the configured roots and scopes.
- **Bound before parsing.** Apply size, depth, count, and time limits; a limit reached means skipped, not absent.
- **Parse safely.** Use parsers that do not evaluate code or expand without bound; reject what exceeds the limits.
- **Sanitize on the way out.** Returned text is typed, length-capped, stripped of control and bidirectional characters,
  and never merged into tool descriptions.
- **Store the minimum.** Keep locations and fingerprints, not document bodies or matched lines.

# Why

Text that reaches a coding agent can attempt to steer it. Vyasa cannot make text trustworthy, so it keeps it inert,
labelled as data, and bounded.[^mcp]

# Related

- [Security Views](/architecture/views/security-views.md)
- [Deterministic Extraction](/concepts/deterministic-extraction.md)

[^sec]: Objectives, Scope, and Threat Model
[^mcp]: MCP Security and Credential Management
