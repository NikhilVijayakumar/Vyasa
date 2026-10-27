# Requirement: Project Profile Lifecycle

- **Package:** `docs/requirements/project-profile/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1
- **Owns:** FR-014
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-014-project-profile-lifecycle.feature](features/fr-014-project-profile-lifecycle.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/architecture/scanning-and-evidence.md` — profile detection (§8), draft rules
- `knowledge/concepts/field-ownership.md` — declared values belong to the repository; drafts are generated state
- `knowledge/architecture/security-and-privacy.md` — draft generation as the only repository write
- `knowledge/concepts/evidence-and-provenance.md` — declared status

## Intent

Some facts a scanner cannot know: the purpose, the lifecycle, how projects relate. Maintainers declare them in a canonical profile that Vyasa reads and never rewrites. An optional, explicitly invoked draft helps a maintainer start one, and stays clearly separate until a person adopts it.

## Scope

- **Included:**
  - The canonical profile format, path, and schema version.
  - Per-field validation and unsupported versions.
  - Optional draft generation and its placement.
  - Precedence between declared and detected values.
- **Excluded:**
  - Automatic promotion of a draft.
  - A second human-readable authority such as VYASA.md.
  - Monorepo component profiles.
- **Deferred:**
  - Multiple components per repository.
  - Profile editing commands.

## Requirements

### FR-014 — Project Profile Lifecycle (P1)

Vyasa MUST distinguish machine-generated draft information from project-maintained canonical information.

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- No profile is an ordinary state, not an error (`fr-014` S1).
- A canonical profile is read and never overwritten (S4, S6).
- A draft is opt-in, separate, and never promoted by Vyasa (S2, S3).

## Constraints

- The standard scanner stays read-only (DOR-005, DOR-006).
- Draft generation is the only operation that writes into a repository, and it states the exact path first.
- Profile text is untrusted repository content (NFR-020).
- A malformed profile never blocks unrelated extraction.

## Acceptance Expectations

- Phase 1 criterion 9 in `phase-acceptance-criteria.md`.
- Before/after hash of a repository proves a scan changes nothing.
- Draft tests show the write is limited to the allowed path and refuses to overwrite.

## Open Decisions

Q2 was revised by the owner on 2026-10-27: the format is TOML, not YAML, and the profile is filled once by a coding agent in each repository, guided over MCP. The draft command (Q6) is deferred; the other rows remain recommendations.

| Decision | Recommended direction | Grill |
|---|---|---|
| DFR-004 / DO-001 | One TOML file at `.vyasa/project-profile.toml`, schema_version 1. | Q2 |
| DO-002 | No root-level VYASA.md in phase 1. | Q2 |
| DO-003 | Draft is opt-in, written to `.vyasa/project-profile.draft.toml`, excluded through `.git/info/exclude`. | Q6 |
| v1 fields | name, purpose, lifecycle, domain, tags, technologies, related_projects, documentation.entry_point, owners. | Q3 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-profile-read`: parse, validate, and report a canonical profile with per-field errors.
- `be-profile-precedence`: declared versus detected values in results.
- `be-profile-draft`: explicit draft command with exclusion and no overwrite.
