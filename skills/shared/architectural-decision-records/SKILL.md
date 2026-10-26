---
name: architectural-decision-records
description: >-
  Writes and reviews Architecture Decision Records (ADRs) capturing significant,
  durable architectural decisions with their context, alternatives, and
  consequences. Use when a change makes a lasting architectural decision, or to
  record explicitly that no new ADR is needed.
metadata:
  scope: shared
---

# Architecture Decision Records (ADRs)

Record decisions that are architecturally significant and durable — costly or
disruptive to reverse, or that constrain future work. Do not write an ADR for
every change.

## When an ADR is warranted

Write one when the change decides something that:

- establishes or changes a boundary, contract, or dependency between components;
- selects or replaces a technology, protocol, storage model, or integration;
- sets a cross-cutting policy (security, data ownership, error handling);
- is expensive to reverse or affects multiple teams.

A local, reversible, or purely tactical choice needs no ADR. In that case the
OpenSpec `adr` artifact explicitly records that no new decision is required, and
why.

## Structure

- **Title** — short and decision-shaped (e.g. "Use event-sourced ordering").
- **Status** — proposed / accepted / superseded / deprecated.
- **Context** — the forces at play: the problem, constraints, and what triggers
  the decision. State it before the decision.
- **Decision** — the choice, in the active voice ("We will …").
- **Alternatives** — options considered, and why each was rejected.
- **Consequences** — the resulting trade-offs, positive and negative, and the
  follow-up work the decision creates.
- **References** — related ADRs, specs, and external sources.

## Discipline

- One decision per record; keep them small and comparable.
- ADRs are append-only: to change a decision, add a new ADR that supersedes the
  old one and set the old one's status to `superseded`. Do not rewrite history.
- Reference an existing ADR instead of restating the same decision.
- Store ADRs where the consuming project keeps durable documentation — not in
  the temporary OpenSpec change directory, unless the project says otherwise.
