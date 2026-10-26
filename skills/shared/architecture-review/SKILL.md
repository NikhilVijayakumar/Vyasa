---
name: architecture-review
description: >-
  Reviews a proposed design or change for component boundaries, interfaces, data
  flow, failure handling, and quality attributes. Use when a change affects
  architecture, interfaces, cross-cutting concerns, or system boundaries.
metadata:
  scope: shared
---

# Architecture Review

Review the design in proportion to the change. A small, local change needs a
quick check; a change that crosses boundaries needs a deliberate review. Do not
run a full review for every change.

## What to check

- **Boundaries** — are responsibilities placed correctly? Is there a component
  that knows too much, or a boundary the change quietly erodes?
- **Interfaces and contracts** — are inputs, outputs, and failure modes
  explicit? Is the change backward-compatible, or is a migration required?
- **Data flow** — where does data originate, transform, and persist? Any
  ownership, duplication, or consistency problem?
- **Failure handling** — what happens on error, timeout, partial failure, or
  retry? Is failure surfaced, or silently swallowed?
- **Quality attributes** — the ones the change actually stresses: security,
  performance, scalability, reliability, maintainability.
- **Reuse** — does existing architecture or a documented decision already cover
  this? Prefer it over a new pattern.

## Proportionality

- Skip a dedicated review when the change is local and reversible; say so.
- Escalate to an ADR when the review surfaces a significant, durable decision.
- Use C4 or another diagram only when it materially clarifies a boundary; a
  diagram is not required.

## Output

Report findings as concise, actionable points: what was reviewed, what is at
risk, and what should change. Distinguish confirmed problems from open
questions. Do not rewrite the design unless asked.
