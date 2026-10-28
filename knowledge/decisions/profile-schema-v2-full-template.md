---
type: Decision
title: "Profile Schema Version 2 Declares the Project in Depth as Nested Tables"
description: A second profile schema adds identity, purpose, scope, capabilities, declared technology, architecture, interfaces, references, and relationships as optional nested TOML tables, validated field by field, while version 1 keeps working.
tags: [adr, profile, schema]
status: stable
generated: { by: claude-code/sonnet-5.5, at: 2026-10-28T12:00:00Z }
---

# Status

Accepted. Implemented and verified.

# Context

The first profile schema holds a few short fields. Agents and other projects want a fuller, predefined description of a project: what it is for, what it does, how it is built, what it connects to, and where its documents are. The profile is repository content, shown to agents and other tools, so it must stay declared, bounded, and free of secrets. Data that other systems own — what the scanner observed, repository activity, delivery status, portfolio priority — must not be copied into it.

# Decision

Schema version 2 is a superset in intent, written as nested TOML tables under a single `project` table: identity, business purpose, scope, capabilities, declared technology, architecture, interfaces, dependencies, engineering references, documentation map, collaboration, relationships, and profile maintenance. Every field is optional and validated on its own; an invalid field is dropped and reported while the rest are kept, and an unknown field is reported. Text and lists have length and count limits, enumerated fields have fixed values, paths must be repository-relative, dates are calendar dates, and text with a URL that carries credentials is rejected; the contact reference may be neither an email address nor a URL. A declared project id and the relationship ids are stored as labels only and never influence the project identity Vyasa derives. Version 2 fields are stored under dotted names such as `project.summary`, version 1 fields keep their names, and one accessor reads a value from either version. Version 1 profiles keep being read unchanged, and a version Vyasa does not know is reported unsupported. The writer guide and the JSON Schema describe version 2 and are built from the same definitions as the validation.

# Alternatives considered

- **A YAML profile at the repository root.** Rejected: YAML has no standard-library parser, and a second authority for the same fields was already rejected.
- **Replace version 1.** Rejected: every existing profile would become unsupported.
- **Grow version 1 in place.** Rejected: the flat namespace cannot mirror the nested template and gives no clean version boundary.
- **Let a declared id drive identity.** Rejected: a mistyped or copied id could merge unrelated projects.
- **Copy observed technology, activity, delivery status, or priority into the profile.** Rejected: those belong to the scanner, version control, OpenSpec, and the portfolio system.

# Consequences

- A profile can describe a project in depth without becoming a second source of truth for what other systems own.
- The validation, the guide, and the JSON Schema share one definition and cannot drift.
- Two schema versions are read until version 1 is retired.
- Declared text is untrusted; it is returned as typed data and never as instructions.

# Related

- [Canonical Profile and Draft Handling](/decisions/canonical-profile-and-draft.md)
- [Stored Identity With Aliases](/decisions/stored-identity-with-aliases.md)
- [Field Ownership](/concepts/field-ownership.md)
