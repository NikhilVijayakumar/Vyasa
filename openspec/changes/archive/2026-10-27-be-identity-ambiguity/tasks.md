# Implementation Tasks: be-identity-ambiguity

- **OpenSpec Change ID:** `be-identity-ambiguity`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-identity-ambiguity`.

## 2. Prerequisite: migration

**Traceability:** Requirement: Existing indexes are migrated

- [x] 2.1 `0003_review_flags.sql`; flag constants in `vyasa.domain.index`.
- [x] 2.2 Tests: schema 2 fixture keeps events, derives a duplicate flag, makes a backup.

## 3. Slice: duplicate checkouts

**Traceability:** Requirement: Duplicate checkouts are flagged

- [x] 3.1 `_raise`, `_clear`, `_sync_duplicate`, `list_flags`.
- [x] 3.2 Tests: two clones, moved, removed, same name different remotes.

## 4. Slice: ambiguous identity

**Traceability:** Requirements: Conflicting evidence makes identity ambiguous; Flags are idempotent and audited

- [x] 4.1 Conflict sets `ambiguous` and raises `identity_unresolved`; repair restores status and clears.
- [x] 4.2 Tests: conflict, visibility, repair, absence, repeat scan, reopen, listing, events hold no path or URL.

## 5. Final Verification

- [x] 5.1 `python -m pytest`
- [x] 5.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [x] 5.3 `openspec validate be-identity-ambiguity`
- [x] 5.4 Each spec scenario has a test (334 pass, 2 skipped, both pre-existing).
- [x] 5.5 Cloned this repository twice into a scratch workspace (https and ssh remote forms) and stored it twice: one project, two checkouts, one open duplicate flag, nothing new on the second store.
- [x] 5.6 Review the diff for scope and the contract (no path or URL in evidence, no automatic merge).

## 6. Documentation and Handover

- [x] 6.1 Extend the identity decision; add a dated entry to `knowledge/log.md`.
- [ ] 6.2 Mark the decision concept accepted when the owner accepts it.

## 7. Review, Merge, and Archive

- [ ] 7.1 Pull request with the change ID.
- [ ] 7.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 7.3 Archive the change.
