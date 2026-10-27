# Implementation Tasks: be-language-query

- **OpenSpec Change ID:** `be-language-query`
- **Status:** Implemented and archived
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use `python` where `python3` is absent. Persistence tests use a real temporary SQLite file (`database-integration-testing`).

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, specs, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` (505 passed, 2 skipped on `develop`) and `python scripts/verify_workflows.py`.
- [x] 1.3 Confirm branch `feature/be-language-query`.

## 2. Implementation Slice: store an observation

**Traceability:** Requirements: Scan stores an observation per checkout; Current and previous observation are kept; Migration preserves the index · Knowledge: `knowledge/decisions/language-observations-in-index.md`, `knowledge/decisions/retention-defaults.md`

- [x] 2.1 Test first: version 5 index upgrades with data intact; storing a report writes the observation and rows; a third store leaves two observations; a failed outcome writes no rows.
- [x] 2.2 Add `0006_languages.sql`, `LanguageOutcome`, `Candidate.languages`, and `projects.store_languages` called from `upsert` after `_store_profile`; prune to two.
- [x] 2.3 Run tests; refactor.

## 3. Implementation Slice: scan detects and isolates failures

**Traceability:** Requirements: Scan stores an observation per checkout; Partial rescan is current and flagged; Detection failure is isolated; Inaccessible and missing checkouts keep their last observation

- [x] 3.1 Test first: scan stores languages for a real temporary repository; declared-only; partial rescan keeps the previous observation; an injected failing detector stores a failed observation, other checkouts are stored, and the run is partial; an unreached checkout is unchanged.
- [x] 3.2 Implement the `detect` parameter and per-candidate enrichment in `scan_workspace`, with failure isolation and the partial-run signal.
- [x] 3.3 Run tests; refactor.

## 4. Implementation Slice: language filter in search

**Traceability:** Requirements: Search filters by language; Search filters by language status; Unknown label or status is rejected; Any present checkout matches; Partial observations match positives only

- [x] 4.1 Test first: one label, several labels, case, combined with state, declared versus files_detected, typo and bad status errors listing allowed values, two checkouts, missing checkout, partial observation.
- [x] 4.2 Implement `language` and `language_status` in `search_projects` with fixed sets and bound values; add `languages` and `language_matches` to items.
- [x] 4.3 Run tests; refactor.

## 5. Implementation Slice: languages in project details

**Traceability:** Requirements: Details list languages per checkout; Languages stay separate from the profile; Queries do not touch the filesystem

- [x] 5.1 Test first: per checkout without a total, `not_observed`, missing checkout keeps its observation, profile unchanged, files changed after the scan do not change the answer.
- [x] 5.2 Implement the `languages` object in `get_project`.
- [x] 5.3 Run tests; refactor.

## 6. Implementation Slice: MCP declaration

**Traceability:** Requirements: Search filters by language; Search filters by language status

- [x] 6.1 Test first: update `tests/snapshots/mcp_tools.json` expectations (new parameters and description) and a server test calling the tool with `language`.
- [x] 6.2 Add the parameters and description to the `search_projects` tool; describe `languages` in `get_project`.
- [x] 6.3 Run tests; refactor.

## 7. Final Verification

- [x] 7.1 `python -m pytest`
- [x] 7.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`; all checks pass
- [x] 7.3 `openspec validate be-language-query`
- [x] 7.4 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [x] 7.5 Review the diff for scope and the contract (no path returned, values bound, queries read-only).

## 8. Documentation and Handover

- [x] 8.1 Behavior matches the decision concept; the observation also records the walk duration (Q19), added to the contract.
- [ ] 8.2 Mark the decision concepts stable when the owner accepts them (left open: owner decision).

## 9. Review, Merge, and Archive

- [x] 9.1 Pull request with the change ID.
- [x] 9.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [x] 9.3 Archive the change.

## Verification Record

`python -m pytest`: 548 passed, 2 skipped (baseline 505 passed, 2 skipped; 43 new tests in tests/test_language_query.py and tests/test_mcp_server.py). The skips are the existing link tests. The MCP tool snapshot was regenerated; its diff only adds the two parameters and descriptions.

## Completion Summary

Implemented and merged into `develop`; archived. The decision concepts stay `draft` until the owner accepts them.
