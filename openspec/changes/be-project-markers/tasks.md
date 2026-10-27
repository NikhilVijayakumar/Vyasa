# Implementation Tasks: be-project-markers

- **OpenSpec Change ID:** `be-project-markers`
- **Status:** Not started
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use `python` where `python3` is absent. Persistence tests use a real temporary SQLite file (`database-integration-testing`).

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, specs, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `python -m pytest` (586 passed, 2 skipped on `develop`) and `python scripts/verify_workflows.py`.
- [ ] 1.3 Confirm branch `feature/be-project-markers`.

## 2. Implementation Slice: rules and detector

**Traceability:** Requirements: Markers come from names and directories; Location rules per marker; Tests are detected by directory and file name; OpenSpec indicators stay separate; Evidence is relative and capped; Marker rules are validated data · Knowledge: `knowledge/decisions/project-marker-observations.md`

- [ ] 2.1 Test first: every marker by its rule, case handling, root-only versus any depth, nested agent scope, OpenSpec directory without config, test names and a non-test name, cap at 20 with the total, stable order, valid and malformed rules data.
- [ ] 2.2 Add `src/vyasa/data/markers.json` (version 1), the domain module `markers` (`MarkerRules`, `MarkerHit`, `MarkerReport`, `markers_of`), and `load_marker_rules` with validation.
- [ ] 2.3 Run tests; refactor.

## 3. Implementation Slice: the walk reports paths and directories

**Traceability:** Requirement: Walk reports relative paths and directories

- [ ] 3.1 Test first: relative POSIX paths for nested files and directories in sorted order; excluded, ignored, and linked directories not reported; a directory at the depth limit reported but not entered; names, stop reason, and counts unchanged.
- [ ] 3.2 Add `files` and `directories` to `WalkResult` and collect them in `walk_checkout`.
- [ ] 3.3 Run tests; refactor.

## 4. Implementation Slice: store markers with the observation

**Traceability:** Requirements: Markers are stored on the observation; Older and failed observations are not assessed; Three states and unknown on partial walks; Detection failure is isolated

- [ ] 4.1 Test first: version 7 index upgrades with data intact and null versions; markers stored with a version; partial stores found markers; failed stores none; retention keeps two with their rows; an injected failing detector is isolated and the run partial.
- [ ] 4.2 Add `0008_project_markers.sql`, `rules` to `scan_checkout`, `markers` to `CheckoutScan` and `LanguageOutcome`, and `_store_markers` in `_store_languages`; load default rules in `scan_workspace`.
- [ ] 4.3 Run tests; refactor.

## 5. Implementation Slice: marker filter in search

**Traceability:** Requirement: Search filters by marker

- [ ] 5.1 Test first: detected, not detected after a complete assessment, partial matches neither state, not assessed matches neither, several names, any active checkout, missing checkout, combined with the language filter, unknown name and state errors listing allowed values.
- [ ] 5.2 Implement `marker` and `marker_state` in `search_projects` with fixed sets and bound values.
- [ ] 5.3 Run tests; refactor.

## 6. Implementation Slice: markers in project details

**Traceability:** Requirements: Details list markers per checkout; Marker queries do not touch the filesystem

- [ ] 6.1 Test first: per checkout, not assessed for old and failed, partial states, evidence with scope and rules, missing checkout keeps markers, no absolute path, no filesystem access.
- [ ] 6.2 Implement `projects.checkout_markers` and add `markers` to `get_project`.
- [ ] 6.3 Run tests; refactor.

## 7. Implementation Slice: MCP declaration

**Traceability:** Requirement: Search filters by marker

- [ ] 7.1 Test first: a tool call with `marker` and `marker_state`, a structured error for an unknown marker, and the regenerated snapshot.
- [ ] 7.2 Add the parameters and describe `markers` in the tool descriptions.
- [ ] 7.3 Run tests; regenerate the snapshot and check its diff only adds the parameters and descriptions.

## 8. Final Verification

- [ ] 8.1 `python -m pytest`
- [ ] 8.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [ ] 8.3 `openspec validate be-project-markers`
- [ ] 8.4 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [ ] 8.5 Review the diff for scope and the contract (no file opened, no absolute path, values bound, queries read-only).

## 9. Documentation and Handover

- [ ] 9.1 Update the decision concept if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 9.2 Mark the decision concept stable when the owner accepts it.

## 10. Review, Merge, and Archive

- [ ] 10.1 Pull request with the change ID.
- [ ] 10.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 10.3 Archive the change.

## Verification Record

Not yet run.

## Completion Summary

Not yet complete.
