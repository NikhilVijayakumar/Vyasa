---
type: Practice
title: "Configuration"
description: Explicit, validated settings with safe defaults, where a missing or malformed value never widens access.
tags: [configuration, defaults, validation, fail-closed]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: sec
    resource: /architecture/security-and-privacy/operations-and-response.md
    title: Logging, Configuration, Incident Response, and References
  - id: scan
    resource: /architecture/scanning-and-evidence/discovery-and-inspection.md
    title: Workspace Discovery and Repository Inspection
---

# Rules

- **Explicit.** Workspace roots, exclusions, symlink policy, limits, enabled integrations, and scopes are written down by
  the user. There are no implied default roots.
- **Validated before use.** A configuration is parsed and checked as a whole; an invalid one is reported and not applied.
- **Fail closed.** A missing or malformed security-relevant setting takes the stricter default and is reported. It never
  silently allows more.
- **Off until enabled.** Sheets and provider integrations are disabled until configured and authorized.
- **No secrets inside.** Credentials live in a credential store or the environment, never in the configuration file.
- **Safe to print.** Diagnostics show which settings were effective without dumping the whole file.[^sec]

# What belongs in it

Workspace roots and exclusions, traversal depth and symlink policy, file-size and count limits, the index location,
enabled detectors, freshness threshold, enabled integrations with their scopes, and log verbosity and retention.[^scan]

# Related

- [Local-First Operation](/concepts/local-first.md)
- [Untrusted Content](/concepts/untrusted-content.md)

[^sec]: Logging, Configuration, Incident Response, and References
[^scan]: Workspace Discovery and Repository Inspection
