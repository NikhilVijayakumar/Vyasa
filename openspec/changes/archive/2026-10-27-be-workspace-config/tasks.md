# Implementation Tasks: be-workspace-config

- **OpenSpec Change ID:** `be-workspace-config`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

> Order of work, by owner instruction 2026-10-27: implement first, then write repository tests that anyone can re-run.

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-workspace-config`.

## 2. Implementation Slice: types and data directory

**Traceability:** Requirement: Locate the configuration file · Knowledge: `knowledge/decisions/configuration-file-format-and-location.md`

- [x] 2.1 Implement `vyasa.domain.workspace_config` and `data_directory`.
- [x] 2.2 Tests: three platform layouts, `VYASA_HOME` override, unset variables.

## 3. Implementation Slice: load and validate

**Traceability:** Requirements: Locate the configuration file; Load several workspace roots; Not configured; Invalid configuration is rejected as a whole

- [x] 3.1 Implement `load_workspace_config`.
- [x] 3.2 Tests: lookup order, explicit missing, multiple roots, duplicates, `~`, nesting warning, not configured (no file, empty roots), syntax error, unknown key, wrong type, relative root, all problems together.

## 4. Implementation Slice: root checks

**Traceability:** Requirement: Each root is checked on its own

- [x] 4.1 Implement `check_roots`.
- [x] 4.2 Tests: accessible, missing, not a directory, unreadable (patched `os.scandir`), independence of roots.

## 5. Final Verification

- [x] 5.1 `python -m pytest`
- [ ] 5.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py` — knowledge passes; workflows has 1 failure, the skill-reference check, which predates this change
- [x] 5.3 `openspec validate be-workspace-config`
- [x] 5.4 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [ ] 5.5 Review the diff for scope and the contract (nothing under a root is opened).

## 6. Documentation and Handover

- [x] 6.1 Add an example configuration to `README.md`.
- [ ] 6.2 Update the knowledge decision if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 6.3 Mark the decision concept accepted when the owner accepts it.

## 7. Review, Merge, and Archive

- [ ] 7.1 Pull request with the change ID.
- [ ] 7.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 7.3 Archive the change.
