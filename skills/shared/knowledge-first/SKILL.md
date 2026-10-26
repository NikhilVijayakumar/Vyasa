---
name: knowledge-first
description: >-
  Checks the OKF knowledge bundle (knowledge/) before any requirement,
  proposal, specification, design, or task is written; reuses relevant
  concepts, creates or updates missing ones as standalone knowledge first,
  then references them from the delivery artifact. Use at the start of every
  requirement package or OpenSpec change, and at closeout to capture what
  implementation taught.
---

# Knowledge First

Knowledge and delivery are separate tracks. `knowledge/` holds durable
engineering knowledge in OKF v0.2 (rules: `knowledge/profile.json`).
Requirements, OpenSpec changes, and code **link to** knowledge; knowledge
**never links to or depends on** them.

## Before writing a requirement, proposal, spec, design, or task

1. **List the topics** the work touches: domain concepts, components,
   interfaces, technologies, practices, past decisions.
2. **Search the bundle.** Read `knowledge/index.md`, then the section
   indexes; grep titles, descriptions, and `tags`.
3. **Classify each topic:**
   - *Exists and current* — reference it.
   - *Exists but wrong or incomplete* — update the concept first.
   - *Missing* — create it first.
4. **Create or update as standalone knowledge:**
   - Put it in the folder its `type` requires (`profile.json` → `types`).
   - Required frontmatter: `type`, `title`, `description`, `status`,
     `generated: { by, at }`. Agent-written content uses `status: draft` and
     `generated.by: <agent>/<version>`; a person confirming it adds
     `verified: { by: human:<id>, at }`.
   - State the general truth, not the requirement: write "MCP query tools are
     read-only", not "FR-12 requires…". No links or `sources` pointing at
     `docs/requirements/`, `openspec/`, or change-specific
     code; in-bundle paths and external URLs only.
   - List it in its folder's `index.md`; add a dated entry to
     `knowledge/log.md`.
   - Run `python3 scripts/verify_knowledge.py`; fix every FAIL.
5. **Reference it** from the artifact's `Knowledge References` section:
   `knowledge/<folder>/<concept>.md` plus one line on why it applies. Specs
   reference knowledge inline in requirement text, since delta spec files
   only allow requirement sections.

## At closeout (with `neat-freak`)

When implementation revealed a reusable lesson, a corrected assumption, or a
new decision, update or create the concept. The knowledge change stands on
its own: it must read correctly even after the change is archived.

## Guardrails

- Never copy requirement text into knowledge or knowledge text into a
  requirement; link instead.
- A concept that only makes sense next to one change is not knowledge; keep
  it in the change.
- Do not mark agent-written knowledge `verified` by a `human:` actor.
