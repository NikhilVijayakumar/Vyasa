---
type: Concept
title: Project Identity
description: A project is identified by stable evidence, never by its name or path; ambiguity is preserved, not guessed away.
tags: [identity, project, repository, deduplication]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T00:00:00Z }
sources:
  - id: dm
    resource: /architecture/data-model.md
    title: Data Model
  - id: scan
    resource: /architecture/scanning-and-evidence.md
    title: Scanning and Evidence
---

# Definition

A **logical project** is separate from its **repositories** and from any
**local checkout**. Identity belongs to the project and its repositories; a
display name and a filesystem path are mutable attributes and never identify
anything.[^dm]

# Evidence order

Identity is taken from the strongest available evidence:

1. A verified provider repository identifier.
2. A normalized Git remote identity.
3. A deterministic local fallback when no reliable remote exists.

The same evidence always yields the same identifier. A directory rename or move
updates the path mapping and leaves the identifier unchanged.[^scan]

# Rules

- Never merge records because their names match.
- Never merge repositories into one project without explicit or sufficiently
  strong evidence; nesting in the filesystem is not such evidence.
- Forks and mirrors keep separate identities and may be associated by a
  distinct relationship.
- When evidence cannot decide, record the identity as ambiguous and flag it
  for review.
- A change to an identity mapping is explicit, recorded, and recoverable.
- Every identity decision stores the evidence behind it.

# Identity status

`resolved`, `provisional`, and `ambiguous` describe how settled an identity is;
a provisional or ambiguous identity is returned as such, never as resolved.

# Related

- [Data Model](/architecture/data-model.md)
- [Evidence and Provenance](/concepts/evidence-and-provenance.md)

[^dm]: Data Model
[^scan]: Scanning and Evidence
