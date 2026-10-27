# Implementation Tasks: be-language-detector

- **OpenSpec Change ID:** `be-language-detector`
- **Status:** Not started
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use `python` where `python3` is absent.

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_workflows.py`.
- [ ] 1.3 Confirm branch `feature/be-language-detector`.

## 2. Implementation Slice: validated language data

**Traceability:** Requirement: Validated language data · Knowledge: `knowledge/decisions/language-evidence-statuses.md`

- [ ] 2.1 Test first: valid version 2, version 1 without maps, keys disagree with `code_extensions`, empty or non-string label.
- [ ] 2.2 Add `languages` and `manifests` to `FileTypes` (default empty), extend `load_file_types`, and move `src/vyasa/data/file_types.json` to version 2 with a label for every code extension and the manifests Cargo.toml, go.mod, pyproject.toml, setup.py, requirements.txt, package.json, tsconfig.json, pom.xml, build.gradle, build.gradle.kts, Gemfile, composer.json.
- [ ] 2.3 Run tests (existing `compose` tests must still pass); refactor.

## 3. Implementation Slice: files detected by extension

**Traceability:** Requirements: Files detected by extension; Statuses stay separate · Knowledge: `knowledge/architecture/scanning-and-evidence/detector-inventory.md`

- [ ] 3.1 Test first: counts, extension case, shared extension, unknown and extensionless ignored, content not read.
- [ ] 3.2 Implement `LanguageReport` and `languages_of`, and `detect_languages` over the walk.
- [ ] 3.3 Run tests; refactor.

## 4. Implementation Slice: declared by manifest and agreement with the code count

**Traceability:** Requirements: Declared by manifest presence; Histogram agrees with the code count

- [ ] 4.1 Test first: manifest without sources, nested manifest, unrecognized manifest, found both ways, sum equals `compose` code count (complete and capped trees).
- [ ] 4.2 Implement manifest matching on `casefold` names.
- [ ] 4.3 Run tests; refactor.

## 5. Implementation Slice: partial results and evidence

**Traceability:** Requirements: Partial walk reports absence as unknown; Evidence · Knowledge: `knowledge/decisions/partial-results-never-imply-absence.md`

- [ ] 5.1 Test first: entry cap makes `is_absent` unknown, complete makes it true, evidence fields, shuffled directory order.
- [ ] 5.2 Implement `is_absent` and evidence.
- [ ] 5.3 Run tests; refactor.

## 6. Final Verification

- [ ] 6.1 `python -m pytest`
- [ ] 6.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [ ] 6.3 `openspec validate be-language-detector`
- [ ] 6.4 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [ ] 6.5 Review the diff for scope and the contract (no file opened, no path returned).

## 7. Documentation and Handover

- [ ] 7.1 Update the knowledge decision and inventory §9.3 if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 7.2 Mark the decision concept stable when the owner accepts it.

## 8. Review, Merge, and Archive

- [ ] 8.1 Pull request with the change ID.
- [ ] 8.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 8.3 Archive the change.

## Verification Record

Not yet run.

## Completion Summary

Not yet complete.
