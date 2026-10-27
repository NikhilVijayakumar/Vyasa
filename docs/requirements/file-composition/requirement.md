# Requirement: File Composition

- **Package:** `docs/requirements/file-composition/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1
- **Owns:** FR-021
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-021-file-composition.feature](features/fr-021-file-composition.feature), [grill-additions.feature](features/grill-additions.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing. The missing detector concept was created in `knowledge/` first.

- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.13 File Composition Detector, §9.3 language detector, §9.6 documentation detector
- `knowledge/architecture/scanning-and-evidence/discovery-and-inspection.md` — inventory, limits, symlinks, partial outcomes
- `knowledge/decisions/scan-limits-and-symlink-defaults.md` — accepted traversal limits and symlink policy
- `knowledge/decisions/partial-results-never-imply-absence.md` — a limit means not assessed, never absent
- `knowledge/concepts/evidence-and-provenance.md` — evidence record and observation statuses
- `knowledge/concepts/field-ownership.md` — observed versus declared values

## Intent

A maintainer with dozens of projects needs to tell a documentation-only repository from a code-heavy one, and an agent needs to know how much code a project holds before opening it. Both can be answered from file names alone. A predecessor tool counted documentation and code files but treated unknown file types as code, so its "documentation only" flag was unreliable; this requirement keeps the cheap counts and makes them honest.

## Scope

- **Included:**
  - Per-checkout counts of code, documentation, and other files, and their total.
  - A derived `documentation_only` indicator.
  - A completeness marker, and evidence of how the count was made.
  - Counts in project details; filtering by `documentation_only` in project search.
- **Excluded:**
  - File size, line counts, and any reading of file content.
  - Quality or completeness of documentation (see the documentation detector).
  - Language of a file beyond what the language detector reports.
- **Deferred:**
  - Synchronizing counts to the shared registry (see Q8).
  - Per-directory breakdowns.

## Requirements

### FR-021 — File Composition (P1)

Vyasa MUST report, for each scanned checkout, how many files are code, documentation, and other, using documented deterministic rules over file names only.

- The three counts and the total MUST agree: `code + documentation + other = total`.
- A file type not recognized as code or documentation MUST be counted as other, never as code.
- A count that reached a traversal bound MUST be marked partial and MUST NOT support `documentation_only`, which is then unknown.
- Counts MUST describe one checkout; the same project in two workspace roots has two observations, never summed.
- Each count MUST carry evidence: the extension data version, the exclusion rules, and the completeness marker.

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- Counts agree, unknown types are other, and symlinks are not followed (`fr-021`).
- A bound makes the count partial and the derived indicator unknown (`fr-021`).
- Classification data is versioned; the count walk is shared with the language detector (`grill-additions`).

## Constraints

- Deterministic: same tree and data version give the same counts (NFR-001).
- File content is never read; paths are never returned, only counts (security §4.3).
- Bounded: depth and time limits from the accepted scan-limits decision; the entry cap is Q4.
- A detector failure is isolated; other detectors and projects continue.

## Acceptance Expectations

- Golden-file fixtures: a documentation-only tree, a mixed tree, a tree with unknown types, and a tree over the entry cap give the documented counts and markers, including under shuffled directory order.
- A symlink-escape fixture proves no file outside the checkout is counted.
- The counts and the language histogram come from one walk and agree on code files.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| FC-001 | Counting uses its own entry cap of 50,000 (depth and time unchanged), because the 5,000 inventory cap would make most real repositories partial. | Q4 |
| FC-002 | Counts stay machine-local in phase 1 and are not in the sync export allowlist. | Q8 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-file-composition-counts`: shared bounded walk, classification data, counts, completeness marker, evidence.
- `be-file-composition-query`: counts in project details and the `documentation_only` search filter.
