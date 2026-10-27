# Requirement: Project Profile Lifecycle

- **Package:** `docs/requirements/project-profile/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1
- **Owns:** FR-014, FR-026, FR-027
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-014-project-profile-lifecycle.feature](features/fr-014-project-profile-lifecycle.feature), [fr-026-027-profile-v2-and-context.feature](features/fr-026-027-profile-v2-and-context.feature)

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

### FR-026 — Comprehensive Project Profile (P1)

Vyasa MUST read a profile of schema version 2 that declares, in nested tables, the project's identity, business purpose, scope, capabilities, declared technology, architecture, interfaces, dependencies, engineering references, documentation map, collaboration, relationships, and profile maintenance.

- Every field MUST be optional and validated on its own; a field that breaks a rule MUST be dropped and reported while the others are kept.
- Schema version 1 profiles MUST keep working unchanged.
- Declared ids (`project.id` and relationship ids) MUST be stored as labels and MUST NOT influence Vyasa's project identity.
- Text MUST NOT carry a URL with credentials; the contact reference MUST NOT be an email address or a URL; paths MUST be repository-relative.
- Declared values MUST stay separate from observed values; the profile MUST NOT hold observations, activity, delivery status, or portfolio priority.
- The writer guide and a JSON Schema MUST describe version 2 and every limit.

### FR-027 — Profile Context for Coding Agents (P1)

Vyasa MUST provide a coding agent with the deterministic facts it holds about a project, the profile as read, and the differences between them, in one read-only response.

- The context MUST be available as an MCP tool, from the stored observation, and as a CLI command, from a live read-only scan of one checkout held in a temporary in-memory index.
- Each context MUST state its source and the time of the observation, MUST include no absolute path, and MUST NOT include file text.
- The differences list MUST compare the declared profile with the observations only where the observation supports it, and MUST label each entry as a finding for review; it MUST NOT change the profile.
- Vyasa MUST NOT launch an agent and MUST NOT write the profile.

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
- Profile version 2 fields are short, structured, and declared; detail stays in the documents they point to.

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
| PP-001 | Profile version 2 is the full template as nested TOML; version 1 keeps working. | Q14, Q15, Q17 |
| PP-002 | Declared ids are labels only and never drive identity. | Q16 |
| PP-003 | Context bundle by MCP tool and CLI; CLI uses a live scan in an in-memory index; Vyasa never launches an agent. | Q18, Q19 |
| PP-004 | Differences list compares only where the observation supports it. | Q20, Q21 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-profile-read`: parse, validate, and report a canonical profile with per-field errors.
- `be-profile-precedence`: declared versus detected values in results.
- `be-profile-draft`: explicit draft command with exclusion and no overwrite.
- `be-profile-v2`: schema version 2 validation, normalized fields, guide, and JSON Schema.
- `be-profile-context`: context bundle, differences, MCP tool, and CLI command.
