# Requirement: <name>

- **Package:** `docs/requirements/<package>/`
- **Status:** Draft / Grilling / Grilled / Reviewed
- **Roadmap phase:** P1 / P2 / P3
- **Owns:** FR-nnn, NFR-nnn (every FR and NFR in the baseline belongs to exactly one package)
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [<name>.feature](features/<name>.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing. Missing concepts were created in `knowledge/` first.

- `knowledge/<folder>/<concept>.md` — why it applies

## Intent

The problem, who has it, and why it matters now.

## Scope

- **Included:**
  - …
- **Excluded:**
  - …
- **Deferred:**
  - …

## Requirements

Statements the package owns (`FR-nnn — title (phase)` followed by its MUST sentence and any lists).

## Expected Behaviour

One line per feature file, naming what is observable. Scenarios live in `features/`; those tagged `@proposed`
come from grill recommendations and become normative when confirmed.

## Constraints

Quality and security constraints (NFR and SEC ids) that shape the design.

## Acceptance Expectations

Observable outcomes and the check that proves each.

## Open Decisions

| Decision | Recommended direction | Grill |
|---|---|---|
| id | … | Qn |

## Delivery

Proposed OpenSpec changes (`be-<id>`), each a set of vertical slices.
