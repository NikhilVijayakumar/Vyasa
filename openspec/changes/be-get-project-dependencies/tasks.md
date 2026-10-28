# Implementation Tasks: be-get-project-dependencies

- **OpenSpec Change ID:** `be-get-project-dependencies`
- **Status:** Planned
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use the project virtual environment (`venv/`) for every command. Persistence tests use a real temporary SQLite file (`database-integration-testing`). Run `code-review-security` over the parsers and the query, and `mcp-contract-review` over the tool declaration.

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, specs, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` (953 passed, 2 skipped on `develop`) and `python scripts/verify_workflows.py`.
- [x] 1.3 Confirm branch `feature/be-get-project-dependencies`.

## 2. Implementation Slice: declared names recorded and stored

**Traceability:** Requirements: Parsed manifests record the package name they declare · Knowledge: `knowledge/decisions/internal-dependencies-by-declared-package-name.md`

- [x] 2.1 Test first: name in each ecosystem (normalized), none declared, not text, too long, unparsed manifest, `requirements*.txt` has none, dependencies and counts unchanged; stored on the manifest row; a database at every earlier version upgrades to 10.
- [x] 2.2 Add `declared_name` to `ParsedManifest`, set it in the four parsers and bound it in `_bounded`, store it in `scan_workspace`, and add `0010_declared_names.sql` (column and index).
- [x] 2.3 Run tests; refactor.

## 3. Implementation Slice: dependencies with evidence

**Traceability:** Requirements: The tool lists direct dependencies with their evidence · Knowledge: `knowledge/decisions/framework-detection-from-manifests.md`

- [x] 3.1 Test first: scope and source, same name in two scopes, ordering, unknown id, invalid id, no local path, only active checkouts' latest observation.
- [x] 3.2 Implement `projects.project_dependencies` (own dependencies) and `query.get_project_dependencies` with the envelope and errors.
- [x] 3.3 Run tests; refactor.

## 4. Implementation Slice: internal, ambiguous, external

**Traceability:** Requirements: A dependency is internal only by exact name in one ecosystem

- [x] 4.1 Test first: internal, other ecosystem, ambiguous with every candidate, not indexed, not itself, normalization, missing checkout is not a target.
- [x] 4.2 Add the resolution join on `(ecosystem, declared_name)` excluding the project itself.
- [x] 4.3 Run tests; refactor.

## 5. Implementation Slice: dependents

**Traceability:** Requirements: The tool lists dependents

- [x] 5.1 Test first: a dependent, ambiguous dependent, none, ordering, truncation at 100 with total.
- [x] 5.2 Add the reverse join with a count and the 100 limit.
- [x] 5.3 Run tests; refactor.

## 6. Implementation Slice: coverage

**Traceability:** Requirements: Every answer states its coverage · Knowledge: `knowledge/decisions/partial-results-never-imply-absence.md`

- [x] 6.1 Test first: complete, unparsed manifest, partial walk, not assessed, nested manifests, names not recorded yet, other projects unchecked.
- [x] 6.2 Build the coverage object from manifest rows, observation status, nested counts, and the unchecked count.
- [x] 6.3 Run tests; refactor.

## 7. Implementation Slice: MCP declaration

**Traceability:** Requirements: The tool is read-only and bounded

- [x] 7.1 Test first: a tool call through the server, structured errors, the index unchanged, and the regenerated snapshot.
- [x] 7.2 Declare `get_project_dependencies` (read-only, one parameter) and describe the fields; regenerate the snapshot and check its diff only adds the tool.
- [x] 7.3 Run tests; refactor.

## 8. Final Verification

- [x] 8.1 `python -m pytest`
- [x] 8.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [x] 8.3 `openspec validate be-get-project-dependencies`
- [x] 8.4 Build with `scripts/build_mcp.py`, scan a fixture workspace of two linked projects, and call the tool through the executable.
- [x] 8.5 Review the diff for scope and the contract (read-only, no absolute path, no file text).
- [x] 8.6 Each spec scenario has a test; record commands, outcomes, failures, skips.

## 9. Documentation and Handover

- [x] 9.1 README MCP section and `docs/setup.md` list the tool and explain coverage; remove "get_project_dependencies not provided" from the limitations.
- [ ] 9.2 Mark the decision concept stable when the owner accepts it.

## 10. Review, Merge, and Archive

- [ ] 10.1 Pull request with the change ID.
- [ ] 10.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 10.3 Archive the change.

## Verification Record

- `python -m pytest`: 1000 passed, 2 skipped (baseline 953 passed, 2 skipped). New: tests/test_declared_names.py, tests/test_project_dependencies.py, additions to tests/test_mcp_server.py, and the migration-chain test now covers version 10. Skips are the existing POSIX-permission and symlink skips.
- `python scripts/verify_workflows.py` and `verify_knowledge.py`: all checks passed. `openspec validate be-get-project-dependencies`: valid (long-requirement warnings only).
- Executable: `scripts/build_mcp.py` built `vyasa-mcp.exe`; a scan of two linked fixture projects answered `get_project_dependencies` over stdio: `Ledger_Core` resolved internal to `ledger`, `ledger` listed `app` as dependent, coverage complete, no local path, unknown id returned `PROJECT_NOT_FOUND`.
- Contract refinements made while building (artifacts updated): `language_observations.names_recorded`, and coverage `partial` when any active checkout was not assessed.
- Not run: the full `code-review-security` procedure; reviewed by inspection that all SQL values are bound and the only interpolated text is a constant.

## Completion Summary

Implemented through task 9.1. Pending: owner acceptance of the decision concept (9.2), then merge and archive (10.1–10.3).
