# Implementation Tasks: be-project-markers

- **OpenSpec Change ID:** `be-project-markers`
- **Status:** Implemented and archived
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use `python` where `python3` is absent. Persistence tests use a real temporary SQLite file (`database-integration-testing`).

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, specs, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` (586 passed, 2 skipped on `develop`) and `python scripts/verify_workflows.py`.
- [x] 1.3 Confirm branch `feature/be-project-markers`.

## 2. Implementation Slice: rules and detector

**Traceability:** Requirements: Markers come from names and directories; Location rules per marker; Tests are detected by directory and file name; OpenSpec indicators stay separate; Evidence is relative and capped; Marker rules are validated data · Knowledge: `knowledge/decisions/project-marker-observations.md`

- [x] 2.1 Test first: every marker by its rule, case handling, root-only versus any depth, nested agent scope, OpenSpec directory without config, test names and a non-test name, cap at 20 with the total, stable order, valid and malformed rules data.
- [x] 2.2 Add `src/vyasa/data/markers.json` (version 1), the domain module `markers` (`MarkerRules`, `MarkerHit`, `MarkerReport`, `markers_of`), and `load_marker_rules` with validation.
- [x] 2.3 Run tests; refactor.

## 3. Implementation Slice: the walk reports paths and directories

**Traceability:** Requirement: Walk reports relative paths and directories

- [x] 3.1 Test first: relative POSIX paths for nested files and directories in sorted order; excluded, ignored, and linked directories not reported; a directory at the depth limit reported but not entered; names, stop reason, and counts unchanged.
- [x] 3.2 Add `files` and `directories` to `WalkResult` and collect them in `walk_checkout`.
- [x] 3.3 Run tests; refactor.

## 4. Implementation Slice: store markers with the observation

**Traceability:** Requirements: Markers are stored on the observation; Older and failed observations are not assessed; Three states and unknown on partial walks; Detection failure is isolated

- [x] 4.1 Test first: version 7 index upgrades with data intact and null versions; markers stored with a version; partial stores found markers; failed stores none; retention keeps two with their rows; an injected failing detector is isolated and the run partial.
- [x] 4.2 Add `0008_project_markers.sql`, `rules` to `scan_checkout`, `markers` to `CheckoutScan` and `LanguageOutcome`, and `_store_markers` in `_store_languages`; load default rules in `scan_workspace`.
- [x] 4.3 Run tests; refactor.

## 5. Implementation Slice: marker filter in search

**Traceability:** Requirement: Search filters by marker

- [x] 5.1 Test first: detected, not detected after a complete assessment, partial matches neither state, not assessed matches neither, several names, any active checkout, missing checkout, combined with the language filter, unknown name and state errors listing allowed values.
- [x] 5.2 Implement `marker` and `marker_state` in `search_projects` with fixed sets and bound values.
- [x] 5.3 Run tests; refactor.

## 6. Implementation Slice: markers in project details

**Traceability:** Requirements: Details list markers per checkout; Marker queries do not touch the filesystem

- [x] 6.1 Test first: per checkout, not assessed for old and failed, partial states, evidence with scope and rules, missing checkout keeps markers, no absolute path, no filesystem access.
- [x] 6.2 Implement `projects.checkout_markers` and add `markers` to `get_project`.
- [x] 6.3 Run tests; refactor.

## 7. Implementation Slice: MCP declaration

**Traceability:** Requirement: Search filters by marker

- [x] 7.1 Test first: a tool call with `marker` and `marker_state`, a structured error for an unknown marker, and the regenerated snapshot.
- [x] 7.2 Add the parameters and describe `markers` in the tool descriptions.
- [x] 7.3 Run tests; regenerate the snapshot and check its diff only adds the parameters and descriptions.

## 8. Final Verification

- [x] 8.1 `python -m pytest`
- [x] 8.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [x] 8.3 `openspec validate be-project-markers`
- [x] 8.4 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [x] 8.5 Review the diff for scope and the contract (no file opened, no absolute path, values bound, queries read-only).

## 9. Documentation and Handover

- [x] 9.1 Behavior matches the decision concept; no knowledge change needed beyond the creation entry already in `knowledge/log.md`.
- [x] 9.2 Mark the decision concept stable when the owner accepts it.

## 10. Review, Merge, and Archive

- [x] 10.1 Pull request with the change ID: not opened; merged locally to `develop` under owner instruction.
- [x] 10.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [x] 10.3 Archive the change.

## Verification Record

`python -m pytest`: 668 passed, 2 skipped (baseline 586 passed, 2 skipped; 82 new tests in tests/test_markers.py, tests/test_walk_paths.py, tests/test_markers_query.py, and tests/test_mcp_server.py). The skips are the existing link tests. The MCP tool snapshot was regenerated; its diff only adds the two parameters and descriptions. `openspec validate` warns that the Search filters by marker requirement text is long; left as written.

## Completion Summary

Implemented, merged into `develop`, and archived. The decision concept is accepted.
