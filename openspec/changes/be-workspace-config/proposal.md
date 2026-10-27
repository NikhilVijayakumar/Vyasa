# Change Proposal: be-workspace-config

## Why

Vyasa must scan only the workspace roots a user has configured, and a user may have several, on different drives. Nothing yet reads a configuration. This change loads and validates the workspace roots, reports a not-configured state instead of guessing a location, and checks each root on its own.

## What Changes

- **workspace-configuration**: find one TOML configuration file, validate it as a whole, return the configured workspace roots or a not-configured state, and report the accessibility of each root separately.

## 1. Problem and Motivation

### Current Situation
The `workspace-discovery` package owns FR-001. The repository has the file composition core (`src/vyasa`) but no configuration and no discovery.

### Problem
Discovery cannot start without a trustworthy list of roots. A missing, malformed, or ambiguous configuration must never lead to scanning a location the user did not choose.

### Evidence
- FR-001 scenarios S1, S3, S4, S5 (`docs/requirements/workspace-discovery/features/fr-001-configuration-and-workspace-roots.feature`).
- The grill log settles the file as TOML found via `--config`, `$VYASA_CONFIG`, then `<data dir>/config.toml` (Q2), and the data directory as the platform data directory with a `VYASA_HOME` override (local-index Q3).

## 2. Desired Outcome

### Goals
- [ ] Several roots, on different drives, load from one file.
- [ ] A missing default file or an empty root list is "not configured", never an error and never a default scan location.
- [ ] An invalid file reports every problem and applies nothing.
- [ ] One bad root does not affect the others.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Every scenario in `specs/workspace-configuration/spec.md` has a passing test.
- [ ] The default location logic is tested for Windows, macOS, and Linux layouts on any operating system.

## 3. Scope

### In Scope
- Locating the file: explicit path, `VYASA_CONFIG`, then the data directory.
- The `workspace.roots` setting, its validation, normalization, and de-duplication.
- Per-root accessibility checks.

### Out of Scope
- Exclusions, depth, symlink policy, and limits (`be-discovery-boundaries`).
- Discovery itself (`be-discover-one-root`).
- A command-line `--config` flag and any writing of the file (the caller passes the explicit path).
- Index location, integrations, and credentials.

### Constraints
Standard library only (`tomllib`). Python 3.12+. No branching on the operating system outside the data-directory function, which takes the platform as an input.

## 4. Stakeholders and Impact

- **Primary stakeholders:** users with one or more workspaces; the discovery change that consumes the roots.
- **Affected components or capabilities:** new `vyasa.domain.workspace_config` and `vyasa.application.configuration`.
- **Dependencies:** none beyond the standard library.
- **Compatibility considerations:** new; unknown keys are rejected so later keys are added deliberately.

## 5. Proposed Direction

A pure domain model for the result types, and one application module that locates, parses, validates, and checks. The durable choices are in `knowledge/decisions/configuration-file-format-and-location.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Locate the file | Explicit, then environment, then data directory | Must |
| REQ-002 | Load several roots | Normalized, de-duplicated, ordered | Must |
| REQ-003 | Not configured | No file or no roots reports why; nothing scanned | Must |
| REQ-004 | Invalid configuration | All problems reported; nothing applied | Must |
| REQ-005 | Root accessibility | Each root checked on its own | Must |
| REQ-006 | Nested roots | Kept and reported | Should |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Platform data directories differ | A config is not found on one system | The function takes the platform and environment as inputs; all three layouts are tested |
| Paths with backslashes in TOML | Windows users mis-escape them | Documented: use forward slashes or single-quoted literal strings; both load |
| Case-insensitive file systems | Duplicate roots by case | Compare with the standard library's `normcase` |

### Assumptions
- `VYASA_HOME` and `VYASA_CONFIG` are the only environment variables read.

### Open Questions
- [ ] Whether nested roots should instead be rejected; kept and reported for now (grill Q4).

## 8. Acceptance Summary

- [ ] All spec scenarios pass as automated tests.
- [ ] `python3 scripts/verify_workflows.py` shows no new failure.

## 9. Traceability

- **OpenSpec Change ID:** `be-workspace-config`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-workspace-config`
- **Requirement package:** `docs/requirements/workspace-discovery/requirement.md` (FR-001)
- **Knowledge references:** `knowledge/practices/configuration.md` — explicit, validated, fail-closed; `knowledge/decisions/configuration-file-format-and-location.md` — format, location, outcomes; `knowledge/architecture/scanning-and-evidence/discovery-and-inspection.md` — configured roots (§4.1)
- **Related issues or references:** None
- **Related existing specifications:** None
- **Related ADRs:** `knowledge/decisions/configuration-file-format-and-location.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved (`docs/reviews/config-and-discovery-grill.md`); two decisions await the owner.
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Draft
