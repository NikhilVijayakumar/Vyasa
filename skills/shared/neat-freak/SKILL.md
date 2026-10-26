---
name: neat-freak
description: >-
  Reconciles documentation, agent instructions, and durable project knowledge
  with what was actually implemented, before a change is archived. Use after
  implementation and verification, as the closeout step of a change.
metadata:
  scope: shared
---

# Neat Freak

Close the loop between what the project says and what it now does. Run this after
implementation and verification, before archiving the change.

## What to reconcile

- **Documentation** — update docs the change made stale; leave no contradiction
  between the docs and the implemented behavior.
- **Agent instructions** — update `AGENTS.md` and similar guidance when
  conventions, commands, or structure changed.
- **Durable project knowledge** — record reusable decisions and facts the change
  produced, following the project's conventions; reference existing entries
  instead of duplicating them.
- **Change artifacts** — confirm the specification, design, ADR, and tasks
  reflect what was actually built.

## Rules

- Reconcile against reality; do not invent undocumented behavior.
- Update in place; do not create parallel or duplicate documents.
- Keep durable knowledge separate from temporary change artifacts.
- A structured knowledge base (e.g. OKF) is optional — follow the project's
  system if one exists; never make one mandatory.
- Do nothing if the project is already consistent — say so.

## Output

A short list of what was updated and what was checked and left unchanged, so the
closeout is auditable.
