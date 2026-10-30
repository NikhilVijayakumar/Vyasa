# Implementation Tasks: be-repeated-dependency-declaration

- **OpenSpec Change ID:** `be-repeated-dependency-declaration`
- **Status:** Complete
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

- Organize work into logical phases and implementation slices.
- Map tasks to relevant requirements, scenarios, design elements, or ADRs.
- Each implementation slice is a vertical slice (`knowledge/practices/vertical-slices.md`): one observable behaviour, its tests, and its evidence. Label pure enabling work as a prerequisite.
- Reference the `knowledge/` concepts a slice depends on next to its traceability line.
- Identify dependencies and preserve the order required for safe implementation.
- Use test-first development where applicable: establish a failing test, implement the behavior, and verify the result.
- Include relevant regression, integration, acceptance, security, accessibility, performance, or platform-specific checks based on the change and team conventions.
- Include documentation, migration, configuration, and operational work when required.
- Do not create tasks for behavior outside the approved scope without first updating the relevant artifacts.
- Do not mark a task complete without the required implementation and verification evidence.
- Apply the applicable team and technology extensions without duplicating their instructions here.

---

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, all capability specifications, design, and ADR checkpoint.
- [x] 1.2 Inspect relevant existing code, tests, interfaces, and project conventions — `projects._store_frameworks`, migration `0009_frameworks.sql`, `tests/test_frameworks_query.py`.
- [x] 1.3 Confirm the working branch follows the project Git policy and includes the OpenSpec change ID — `fix/be-repeated-dependency-declaration` from `develop`.
- [x] 1.4 Record relevant baseline checks and existing failures when needed to distinguish pre-existing issues from regressions — baseline: full suite green (1075 passed, 4 skipped) before the change; `vyasa scan` on two workspace roots failed with `UNIQUE constraint failed: checkout_dependencies...` before the change.

## 2. Implementation Slice: One dependency row per name and scope

**Traceability:** Requirement(s): REQ-001, REQ-002, REQ-003 (`specs/framework-detection/spec.md`) · Knowledge: `knowledge/decisions/framework-detection-from-manifests.md`

- [x] 2.1 Add or update tests for the expected behavior and confirm the relevant test fails for the intended reason — `test_a_dependency_declared_twice_in_one_scope_is_stored_once` failed with the same `sqlite3.IntegrityError` the real scan raised.
- [x] 2.2 Implement the minimum change required to satisfy the behavior — collapse the manifest's dependencies by `(name, scope)`, keeping the first, before the `executemany` insert.
- [x] 2.3 Run the relevant tests and refactor while keeping them passing — `tests/test_frameworks_query.py`: 37 passed.
- [x] 2.4 Verify applicable boundary, error, and regression scenarios — `test_frameworks_are_stored_with_the_observation` (4 rows, scopes kept apart) and `test_non_parsed_manifests_store_status_and_reason_only` (no rows for unparsed manifests) still pass; the CHECK on `scope` is untouched by the change.
- [x] 2.5 Update relevant documentation or contracts — FR-025 in `docs/requirements/framework-detection/requirement.md`, the framework-detection delta spec, the contract, and the existing decision concept.

## 3. Integration and Cross-Cutting Work

- [x] 3.1 Integrate the affected components and verify their interfaces and contracts — the store is the only writer of `checkout_dependencies`; the read path (`checkout_frameworks`, `dependencies.py`) is unchanged.
- [x] 3.2 Verify relevant cross-capability behavior and end-to-end workflows — a real `vyasa scan` of `E:/Python` and `D:/UnrealProjects` completed with 74 projects; `get_index_status` reported `current` through the MCP server, and `search_projects` returned indexed projects.
- [x] 3.3 Complete applicable security, privacy, performance, accessibility, compatibility, and reliability checks — nothing new is read or exposed; the pass is over at most 200 items per manifest; no schema or data-ownership change, so compatibility is unchanged.
- [x] 3.4 Complete required data migration, configuration, deployment, or rollback work — none: no migration, no configuration change. The standalone install at `E:\MCP\Vyasa MCP` was rebuilt so the executable carries the fix.
- [x] 3.5 Verify that existing functionality remains compatible where required — full suite passes; existing indexes remain valid at schema version 11.

## 4. Final Verification

- [x] 4.1 Run the required unit, integration, contract, component, and acceptance tests applicable to this change.
- [x] 4.2 Run required build, lint, type-check, static-analysis, and other project quality checks.
- [x] 4.3 Verify each in-scope specification requirement and scenario.
- [x] 4.4 Review the implementation for unintended scope changes, security concerns, and consistency with the design and applicable ADRs.
- [x] 4.5 Record verification commands, outcomes, failures, skips, and unverified checks.
- [x] 4.6 Resolve failures introduced by the change or explicitly document approved exceptions and outstanding risks.
- [x] 4.7 Verify the implementation against the API and data contract, including the trust boundary and the documented error model.

