---
name: clarification-management
description: "Creates and maintains a prioritized clarification log for ambiguous, conflicting, or missing project decisions."
---

# Skill: Clarification Management
## Goal
Resolve ambiguity early and keep decisions visible to the team.

## Procedure
1. Collect all Open Questions and conflicts from source analysis, stories, design, data, and test planning.
2. For each question, state the affected feature, why the decision matters, and the impact if unresolved.
3. Offer neutral options only when useful; do not present a preferred option as approved.
4. Identify the accountable decision owner (Product Owner, architect, security, data owner) if known; otherwise mark owner unknown.
5. Record answer, date, decision owner, source, and affected requirement IDs.
6. Update the specification and linked tests only after the decision is confirmed.
7. Preserve superseded decisions with status/history rather than silently deleting them.

## Output
Prioritized clarification log: Critical / High / Medium / Low.

## Guardrails
Never treat silence, a prototype implementation, or an informal guess as approval. Do not block unrelated work if it can proceed safely with a clearly labelled assumption.
