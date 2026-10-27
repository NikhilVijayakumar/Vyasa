# Implementation Tasks: be-repository-ignore

- **OpenSpec Change ID:** `be-repository-ignore`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

> Order of work, by owner instruction 2026-10-27: implement first, then write repository tests that anyone can re-run.

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-repository-ignore`.

## 2. Implementation Slice: parse and match

**Traceability:** Requirements: Patterns name directories; The file cannot widen the scan; The file is bounded · Knowledge: `knowledge/decisions/repository-ignore-file.md`

- [x] 2.1 Implement `vyasa.domain.ignore` and `read_ignore_file`.
- [x] 2.2 Tests: every pattern scenario, invalid lines, the digest, oversized and too-many-patterns files, unreadable file.

## 3. Implementation Slice: discovery honors the file

**Traceability:** Requirements: Discovery honors the file; Mistakes are reported; Only the ignore file is read

- [x] 3.1 Implement the rule stack in `find_repositories`, the `ignore_file` warning, and `ScanWarning.details`.
- [x] 3.2 Tests: ignored directory, sibling isolation, nested repositories, ignored deep directory, warning for a bad line, files opened.

## 4. Implementation Slice: file composition honors the file

**Traceability:** Requirement: File composition honors the file

- [x] 4.1 Implement rules in `walk_checkout`, loading in `compose`, and `Evidence.ignore`.
- [x] 4.2 Tests: ignored files not counted, evidence of use, no file.

## 5. Final Verification

- [x] 5.1 `python -m pytest`
- [ ] 5.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py` — knowledge passes; workflows has 1 failure, the skill-reference check, which predates this change
- [x] 5.3 `openspec validate be-repository-ignore`
- [x] 5.4 Each spec scenario has a test (192 tests pass in total; none skipped on Windows; not yet run on Linux).
- [x] 5.5 Ran discovery on the real workspace (read-only): 868 depth-skipped folders; the largest sources are Kriti/samgraha (307), srotas/knwoledge (103), AgentNoir/data (63). No repository of the owner's was modified, so no after figure exists yet.
- [ ] 5.6 Review the diff for scope and the contract.

## 6. Documentation and Handover

- [x] 6.1 Add a `.vyasaignore` section to `README.md`.
- [ ] 6.2 Update the knowledge decision if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 6.3 Mark the decision concept accepted when the owner accepts it.

## 7. Review, Merge, and Archive

- [ ] 7.1 Pull request with the change ID.
- [ ] 7.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 7.3 Archive the change.
