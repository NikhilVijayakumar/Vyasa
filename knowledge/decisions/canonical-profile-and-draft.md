---
type: Decision
title: "Canonical Profile and Draft Handling"
description: One YAML profile at a fixed path is the declared source; an opt-in draft is separate and excluded locally.
tags: [adr, profile, drafts]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: prof
    resource: /architecture/scanning-and-evidence/detectors-identity-profile.md
    title: Detectors, Identity, and Profile Detection
  - id: own
    resource: /concepts/field-ownership.md
    title: Field Ownership
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

Some facts cannot be detected: purpose, lifecycle, relations. Maintainers need one place to declare them, and a way to start without writing into tracked files unprompted.

# Decision

The canonical profile is `.vyasa/project-profile.yaml` with a `schema_version`, validated per field; unsupported versions are reported and unrelated extraction continues. There is no second human-readable authority for the same fields. A draft is generated only by an explicit command to `.vyasa/project-profile.draft.yaml`, shown before writing, never overwritten without confirmation, and excluded through the repository's local exclude file rather than a tracked ignore file. Promotion is a person's edit and commit.

# Alternatives considered

- **A root-level Markdown profile.** Readable, but a second authority for the same fields.
- **Edit the tracked ignore file for the draft.** Modifies a tracked file unprompted.
- **Generate drafts during every scan.** Violates read-only scanning.

# Consequences

- Maintainers write YAML.
- Draft generation is the single, explicit write into a repository.
- The profile schema is a contract and is versioned.

# Related

- [Field Ownership](/concepts/field-ownership.md)
- [Read-Only Repository Access and Git Policy](/decisions/read-only-access-and-git-policy.md)
