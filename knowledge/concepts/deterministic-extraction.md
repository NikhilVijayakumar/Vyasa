---
type: Concept
title: "Deterministic Extraction"
description: Every extracted fact comes from a recognized source by a documented rule, so the same input always gives the same output.
tags: [determinism, detectors, principle]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: scan
    resource: /architecture/scanning-and-evidence/principles-and-pipeline.md
    title: Principles and Scanning Pipeline
  - id: det
    resource: /architecture/scanning-and-evidence/detectors-identity-profile.md
    title: Detectors, Identity, and Profile Detection
---

# Definition

Vyasa reports a fact only when a documented rule applied to a recognized source supports it. Given the same files,
configuration, and detector versions, extraction produces the same facts in the same order.[^scan]

# Rules

- **Recognized evidence only.** A technology is claimed from a manifest key, not from a mention in prose or an import
  statement.
- **No inference.** No language model, similarity score, or heuristic produces a stored fact. Models may read Vyasa's
  output; they never write it.
- **Versioned detectors.** A detector has an id and a version. Changing what it emits changes its version, which
  invalidates earlier results.
- **Pure detectors.** A detector is a function of the file inventory and a bounded reader. It has no hidden state, no
  clock, and no network.
- **Isolated failure.** A detector that fails reports an item error; other detectors and other projects continue.
- **Ordered output.** Paths are visited, and results emitted, in a stable sorted order.

# Why

A smaller index of verifiable facts is better than a larger one that guesses. Determinism is what makes extraction
testable with fixed inputs and makes incremental reuse safe.[^det]

# How it is checked

Fixture repositories produce normalized output compared to stored expectations. The same input is scanned twice, and
with directory entries shuffled, and the outputs must match.

# Related

- [Scanning and Evidence](/architecture/scanning-and-evidence.md)
- [Evidence and Provenance](/concepts/evidence-and-provenance.md)

[^scan]: Principles and Scanning Pipeline
[^det]: Detectors, Identity, and Profile Detection
