# Implementation Tasks: be-language-detector

- **OpenSpec Change ID:** `be-language-detector`
- **Status:** Implemented and archived
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use `python` where `python3` is absent.

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_workflows.py`.
- [x] 1.3 Confirm branch `feature/be-language-detector`.

## 2. Implementation Slice: validated language data

**Traceability:** Requirement: Validated language data · Knowledge: `knowledge/decisions/language-evidence-statuses.md`

- [x] 2.1 Test first: valid version 2, version 1 without maps, keys disagree with `code_extensions`, empty or non-string label.
- [x] 2.2 Add `languages` and `manifests` to `FileTypes` (default empty), extend `load_file_types`, and move `src/vyasa/data/file_types.json` to version 2 with a label for every code extension and the manifests Cargo.toml, go.mod, pyproject.toml, setup.py, requirements.txt, package.json, tsconfig.json, pom.xml, build.gradle, build.gradle.kts, Gemfile, composer.json.
- [x] 2.3 Run tests (existing `compose` tests must still pass); refactor.

## 3. Implementation Slice: files detected by extension

**Traceability:** Requirements: Files detected by extension; Statuses stay separate · Knowledge: `knowledge/architecture/scanning-and-evidence/detector-inventory.md`

- [x] 3.1 Test first: counts, extension case, shared extension, unknown and extensionless ignored, content not read.
- [x] 3.2 Implement `LanguageReport` and `languages_of`, and `detect_languages` over the walk.
- [x] 3.3 Run tests; refactor.

## 4. Implementation Slice: declared by manifest and agreement with the code count

**Traceability:** Requirements: Declared by manifest presence; Histogram agrees with the code count

- [x] 4.1 Test first: manifest without sources, nested manifest, unrecognized manifest, found both ways, sum equals `compose` code count (complete and capped trees).
- [x] 4.2 Implement manifest matching on `casefold` names.
- [x] 4.3 Run tests; refactor.

## 5. Implementation Slice: partial results and evidence

**Traceability:** Requirements: Partial walk reports absence as unknown; Evidence · Knowledge: `knowledge/decisions/partial-results-never-imply-absence.md`

- [x] 5.1 Test first: entry cap makes `is_absent` unknown, complete makes it true, evidence fields, shuffled directory order.
- [x] 5.2 Implement `is_absent` and evidence.
- [x] 5.3 Run tests; refactor.

## 6. Final Verification

- [x] 6.1 `python -m pytest`
- [x] 6.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`; all checks pass
- [x] 6.3 `openspec validate be-language-detector`
- [x] 6.4 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [x] 6.5 Review the diff for scope and the contract (no file opened, no path returned).

## 7. Documentation and Handover

- [x] 7.1 Behavior did not diverge from the decision or inventory §9.3; no knowledge change needed.
- [ ] 7.2 Mark the decision concept stable when the owner accepts it (left open: owner decision).

## 8. Review, Merge, and Archive

- [x] 8.1 Pull request with the change ID: not opened; merged locally to `develop` under owner instruction.
- [x] 8.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [x] 8.3 Archive the change.

## Verification Record

`python -m pytest`: 505 passed, 2 skipped (baseline 483 passed, 2 skipped; 22 new tests in tests/test_languages.py, one or more per spec scenario). Skips are the existing link tests.

## Completion Summary

Implemented and merged into `develop`; archived. The decision concepts stay `draft` until the owner accepts them.
