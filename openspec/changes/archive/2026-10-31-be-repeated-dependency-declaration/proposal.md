# Change Proposal: be-repeated-dependency-declaration

## Why

A scan aborts when a root manifest declares the same dependency twice in one scope, which real `pyproject.toml` files do whenever two optional-dependency groups list the same package. The index table `checkout_dependencies` is keyed by `(observation_id, path, name, scope)`, but the store inserts one row per declared entry, so the second entry raises `sqlite3.IntegrityError: UNIQUE constraint failed` and the whole scan fails. The index is left with an interrupted run and no project data for the roots that were not reached.

## What Changes

- **framework-detection**: the store keeps one dependency row per name and scope for a parsed manifest, keeping the first declaration's constraint; a repeat in the same scope no longer fails the scan. No schema change.

## 1. Problem and Motivation

### Current Situation
`projects._store_frameworks` inserts every dependency the parser returned. Migration 0009 keys `checkout_dependencies` by `(observation_id, path, name, scope)`, which cannot hold two rows for the same name and scope in one manifest.

### Problem
Two ordinary, supported shapes collide with that key:
- `[project.optional-dependencies]` with two groups that both list a package (e.g. `docs` and `notebooks` both naming `pandas`), both scoped `optional`;
- a `requirements*.txt` that names a package twice.

The parser keeps both entries, which is correct (scopes are not merged), but storage has no rule for the repeat, so the scan raises and stops.

### Evidence
Reproduced on this machine: `vyasa scan` over `E:/Python` and `D:/UnrealProjects` failed with the `UNIQUE constraint failed: checkout_dependencies.observation_id, checkout_dependencies.path, checkout_dependencies.name, checkout_dependencies.scope` traceback at `src/vyasa/adapters/sqlite/projects.py:235`, leaving the index at `freshness: partial` with an interrupted run; two manifests declare a repeat (`E:\Python\Nibandha\pyproject.toml` with eight packages across two optional groups, `E:\Python\Tantra\pyproject.toml` with `nltk`). A store-level unit test reproduces the same failure without the workspace.

## 2. Desired Outcome

### Goals
- [ ] A manifest that declares the same dependency twice in one scope is stored once and the scan completes.
- [ ] Distinct scopes for the same name are still kept apart.
- [ ] A repeat never aborts a scan, never loses another manifest's dependencies, and never changes what is reported for entries that were already stored.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] Storing a manifest whose dependencies repeat a `(name, scope)` pair writes one row and completes.
- [ ] The kept row carries the first declaration's constraint.
- [ ] `runtime` and `optional` declarations of the same package remain two rows.
- [ ] The full suite, the workflow checks, a rebuilt standalone executable, and a real scan of two workspace roots all pass.

## 3. Scope

### In Scope
- The dependency insert in `projects._store_frameworks` and its regression test.
- The clarification of FR-025 and of the framework-detection specification, contract, and decision concept about repeats.

### Out of Scope
- Schema or migration changes: the key already expresses the intent.
- Changing `total_dependencies`, which counts declared entries, not distinct names.
- Deduplicating across manifests or across scopes; scopes stay separate.
- Reading nested or workspace-member manifests.

### Constraints
Read-only over repository content; no new dependency; the fix must not weaken the constraint that protects the table.

## 4. Stakeholders and Impact

- **Primary stakeholders:** coding agents reading the index; the maintainer running scans.
- **Affected components or capabilities:** scan storage (SQLite index repository), framework detection.
- **Dependencies:** `be-framework-detector` (archived) supplies the table and parsers; `be-get-project-dependencies` (archived) reads the rows.
- **Compatibility considerations:** no schema change, so existing indexes and MCP clients are unaffected; an index left interrupted by the failure needs one successful scan, not a repair.

## 5. Proposed Direction

Collapse repeats at the insertion point, keyed by `(name, scope)`, keeping the first declaration's constraint. This honors the primary key the table already declares and leaves the parser, the caps, the scopes, and every read path unchanged. Alternatives (making the key include the constraint, `INSERT OR IGNORE`, deduplicating in the parser) are weighed in `design.md`.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | One row per name and scope | A repeated declaration is stored once, with the first constraint | Must |
| REQ-002 | Distinct scopes stay distinct | `runtime` and `optional` of the same name are two rows | Must |
| REQ-003 | A repeat never fails a scan | The row is skipped, other manifests unaffected | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Silently hiding a differing constraint | An agent sees one of two declared constraints | The kept constraint is the first declaration, which is deterministic; the row's constraint is still the manifest's own text |
| Hiding genuine constraint violations | A future bug stored silently | Only the duplicate `(name, scope)` case is collapsed before the insert; CHECK and foreign-key violations still raise |

### Assumptions
- A repeat in one scope carries no information the index models: the table has one constraint column per name and scope.

### Open Questions
- [ ] None blocking. Whether `total_dependencies` should count distinct names is deferred; it counts declared entries today and no consumer depends on the difference.

## 8. Acceptance Summary

- [ ] Each specification scenario has a passing test.
- [ ] The full suite and workflow checks pass.
- [ ] A rebuilt executable completes a scan of two workspace roots and `get_index_status` reports `current`.

## 9. Traceability

- **OpenSpec Change ID:** `be-repeated-dependency-declaration`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `fix/be-repeated-dependency-declaration`
- **Requirement package:** `docs/requirements/framework-detection/requirement.md` (FR-025)
- **Knowledge references:** `knowledge/decisions/framework-detection-from-manifests.md` — dependency scopes and the one-row-per-name-and-scope rule; `knowledge/decisions/index-lifecycle-and-single-writer.md` — the scan is the only writer and must complete or report failure
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/framework-detection/spec.md`
- **Related ADRs:** `knowledge/decisions/framework-detection-from-manifests.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved, or explicitly recorded.
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
