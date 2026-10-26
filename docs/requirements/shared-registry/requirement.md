# Requirement: Shared Registry and Cross-Device Visibility

- **Package:** `docs/requirements/shared-registry/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P2
- **Owns:** FR-016, FR-017, NFR-018, NFR-035
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-016-shared-registry-synchronization.feature](features/fr-016-shared-registry-synchronization.feature), [fr-017-cross-device-project-visibility.feature](features/fr-017-cross-device-project-visibility.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/architecture/synchronization.md` — export/import flow, ownership, conflicts, authentication (§13)
- `knowledge/architecture/data-model.md` — shared registry record and synchronization run
- `knowledge/concepts/field-ownership.md` — synchronization shares information; it does not transfer ownership
- `knowledge/concepts/project-identity.md` — matching local and shared records through aliases
- `knowledge/architecture/c4-system-views.md` — registry sync container and Google Sheets context

## Intent

A developer on a second machine, or an agent there, can learn which projects exist and what they are without cloning them, through a Google Sheets registry. Vyasa exports only an approved subset, preserves human-managed portfolio fields, and never lets a failed or partial sync damage the local index.

## Scope

- **Included:**
  - Export allowlist, import of portfolio fields, and conflict handling.
  - Registry schema validation and row matching.
  - Cross-device visibility of registry-only projects.
  - Authentication choice and API quota behaviour.
- **Excluded:**
  - Local paths, workspace roots, credentials, or raw evidence in the registry.
  - Remote provider discovery (remote-discovery).
  - Automatic sync from MCP queries.
- **Deferred:**
  - Scheduled or background sync.
  - Sharing review decisions between devices.
  - A Repositories tab for multi-repository projects.

## Requirements

### FR-016 — Shared Registry Synchronization (P2)

Vyasa MUST synchronize an approved subset of project metadata with Google Sheets.

### FR-017 — Cross-Device Project Visibility (P2)

Vyasa MUST allow a device to retrieve shared project metadata even when the corresponding repository is not cloned locally.

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- New and changed projects reach the registry through the allowlist only (`fr-016`).
- Human-managed fields are preserved; conflicts are visible, not overwritten (`fr-016` S3, S6).
- A registry-only project is discoverable and says its source is unavailable here (`fr-017`).

## Constraints

- Explicit field allowlist; a field is not exportable because it exists (SEC-008).
- Sync is an explicit operation with dry-run; queries never sync (NFR-037).
- Idempotent upserts keyed by project id; re-running converges (NFR-035).
- Conflicts are decided by ownership, not timestamp alone.

## Acceptance Expectations

- Phase 2 criteria 1 to 8 in `phase-acceptance-criteria.md`.
- A canary test fills every local-only field with a sentinel and proves none reaches the payload.
- Tests run against a fake Sheets gateway; live tests are gated by an environment variable.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| SP-006 / DM-010 | Versioned allowlist of summary fields plus three portfolio fields. | Q2 |
| NFD-010 / DFR-009 | Portfolio fields: Sheets wins. Scanner fields: newest observation, with a hand-edited cell reported as a conflict. | Q3 |
| DFR-010 / SP-007 | Service account against one shared sheet by default; OAuth for individuals; credentials in the OS keyring. | Q4 |
| DO-009 | Two timestamps: Last Verified At (any device) and Last Synced At. | Q9 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-registry-schema-check`: validate tabs and columns without writing.
- `be-registry-export-one`: export one project through the allowlist with dry-run.
- `be-registry-import-portfolio`: import portfolio fields; detect conflicts.
- `be-registry-visibility`: registry-only projects in search and context.
