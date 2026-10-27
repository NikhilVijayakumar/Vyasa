# Implementation Tasks: be-file-composition-query

- **OpenSpec Change ID:** `be-file-composition-query`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use `python` where `python3` is absent. Persistence tests use a real temporary SQLite file (`database-integration-testing`).

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, specs, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` (548 passed, 2 skipped on `develop`) and `python scripts/verify_workflows.py`.
- [x] 1.3 Confirm branch `feature/be-file-composition-query`.

## 2. Implementation Slice: one walk for counts and languages

**Traceability:** Requirement: One walk feeds counts and languages · Knowledge: `knowledge/decisions/checkout-walk-observation.md`

- [x] 2.1 Test first: languages sum to the code count on one scan (complete and capped); a stubbed walk is called once; existing `compose` and `detect_languages` tests stay unchanged and green.
- [x] 2.2 Implement `scan_checkout` and `CheckoutScan`; make `compose` and `detect_languages` delegate; move the documentation-only rule to one domain function.
- [x] 2.3 Switch `scan_workspace` to a `detect` callable returning a `CheckoutScan` and update the existing scan tests' stubs; run tests; refactor.

## 3. Implementation Slice: store the counts

**Traceability:** Requirements: Counts are stored on the observation; Failed and older observations have no counts

- [x] 3.1 Test first: version 6 index upgrades with data intact and null counts; counts stored for a complete scan; partial stores lower bounds; failed stores null; retention keeps two with their counts.
- [x] 3.2 Add `0007_composition_counts.sql` and write the counts in `_store_languages`.
- [x] 3.3 Run tests; refactor.

## 4. Implementation Slice: documentation_only filter

**Traceability:** Requirement: Search filters by documentation_only

- [x] 4.1 Test first: true, false, partial matches neither, not counted matches neither, any active checkout, missing checkout, combined with a language filter, non-boolean error.
- [x] 4.2 Implement the parameter, validation, and clauses in `search_projects`.
- [x] 4.3 Run tests; refactor.

## 5. Implementation Slice: composition in project details

**Traceability:** Requirements: Details list composition per checkout; Queries do not touch the filesystem

- [x] 5.1 Test first: per checkout without a total, totals agree, not counted for old and failed, partial bound, indicator follows the counts, missing checkout keeps counts, no filesystem access.
- [x] 5.2 Implement `projects.checkout_composition` and add `composition` to `get_project`.
- [x] 5.3 Run tests; refactor.

## 6. Implementation Slice: MCP declaration

**Traceability:** Requirement: Search filters by documentation_only

- [x] 6.1 Test first: a tool call with `documentation_only`, a structured error for a non-boolean, and the regenerated snapshot.
- [x] 6.2 Add the parameter and describe `composition` in the tool descriptions.
- [x] 6.3 Run tests; regenerate the snapshot and check its diff only adds the parameter and descriptions.

## 7. Final Verification

- [x] 7.1 `python -m pytest`
- [x] 7.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [x] 7.3 `openspec validate be-file-composition-query`
- [x] 7.4 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [x] 7.5 Review the diff for scope and the contract (no path returned, values bound, queries read-only).

## 8. Documentation and Handover

- [x] 8.1 Behavior matches the decision concept. One note: the MCP tool types `documentation_only` as a boolean, so the framework rejects a non-boolean such as "maybe" before the query layer; the query layer itself rejects non-booleans with `INVALID_INPUT` (tested). The framework also accepts "yes" as true.
- [ ] 8.2 Mark the decision concept stable when the owner accepts it.

## 9. Review, Merge, and Archive

- [ ] 9.1 Pull request with the change ID.
- [ ] 9.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 9.3 Archive the change.

## Verification Record

`python -m pytest`: 586 passed, 2 skipped (baseline 548 passed, 2 skipped; 38 new tests in tests/test_checkout_scan.py, tests/test_composition_query.py, tests/test_mcp_server.py, and adjusted stubs in tests/test_language_query.py). The skips are the existing link tests. The MCP tool snapshot was regenerated; its diff only adds the parameter and descriptions.

## Completion Summary

Not yet complete.