## 5. Documentation and Handover

- [x] 5.1 Update developer, user, API, architecture, or operational documentation as applicable — FR-025, the spec delta, and the decision concept; no user-facing guide changes because no tool or command surface changed.
- [x] 5.2 Record relevant decisions, deviations, limitations, and follow-up work — no new ADR; the `total_dependencies` question is recorded as deferred in `design.md` §8.
- [x] 5.3 Capture durable lessons in `knowledge/` with the `knowledge-first` skill — `knowledge/decisions/framework-detection-from-manifests.md` updated and `knowledge/log.md` records it.
- [x] 5.4 Prepare a change summary with links to requirements, tests, and verification evidence — see the Verification Record below.

## 6. Review, Merge, and Archive

- [x] 6.1 Review the diff and confirm all in-scope requirements are addressed.
- [x] 6.2 Ensure the required review and verification gates are satisfied.
- [x] 6.3 Prepare the pull request with the OpenSpec change ID and traceability references.
- [x] 6.4 Merge the normal feature or fix change into `develop` only after required review and verification.
- [x] 6.5 Confirm the change is integrated according to project policy before archiving its OpenSpec artifacts. Integrated on `develop` by merge `b1cfb0d` (`fix/be-repeated-dependency-declaration`); `openspec validate` passes.
- [x] 6.6 Archive the change and preserve the relevant traceability and durable knowledge. Archived as `openspec/changes/archive/2026-10-31-be-repeated-dependency-declaration`; `framework-detection` spec updated.

---

## Verification Record

| Check | Command or Evidence | Result | Notes |
|---|---|---|---|
| Unit tests (focused) | `venv\Scripts\python.exe -m pytest tests\test_frameworks_query.py -q` | Passed | 37 passed |
| Full suite | `venv\Scripts\python.exe -m pytest -q` | Passed | 1075 passed, 4 skipped |
| Workflow checks | `venv\Scripts\python.exe scripts\verify_workflows.py` | Passed | All checks passed, including this change's delta parse and the skill references. `python3` is not on this host; the project venv interpreter was used |
| Knowledge bundle | `venv\Scripts\python.exe scripts\verify_knowledge.py` | Passed | 150 concepts, 0 errors, 0 warnings |
| Requirements packages | `venv\Scripts\python.exe scripts\verify_requirements.py` | Passed | 17 packages, 49 feature files, 398 scenarios, 0 errors |
| Verification script tests | `venv\Scripts\python.exe -m unittest scripts\test_verify_knowledge.py scripts\test_verify_requirements.py` | Passed | 23 tests OK |
| Skill reference tests | `venv\Scripts\python.exe -m unittest scripts\test_sync_skills.py` | Passed | 6 tests OK |
| Schema smoke | `venv\Scripts\python.exe scripts\smoke_team_schemas.py` | Passed | Scratch change per schema is valid; none left behind |
| OpenSpec validation | `openspec validate be-repeated-dependency-declaration` | Passed | Change is valid. Archive warnings for the template's overview/capability/review sections, the same structure the other change artifacts use |
| Standalone build | `venv\Scripts\python.exe scripts\build_mcp.py` | Passed | Rebuilt `E:\MCP\Vyasa MCP` (both executables); data folder preserved |
| Real scan | `& "E:\MCP\Vyasa MCP\vyasa\vyasa.exe" scan` | Passed | `E:\Python` 63 repositories (31 added, 32 unchanged), `D:\UnrealProjects` 11 repositories, 74 projects indexed, exit code 0 |
| MCP contract | Stdio probe of `vyasa-mcp.exe`: `tools/list`, `get_index_status`, `search_projects` | Passed | 8 tools listed; `freshness: current`, 74 active projects |
| Specification coverage | Requirement-to-test mapping in §4.3 and `specs/framework-detection/spec.md` | Verified | REQ-001 covered by the new test; REQ-002 and REQ-003 by existing store tests |

## Completion Summary

- **Implementation status:** Complete
- **Requirements verified:** REQ-001, REQ-002, REQ-003
- **Outstanding failures or risks:** None. Every check in the record was executed; none is skipped or blocked.
- **Known deviations:** None in behavior. `python3`, the interpreter AGENTS.md names, is not on this host, so the project venv interpreter ran the same scripts.
- **Pull request:** None (direct fix branch merge per project policy)
- **Archive status:** Archived (2026-10-31)
