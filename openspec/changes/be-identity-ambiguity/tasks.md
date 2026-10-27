# Implementation Tasks: be-identity-ambiguity

- **OpenSpec Change ID:** `be-identity-ambiguity`
- **Status:** Planned
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [ ] 1.3 Confirm branch `feature/be-identity-ambiguity`.

## 2. Prerequisite: migration

**Traceability:** Requirement: Existing indexes are migrated

- [ ] 2.1 `0003_review_flags.sql`; flag constants in `vyasa.domain.index`.
- [ ] 2.2 Tests: schema 2 fixture keeps events, derives a duplicate flag, makes a backup.

## 3. Slice: duplicate checkouts

**Traceability:** Requirement: Duplicate checkouts are flagged

- [ ] 3.1 `_raise`, `_clear`, `_sync_duplicate`, `list_flags`.
- [ ] 3.2 Tests: two clones, moved, removed, same name different remotes.

## 4. Slice: ambiguous identity

**Traceability:** Requirements: Conflicting evidence makes identity ambiguous; Flags are idempotent and audited

- [ ] 4.1 Conflict sets `ambiguous` and raises `identity_unresolved`; repair restores status and clears.
- [ ] 4.2 Tests: conflict, visibility, repair, absence, repeat scan, reopen, listing, events hold no path or URL.

## 5. Final Verification

- [ ] 5.1 `python -m pytest`
- [ ] 5.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [ ] 5.3 `openspec validate be-identity-ambiguity`
- [ ] 5.4 Each spec scenario has a test; skips reported.
- [ ] 5.5 Real workspace: clone a repository twice in a scratch workspace and confirm one project, two checkouts, one flag.
- [ ] 5.6 Review the diff for scope and the contract (no path or URL in evidence, no automatic merge).

## 6. Documentation and Handover

- [ ] 6.1 Extend the identity decision; add a dated entry to `knowledge/log.md`.
- [ ] 6.2 Mark the decision concept accepted when the owner accepts it.

## 7. Review, Merge, and Archive

- [ ] 7.1 Pull request with the change ID.
- [ ] 7.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 7.3 Archive the change.
