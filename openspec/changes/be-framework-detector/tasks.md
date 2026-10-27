# Implementation Tasks: be-framework-detector

- **OpenSpec Change ID:** `be-framework-detector`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use `python` where `python3` is absent. Persistence tests use a real temporary SQLite file (`database-integration-testing`). This is the first detector that reads untrusted files: run `code-review-security` over the reader and parsers before the final verification.

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, specs, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` (668 passed, 2 skipped on `develop`) and `python scripts/verify_workflows.py`.
- [x] 1.3 Confirm branch `feature/be-framework-detector`.

## 2. Implementation Slice: registry and parsers

**Traceability:** Requirements: Dependencies are recorded with constraint and scope; Technologies come only from the registry; Registry is validated versioned data · Knowledge: `knowledge/decisions/framework-detection-from-manifests.md`, `knowledge/decisions/technology-registry-as-data.md`

- [x] 2.1 Test first: each format's scopes, constraints, name normalization, skipped kinds, workspace flag, cap with total; known and unknown dependencies, united scopes, two manifests, ecosystems not mixed; valid and malformed registry data.
- [x] 2.2 Add `src/vyasa/data/technologies.json` (version 1, about forty entries across the four ecosystems), the domain modules `frameworks` and `manifests`, `load_registry`, and `technologies_of`.
- [x] 2.3 Run tests; refactor.

## 3. Implementation Slice: strict reader and hostile files

**Traceability:** Requirements: Manifests are read under strict rules; Each manifest has its own status

- [x] 3.1 Test first: regular file, symlink (skip with a reason where unsupported), directory named like a manifest, oversized, grown after `lstat`, BOM, invalid UTF-8, binary, truncated TOML, deeply nested JSON, top-level array, one bad file among good ones, `setup.py` never opened.
- [x] 3.2 Add `manifest_reader.read_manifest` and map parser exceptions to fixed reasons in `parse_manifest`.
- [x] 3.3 Run tests; refactor.

## 4. Implementation Slice: detection and ecosystem inputs

**Traceability:** Requirements: Nested manifests are counted, not parsed; Ecosystem states keep absence honest (inputs)

- [x] 4.1 Test first: root manifests found from the walk's file list, case-insensitive names, `requirements*.txt` pattern, nested manifests counted per ecosystem and not read, workspace flag only, deterministic order, a detector failure for one manifest not affecting others.
- [x] 4.2 Implement `detect_frameworks` and add `frameworks` (registry) to `scan_checkout`, `CheckoutScan`, and `LanguageOutcome`; load the default registry in `scan_workspace`.
- [x] 4.3 Run tests; refactor.

## 5. Implementation Slice: store frameworks with the observation

**Traceability:** Requirement: Frameworks are stored on the observation

- [x] 5.1 Test first: version 8 index upgrades with data intact and null versions; manifests, dependencies, technologies, and nested counts stored; partial stores found rows; failed stores none; retention keeps two with their rows; an injected failing detector is isolated and the run partial.
- [x] 5.2 Add `0009_frameworks.sql` and `_store_frameworks` in `_store_languages`.
- [x] 5.3 Run tests; refactor.

## 6. Implementation Slice: technology filter in search

**Traceability:** Requirement: Search filters by technology

- [x] 6.1 Test first: one key, several keys, case, dev declaration, any active checkout, missing checkout, malformed and not-assessed checkouts match nothing, combined with the language filter, unknown key error listing allowed keys.
- [x] 6.2 Implement `technology` in `search_projects` with registry-validated keys and bound values.
- [x] 6.3 Run tests; refactor.

## 7. Implementation Slice: frameworks in project details

**Traceability:** Requirements: Details list frameworks per checkout; Framework queries do not touch the filesystem

- [x] 7.1 Test first: per checkout, ecosystem states for complete and partial, not assessed for old and failed, evidence fields, no text and no absolute path, missing checkout keeps frameworks, no filesystem access.
- [x] 7.2 Implement `projects.checkout_frameworks` and add `frameworks` to `get_project`.
- [x] 7.3 Run tests; refactor.

## 8. Implementation Slice: MCP declaration

**Traceability:** Requirement: Search filters by technology

- [x] 8.1 Test first: a tool call with `technology`, a structured error for an unknown key, and the regenerated snapshot.
- [x] 8.2 Add the parameter and describe `frameworks` in the tool descriptions.
- [x] 8.3 Run tests; regenerate the snapshot and check its diff only adds the parameter and descriptions.

## 9. Final Verification

- [x] 9.1 `python -m pytest`
- [x] 9.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [x] 9.3 `openspec validate be-framework-detector`
- [x] 9.4 Security review of the reader and parsers with `code-review-security`: three findings, all fixed with tests — (1) medium: URL constraints could carry credentials into the index, now stored as `direct reference` in every ecosystem; (2) medium: unbounded dependency count, name length, and constraint length, now capped at 10,000 dependencies, 214-character names, and 200-character constraints, with the rest counted as skipped; (3) low: a file swapped for a link between `lstat` and `open` on platforms without `O_NOFOLLOW`, now refused by comparing the opened file with the checked one.
- [x] 9.5 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [x] 9.6 Review the diff for scope and the contract (nothing executed, no text or absolute path stored, values bound, queries read-only).

## 10. Documentation and Handover

- [x] 10.1 Behavior matches the decision concepts, with the security caps added to the reading rules in code and tests.
- [ ] 10.2 Mark the decision concepts stable when the owner accepts them.

## 11. Review, Merge, and Archive

- [ ] 11.1 Pull request with the change ID.
- [ ] 11.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 11.3 Archive the change.

## Verification Record

`python -m pytest`: 798 passed, 2 skipped (baseline 668 passed, 2 skipped; 130 new tests in tests/test_manifests.py, tests/test_manifest_reader.py, tests/test_framework_detection.py, tests/test_frameworks_query.py, and tests/test_mcp_server.py). The skips are the existing link tests; the real-symlink reader tests ran on this platform. The MCP tool snapshot was regenerated; its diff only adds the parameter and descriptions. `openspec validate` warns that one requirement text is long; left as written.

## Completion Summary

Not yet complete.
