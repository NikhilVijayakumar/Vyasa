---
type: Decision
title: "Deterministic Extraction Without a Language Model"
description: Stored facts are produced only by versioned deterministic detectors over recognized evidence.
tags: [adr, determinism, detectors]
status: draft
generated: { by: claude-code/sonnet-5.5, at: 2026-10-26T12:00:00Z }
sources:
  - id: det
    resource: /concepts/deterministic-extraction.md
    title: Deterministic Extraction
  - id: scan
    resource: /architecture/scanning-and-evidence/principles-and-pipeline.md
    title: Principles and Scanning Pipeline
---

# Status

Proposed (draft). It becomes stable when reviewed and accepted.

# Context

The index is only useful if its facts can be trusted and reproduced. Model-generated summaries vary between runs, cannot be tested against fixed expectations, and may send repository content to a third party.

# Decision

Extraction, search, matching, and ranking use documented rules over recognized sources. A language model may consume Vyasa's output but never produces a stored fact.

# Alternatives considered

- **Model-generated descriptions.** Richer text, but unverifiable, non-deterministic, and a privacy risk.
- **Heuristic guesses from prose.** Cheap, but wrong often enough to destroy trust.

# Consequences

- Some fields stay `unknown` where a person could have guessed.
- Detectors are tested with fixed inputs and compared output.
- Adding a new fact means adding a new rule and detector version.

# Related

- [Deterministic Extraction](/concepts/deterministic-extraction.md)
- [Evidence and Provenance](/concepts/evidence-and-provenance.md)
