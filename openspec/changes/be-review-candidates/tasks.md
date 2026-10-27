# Implementation Tasks: be-review-candidates

- **OpenSpec Change ID:** `be-review-candidates`
- **Status:** Planned
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [ ] 1.3 Confirm branch `feature/be-review-candidates`.

## 2. Prerequisite: migration and catalogue

**Traceability:** Requirement: Decisions are never shared

- [ ] 2.1 `0004_review_decisions.sql`; `RULES`, statuses, and error codes in `vyasa.domain.index`.
- [ ] 2.2 Tests: migration from schema 3 gives an empty table and a backup.

## 3. Slice: explainable candidates

**Traceability:** Requirement: Candidates are explainable

- [ ] 3.1 `list_candidates`.
- [ ] 3.2 Tests: duplicate, unresolved, cleared flags absent.

## 4. Slice: local decisions

**Traceability:** Requirements: Decisions are stored locally; A decision holds only for the evidence it was made on

- [ ] 4.1 `decide` with validation; evidence comparison.
- [ ] 4.2 Tests: dismiss with note, change of mind, unknown candidate, invalid input, evidence changed, same condition returns.

## 5. Slice: nothing changes automatically

**Traceability:** Requirement: Nothing is changed automatically

- [ ] 5.1 Write-set snapshot of every other table around `decide`.
- [ ] 5.2 Tests: confirm leaves other tables identical; inaccessible and long-unseen projects have no candidate.

## 6. Final Verification

- [ ] 6.1 `python -m pytest`
- [ ] 6.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [ ] 6.3 `openspec validate be-review-candidates`
- [ ] 6.4 Each spec scenario has a test; skips reported.
- [ ] 6.5 Real workspace: double clone, dismiss, rescan, confirm it stays dismissed.
- [ ] 6.6 Review the diff for scope and the contract (decisions written only to their table).

## 7. Documentation and Handover

- [ ] 7.1 Add a dated entry to `knowledge/log.md` if behavior diverged.
- [ ] 7.2 Mark the decision concept accepted when the owner accepts it.

## 8. Review, Merge, and Archive

- [ ] 8.1 Pull request with the change ID.
- [ ] 8.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 8.3 Archive the change.
