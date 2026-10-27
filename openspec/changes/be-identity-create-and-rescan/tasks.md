# Implementation Tasks: be-identity-create-and-rescan

- **OpenSpec Change ID:** `be-identity-create-and-rescan`
- **Status:** Planned
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [ ] 1.3 Confirm branch `feature/be-identity-create-and-rescan`.

## 2. Prerequisite: migration

**Traceability:** Requirement: Existing indexes are migrated

- [ ] 2.1 `0002_identity.sql` with backfill; identity constants in `vyasa.domain.index`.
- [ ] 2.2 Tests: migration with data, two projects with one remote, backup made.

## 3. Slice: create identity

**Traceability:** Requirements: Identity is created once; Identity changes are recorded

- [ ] 3.1 New projects get status, source, alias, and a `created` event.
- [ ] 3.2 Tests: with remote, without, ambiguous or local remote, event contents.

## 4. Slice: rediscover by alias then path

**Traceability:** Requirement: Rediscovery finds the project by alias, then by path

- [ ] 4.1 Matching, attached checkouts, derived project state.
- [ ] 4.2 Tests: rescan adds no event, move keeps id, state from checkouts, provisional move.

## 5. Slice: later evidence and conflicts

**Traceability:** Requirements: Later evidence becomes an alias; Conflicting evidence is preserved

- [ ] 5.1 Alias added on a known checkout; provisional to resolved; conflict event.
- [ ] 5.2 Tests: remote added, renamed, removed, conflict.

## 6. Final Verification

- [ ] 6.1 `python -m pytest`
- [ ] 6.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [ ] 6.3 `openspec validate be-identity-create-and-rescan`
- [ ] 6.4 Each spec scenario has a test; skips reported.
- [ ] 6.5 Real workspace: store, simulate a rename in a scratch copy, confirm one project.
- [ ] 6.6 Review the diff for scope and the contract (no path or URL in aliases or events, no deletes).

## 7. Documentation and Handover

- [ ] 7.1 Extend the identity decision with conflict handling and the interim fallback; log entry.
- [ ] 7.2 Mark the decision concept accepted when the owner accepts it.

## 8. Review, Merge, and Archive

- [ ] 8.1 Pull request with the change ID.
- [ ] 8.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 8.3 Archive the change.
