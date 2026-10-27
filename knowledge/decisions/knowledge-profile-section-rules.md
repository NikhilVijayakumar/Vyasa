---
type: Decision
title: "Knowledge Profile Enforces Sections and Supersession"
description: The bundle profile requires named sections per type, bans open questions in stable concepts, and makes a deprecated decision name its replacement.
tags: [adr, knowledge, okf, validation]
status: stable
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T09:00:00Z }
---

# Status

Accepted. The rules are enforced by the bundle verifier.

# Context

OKF requires only a `type` per concept. The bundle profile already enforces
frontmatter, folders, indexes, links, and size. Nothing yet stops a decision
without alternatives, a stable concept with unresolved questions, or a
replaced decision with no pointer to its replacement.

# Decision

The profile gains three optional keys, each enforced as an error by the
bundle verifier: `required_sections` (per type, top-level headings that must
appear and be non-empty), `forbidden_words` (patterns a concept may not
contain), and a supersession rule (a deprecated Decision carries `superseded_by`,
which must resolve to another Decision). A concept with status `stable` may not contain an Open
questions section. A missing key disables its check, so a bundle with an
older profile still verifies.

# Alternatives considered

- **Per-type kind definitions with templates and layered link direction.**
  Rejected: eight types do not justify a kind catalogue, and phase and
  roadmap concepts legitimately mention future work.
- **Warnings only.** Rejected: the current bundle already satisfies every
  rule, so an error costs nothing today and keeps it that way.
- **Enforce decision immutability in the verifier.** Rejected: it needs
  version history; it stays a review rule.
- **Two-way `supersedes` and `superseded_by`.** Rejected: two fields to keep
  in step for one fact; the old decision's pointer is enough.

# Consequences

- New decisions must carry the four sections; older ones already do.
- Stable promotion requires clearing open questions.
- Tightening a rule later is an edit to `profile.json`, not to the verifier.

# Related

- [Writing Knowledge](/practices/writing-knowledge.md)
- [Open Knowledge Format (OKF)](/technologies/okf.md)
