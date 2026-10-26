# Requirement: Project Identity and Review Candidates

- **Package:** `docs/requirements/project-identity/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1
- **Owns:** FR-003, FR-020, NFR-004
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-003-project-identity.feature](features/fr-003-project-identity.feature), [fr-020-duplicate-and-obsolete-candidates.feature](features/fr-020-duplicate-and-obsolete-candidates.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/concepts/project-identity.md` — evidence order, rules, and identity status
- `knowledge/architecture/data-model.md` — project, repository, checkout, and external identity entities
- `knowledge/architecture/scanning-and-evidence.md` — identity detection inputs and rules (§7)
- `knowledge/concepts/field-ownership.md` — review decisions are Vyasa-generated state, not repository content

## Intent

A project keeps one identity whatever its name, folder, or machine. Identity is what makes rescans idempotent, renames harmless, and cross-device sync possible, so it is the highest-risk decision in phase 1. The same package covers the review flags built on it: probable duplicates and probable obsolete projects, raised for a human and never acted on automatically.

## Scope

- **Included:**
  - Identity evidence order, remote normalization, and local fallback.
  - Alias and identity-change history.
  - Duplicate checkouts and ambiguous matches.
  - Duplicate and obsolete candidates with their criteria and evidence.
- **Excluded:**
  - Provider identifiers and fork relationships from APIs (remote-discovery).
  - Merging or deleting records (never automatic).
  - Registry row matching (shared-registry).
- **Deferred:**
  - Time-based obsolescence indicators, disabled by default.
  - Monorepo sub-project identities.

## Requirements

### FR-003 — Project Identity (P1)

Vyasa MUST maintain stable project identity independently of a project's display name and local filesystem path wherever reliable identity evidence exists.

### FR-020 — Duplicate and Obsolete Candidates (P1)

Vyasa MUST help users identify potentially duplicate or obsolete projects without automatically performing destructive actions.

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- Stable identity survives renames and moves, and rescans never duplicate (`fr-003`).
- Ambiguity is preserved and flagged, never resolved by guessing (`fr-003` S5).
- Candidates are flagged with deterministic criteria and left to a human (`fr-020`).

## Constraints

- Identity never derives from a display name or path alone (NFR-004).
- Credentials embedded in remote URLs are stripped before use or storage (SEC-005).
- Identity changes leave an audit trail and are recoverable.

## Acceptance Expectations

- Phase 1 criterion 8 (no duplicate projects when paths or ordering change).
- A parametrized table of URL forms normalizes to one identity.
- Rename, move, double-clone, no-remote, and rewritten-remote fixtures all behave as specified.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| DFR-005 / DM-002 | Normalize remotes to host/org/repo, lowercase for GitHub and Bitbucket; use origin, else the only remote. | Q2 |
| DO-004 / DM-001 | Create the ID once from the first strongest evidence; later evidence becomes aliases; the ID is never recomputed. | Q4 |
| DM-002 | No remote: root-commit hash through one sanitized read-only Git call; otherwise a provisional path-based identity flagged for review. | Q5 |
| FR-020 | Duplicate rules are deterministic; obsolescence needs a declared state; time-based rules are opt-in. | Q14 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-remote-normalization`: pure normalization function with the URL table.
- `be-identity-create-and-rescan`: create identity, rescan idempotently, survive rename.
- `be-identity-ambiguity`: duplicate checkouts, ambiguity flag, identity events.
- `be-review-candidates`: duplicate and obsolete candidates with evidence.
