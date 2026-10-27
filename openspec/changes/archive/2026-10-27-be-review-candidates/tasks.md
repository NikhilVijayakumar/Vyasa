# Implementation Tasks: be-review-candidates

- **OpenSpec Change ID:** `be-review-candidates`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-review-candidates`.

## 2. Prerequisite: migration and catalogue

**Traceability:** Requirement: Decisions are never shared

- [x] 2.1 `0004_review_decisions.sql`; `RULES`, statuses, and error codes in `vyasa.domain.index`.
- [x] 2.2 Tests: migration from schema 3 gives an empty table and a backup.

## 3. Slice: explainable candidates

**Traceability:** Requirement: Candidates are explainable

- [x] 3.1 `list_candidates`.
- [x] 3.2 Tests: duplicate, unresolved, cleared flags absent.

## 4. Slice: local decisions

**Traceability:** Requirements: Decisions are stored locally; A decision holds only for the evidence it was made on

- [x] 4.1 `decide` with validation; evidence comparison.
- [x] 4.2 Tests: dismiss with note, change of mind, unknown candidate, invalid input, evidence changed, same condition returns.

## 5. Slice: nothing changes automatically

**Traceability:** Requirement: Nothing is changed automatically

- [x] 5.1 Write-set snapshot of every other table around `decide`.
- [x] 5.2 Tests: confirm leaves other tables identical; inaccessible and long-unseen projects have no candidate.

## 6. Final Verification

- [x] 6.1 `python -m pytest`
- [x] 6.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [x] 6.3 `openspec validate be-review-candidates`
- [x] 6.4 Each spec scenario has a test (349 pass, 2 skipped, both pre-existing).
- [x] 6.5 Two clones of one remote in a scratch workspace: one high-confidence candidate, dismissed with a note, still dismissed after a rescan.
- [x] 6.6 Review the diff for scope and the contract (decisions written only to their table).

## 7. Documentation and Handover

- [x] 7.1 Add a dated entry to `knowledge/log.md` if behavior diverged.
- [ ] 7.2 Mark the decision concept accepted when the owner accepts it.

## 8. Review, Merge, and Archive

- [ ] 8.1 Pull request with the change ID.
- [ ] 8.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 8.3 Archive the change.
