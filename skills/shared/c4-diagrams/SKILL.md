---
name: c4-diagrams
description: >-
  Produces C4 context, container, component, and relevant interaction diagrams
  that clarify a design. Use when a diagram materially helps explain system
  boundaries, responsibilities, or data flow; skip it for local, obvious
  changes.
metadata:
  scope: shared
---

# C4 Diagrams

Use diagrams only when they materially clarify a boundary or flow that prose
handles poorly. A trivial or local change needs no diagram — say so and move on.

## Levels

- **Context** — the system, its users, and the external systems it talks to.
- **Container** — the deployable or runnable pieces and how they communicate.
- **Component** — the significant parts inside one container and their
  responsibilities.
- **Interaction/dynamic** — the sequence of calls or data flow for one specific
  scenario, when the ordering matters.

Choose the lowest level that answers the question. Do not draw every level by
default.

## Rules

- One diagram, one question. Title it with what it answers.
- Label every element and relationship; an unlabeled arrow is noise.
- Show only elements relevant to the decision; omit the rest.
- Keep notation tool-agnostic — a simple box-and-arrow or a text diagram
  (e.g. Mermaid/PlantUML) is fine.
- Place diagrams with the design they explain. Do not duplicate structure the
  design text already states plainly.
