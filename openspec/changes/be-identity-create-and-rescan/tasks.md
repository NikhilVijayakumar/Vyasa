# Implementation Tasks: be-identity-create-and-rescan

- **OpenSpec Change ID:** `be-identity-create-and-rescan`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-identity-create-and-rescan`.

## 2. Prerequisite: migration

**Traceability:** Requirement: Existing indexes are migrated

- [x] 2.1 `0002_identity.sql` with backfill; identity constants in `vyasa.domain.index`.
- [x] 2.2 Tests: migration with data, two projects with one remote, backup made.

## 3. Slice: create identity

**Traceability:** Requirements: Identity is created once; Identity changes are recorded

- [x] 3.1 New projects get status, source, alias, and a `created` event.
- [x] 3.2 Tests: with remote, without, ambiguous or local remote, event contents.

## 4. Slice: rediscover by alias then path

**Traceability:** Requirement: Rediscovery finds the project by alias, then by path

- [x] 4.1 Matching, attached checkouts, derived project state.
- [x] 4.2 Tests: rescan adds no event, move keeps id, state from checkouts, provisional move.

## 5. Slice: later evidence and conflicts

**Traceability:** Requirements: Later evidence becomes an alias; Conflicting evidence is preserved

- [x] 5.1 Alias added on a known checkout; provisional to resolved; conflict event.
- [x] 5.2 Tests: remote added, renamed, removed, conflict.

## 6. Final Verification

- [x] 6.1 `python -m pytest`
- [x] 6.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [x] 6.3 `openspec validate be-identity-create-and-rescan`
- [x] 6.4 Each spec scenario has a test (321 pass, 2 skipped, both pre-existing).
- [x] 6.5 Cloned this repository into a scratch workspace with a token in its remote URL, stored it, renamed the folder, stored again: one project, two checkouts (old missing), one alias, token not in the database.
- [x] 6.6 Review the diff for scope and the contract (no path or URL in aliases or events, no deletes).

## 7. Documentation and Handover

- [x] 7.1 Extend the identity decision with conflict handling and the interim fallback; log entry.
- [ ] 7.2 Mark the decision concept accepted when the owner accepts it.

## 8. Review, Merge, and Archive

- [ ] 8.1 Pull request with the change ID.
- [ ] 8.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 8.3 Archive the change.
