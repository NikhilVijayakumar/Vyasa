---
type: Practice
title: Writing Knowledge
description: Section, lifecycle, and wording rules that keep a knowledge concept self-contained, checkable, and free of delivery vocabulary.
tags: [knowledge, okf, authoring, validation]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-27T09:00:00Z }
---

# Rule

A concept states what is true by design and can be read cold. The bundle
profile enforces the mechanical part of that; a reviewer checks the rest.

# Required sections

Each type may name sections that must appear exactly as top-level headings
and must not be empty. A Decision has Context, Decision, Alternatives
considered, and Consequences. Other types add sections only when a real
reader needs them; extra sections are always allowed.

# Reserved sections

- **Evidence** holds dated, sourced facts: a number, limit, or measurement
  states its source and date next to it.
- **Open questions** holds unresolved items. A concept with status `stable`
  has none: resolve each question or move it to its own concept first.

# Wording

A concept describes its subject, not the work of describing it, so it does not
refer to "this change" or a work item. The profile lists the banned patterns.

# Decisions are not edited

Once a decision is accepted its text stays as written. A change of mind is a
new decision; the replaced decision gets status `deprecated` and
`superseded_by`, naming its replacement. This is a review rule: the profile
checks that the replacement exists, not that the text is unchanged.

# Related

- [Evidence and Provenance](/concepts/evidence-and-provenance.md)
- [Open Knowledge Format (OKF)](/technologies/okf.md)
