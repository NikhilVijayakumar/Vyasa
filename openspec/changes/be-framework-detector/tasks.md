# Implementation Tasks: be-framework-detector

- **OpenSpec Change ID:** `be-framework-detector`
- **Status:** Not started
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use `python` where `python3` is absent. Persistence tests use a real temporary SQLite file (`database-integration-testing`). This is the first detector that reads untrusted files: run `code-review-security` over the reader and parsers before the final verification.

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, specs, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `python -m pytest` (668 passed, 2 skipped on `develop`) and `python scripts/verify_workflows.py`.
- [ ] 1.3 Confirm branch `feature/be-framework-detector`.

## 2. Implementation Slice: registry and parsers

**Traceability:** Requirements: Dependencies are recorded with constraint and scope; Technologies come only from the registry; Registry is validated versioned data · Knowledge: `knowledge/decisions/framework-detection-from-manifests.md`, `knowledge/decisions/technology-registry-as-data.md`

- [ ] 2.1 Test first: each format's scopes, constraints, name normalization, skipped kinds, workspace flag, cap with total; known and unknown dependencies, united scopes, two manifests, ecosystems not mixed; valid and malformed registry data.
- [ ] 2.2 Add `src/vyasa/data/technologies.json` (version 1, about forty entries across the four ecosystems), the domain modules `frameworks` and `manifests`, `load_registry`, and `technologies_of`.
- [ ] 2.3 Run tests; refactor.

## 3. Implementation Slice: strict reader and hostile files

**Traceability:** Requirements: Manifests are read under strict rules; Each manifest has its own status

- [ ] 3.1 Test first: regular file, symlink (skip with a reason where unsupported), directory named like a manifest, oversized, grown after `lstat`, BOM, invalid UTF-8, binary, truncated TOML, deeply nested JSON, top-level array, one bad file among good ones, `setup.py` never opened.
- [ ] 3.2 Add `manifest_reader.read_manifest` and map parser exceptions to fixed reasons in `parse_manifest`.
- [ ] 3.3 Run tests; refactor.

## 4. Implementation Slice: detection and ecosystem inputs

**Traceability:** Requirements: Nested manifests are counted, not parsed; Ecosystem states keep absence honest (inputs)

- [ ] 4.1 Test first: root manifests found from the walk's file list, case-insensitive names, `requirements*.txt` pattern, nested manifests counted per ecosystem and not read, workspace flag only, deterministic order, a detector failure for one manifest not affecting others.
- [ ] 4.2 Implement `detect_frameworks` and add `frameworks` (registry) to `scan_checkout`, `CheckoutScan`, and `LanguageOutcome`; load the default registry in `scan_workspace`.
- [ ] 4.3 Run tests; refactor.

## 5. Implementation Slice: store frameworks with the observation

**Traceability:** Requirement: Frameworks are stored on the observation

- [ ] 5.1 Test first: version 8 index upgrades with data intact and null versions; manifests, dependencies, technologies, and nested counts stored; partial stores found rows; failed stores none; retention keeps two with their rows; an injected failing detector is isolated and the run partial.
- [ ] 5.2 Add `0009_frameworks.sql` and `_store_frameworks` in `_store_languages`.
- [ ] 5.3 Run tests; refactor.

## 6. Implementation Slice: technology filter in search

**Traceability:** Requirement: Search filters by technology

- [ ] 6.1 Test first: one key, several keys, case, dev declaration, any active checkout, missing checkout, malformed and not-assessed checkouts match nothing, combined with the language filter, unknown key error listing allowed keys.
- [ ] 6.2 Implement `technology` in `search_projects` with registry-validated keys and bound values.
- [ ] 6.3 Run tests; refactor.

## 7. Implementation Slice: frameworks in project details

**Traceability:** Requirements: Details list frameworks per checkout; Framework queries do not touch the filesystem

- [ ] 7.1 Test first: per checkout, ecosystem states for complete and partial, not assessed for old and failed, evidence fields, no text and no absolute path, missing checkout keeps frameworks, no filesystem access.
- [ ] 7.2 Implement `projects.checkout_frameworks` and add `frameworks` to `get_project`.
- [ ] 7.3 Run tests; refactor.

## 8. Implementation Slice: MCP declaration

**Traceability:** Requirement: Search filters by technology

- [ ] 8.1 Test first: a tool call with `technology`, a structured error for an unknown key, and the regenerated snapshot.
- [ ] 8.2 Add the parameter and describe `frameworks` in the tool descriptions.
- [ ] 8.3 Run tests; regenerate the snapshot and check its diff only adds the parameter and descriptions.

## 9. Final Verification

- [ ] 9.1 `python -m pytest`
- [ ] 9.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [ ] 9.3 `openspec validate be-framework-detector`
- [ ] 9.4 Security review of the reader and parsers with `code-review-security`; record findings.
- [ ] 9.5 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [ ] 9.6 Review the diff for scope and the contract (nothing executed, no text or absolute path stored, values bound, queries read-only).

## 10. Documentation and Handover

- [ ] 10.1 Update the decision concepts if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 10.2 Mark the decision concepts stable when the owner accepts them.

## 11. Review, Merge, and Archive

- [ ] 11.1 Pull request with the change ID.
- [ ] 11.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 11.3 Archive the change.

## Verification Record

Not yet run.

## Completion Summary

Not yet complete.
