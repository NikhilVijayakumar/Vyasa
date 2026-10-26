# Requirement: Data Ownership and Source of Truth

- **Package:** `docs/requirements/data-ownership/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1–P3
- **Owns:** DOR-001, DOR-002, DOR-003, DOR-004, DOR-005, DOR-006, DOR-007, DOR-008, DOR-009, DOR-010, DOR-011, DOR-012
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [dor-ownership-rules.feature](features/dor-ownership-rules.feature), [grill-additions.feature](features/grill-additions.feature), [ownership-examples.feature](features/ownership-examples.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/concepts/field-ownership.md` — owner categories and the rules every adapter follows
- `knowledge/concepts/evidence-and-provenance.md` — provenance and the conflicting status
- `knowledge/architecture/synchronization.md` — export, import, and conflict handling
- `knowledge/architecture/data-model.md` — observations and current-value resolution (§9)

## Intent

Vyasa sits between what a project declares, what a scanner observes, what a person manages centrally, and what Vyasa calculates. This package makes that boundary enforceable: one owner per field, provenance on every value, no silent overwrite, and local data that never leaves the machine. Synchronization shares information; it does not transfer ownership.

## Scope

- **Included:**
  - The ownership categories, the field matrix, and precedence rules.
  - Enforcement rules DOR-001 to DOR-012.
  - The worked examples A to E as acceptance scenarios.
  - Portfolio-owned fields and lifecycle ownership.
- **Excluded:**
  - Authorization in Google Sheets: who may edit cells is a Sheets sharing matter.
  - Conflict resolution commands beyond reporting.
- **Deferred:**
  - Interactive conflict resolution.
  - Per-field audit UI.

## Requirements

The normative detail stays in `docs/requirements/data-ownership.md`: the ownership categories, the field-level
matrix (§5), precedence rules (§6), classification boundaries (§7), and synchronization and remote rules (§8, §9).
This package turns them into scenarios and a decision record.

### Enforcement requirements

| ID | Rule |
|---|---|
| DOR-001 | Every persisted field that scanning, synchronization, or editing may change has an ownership category. |
| DOR-002 | Extracted and synchronized values keep enough provenance to tell their origins apart. |
| DOR-003 | No process overwrites a field owned by another source without an explicit authorization rule. |
| DOR-004 | Machine-specific information never enters shared exports. |
| DOR-005 | Generated drafts stay distinct from canonical profiles. |
| DOR-006 | Promotion from draft to canonical needs a human decision. |
| DOR-007 | Unresolved conflicts are visible. |
| DOR-008 | Derived fields are reproducible and not presented as authored facts. |
| DOR-009 | Failed scans and syncs never silently destroy valid information. |
| DOR-010 | Profiles and registry records are validated before their fields are accepted. |
| DOR-011 | Synchronization uses an explicit field allowlist. |
| DOR-012 | Automated tests verify each adapter respects ownership and conflict policy. |

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- Every adapter obeys the ownership registry (`dor-ownership-rules.feature`).
- The five worked examples hold in practice (`ownership-examples.feature`).

## Constraints

- Machine-local fields never enter a shared export (SEC-008, DOR-004).
- Failed operations never destroy valid data (DOR-009).
- Conflicts are visible and decided by ownership, not by timestamp alone.

## Acceptance Expectations

- Phase 2 criteria 3 and 4 in `phase-acceptance-criteria.md`.
- An adapter conformance test runs each adapter against the ownership registry.
- A canary test proves local-only values never reach any export.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| DO-006 | Portfolio fields: tracking level, domain, project type; priority and notes only after a schema change. | Q3 |
| DO-007 | Lifecycle is two fields: declared lifecycle (project) and portfolio status (portfolio). | Q4 |
| DO-005 | Name from profile, then manifest, then directory name marked provisional; purpose from profile or manifest description only. | Q5 |
| DOR-001 | A code-defined ownership registry, checked by a completeness test. | Q2 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-ownership-registry`: registry, completeness test, and the authorize-write check.
- `be-ownership-precedence`: precedence resolution and conflicting status.
- `be-ownership-canary`: export canary and adapter conformance tests.
