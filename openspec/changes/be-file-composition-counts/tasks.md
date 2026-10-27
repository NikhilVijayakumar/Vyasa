# Implementation Tasks: be-file-composition-counts

- **OpenSpec Change ID:** `be-file-composition-counts`
- **Status:** Not Started
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline (`python` where `python3` is absent): `python3 scripts/verify_workflows.py` (known failure: skill-reference check) and `python3 scripts/verify_knowledge.py`.
- [ ] 1.3 Confirm branch `feature/be-file-composition-counts`.

## 2. Prerequisite: project scaffolding

**Prerequisite, not a slice:** it delivers no behavior.

- [ ] 2.1 Add `pyproject.toml` (Python 3.12+, `pytest` as a dev dependency, `src` layout) and `src/vyasa/__init__.py`; add `tests/`.
- [ ] 2.2 Confirm `python -m pytest` runs and collects zero tests without error.

## 3. Implementation Slice: validated file-type data

**Traceability:** Requirement: Validated versioned file-type data · Knowledge: `knowledge/decisions/file-composition-data-and-limits.md`

- [ ] 3.1 Test first: valid, overlapping, missing version, and no-leading-dot cases.
- [ ] 3.2 Implement `FileTypes`, `FileTypeDataError`, `load_file_types`, and `src/vyasa/data/file_types.json` (version 1: code and documentation extensions per Q9 of the grill log).
- [ ] 3.3 Run tests; refactor.

## 4. Implementation Slice: counts and indicator on a flat tree

**Traceability:** Requirements: Counts classify by extension and agree; Documentation-only indicator; Evidence · Knowledge: `knowledge/architecture/scanning-and-evidence/detector-inventory.md`

- [ ] 4.1 Test first: mixed, case, unknown type, no extension, content not read, empty, documentation-only, evidence fields.
- [ ] 4.2 Implement `classify`, `WalkLimits`, `FileComposition`, and `compose` over a plain single-level walk.
- [ ] 4.3 Run tests; refactor.

## 5. Implementation Slice: bounded walk

**Traceability:** Requirement: Bounded walk with a partial marker · Knowledge: `knowledge/decisions/scan-limits-and-symlink-defaults.md`, `knowledge/decisions/partial-results-never-imply-absence.md`

- [ ] 5.1 Test first: entry cap, depth, time (injected clock), unreadable directory, within limits, indicator unknown when partial.
- [ ] 5.2 Implement `walk_checkout` with depth, entries, time, and `onerror`.
- [ ] 5.3 Run tests; refactor.

## 6. Implementation Slice: symlinks, exclusions, determinism

**Traceability:** Requirements: Symlinks and exclusions; Evidence (deterministic order)

- [ ] 6.1 Test first: symlink escape, junction escape (Windows), excluded directory, exclusion name case, checkout named like an exclusion, shuffled order, repeatable partial result (skip a link test with a stated reason where the platform cannot create one).
- [ ] 6.2 Implement pruning (`islink` and `isjunction`), case-insensitive exclusion, sorted traversal, and `DEFAULT_EXCLUSIONS`.
- [ ] 6.3 Run tests; refactor.

## 7. Final Verification

- [ ] 7.1 `python -m pytest`
- [ ] 7.2 `python3 scripts/verify_workflows.py` and `python3 scripts/verify_knowledge.py`
- [ ] 7.3 `openspec validate be-file-composition-counts`
- [ ] 7.4 Check each spec scenario has a test; record commands, outcomes, failures, skips.
- [ ] 7.5 Review the diff for scope and the contract (no file opened, no path returned).

## 8. Documentation and Handover

- [ ] 8.1 Add test instructions to `README.md`.
- [ ] 8.2 Update the knowledge decision if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 8.3 Mark the decision concept accepted when the owner accepts it.

## 9. Review, Merge, and Archive

- [ ] 9.1 Pull request with the change ID.
- [ ] 9.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 9.3 Archive the change.
