# Implementation Tasks: be-project-query-basics

- **OpenSpec Change ID:** `be-project-query-basics`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-project-query-basics`.

## 2. Prerequisite: errors, envelope, validation

**Traceability:** Requirement: Queries are read-only and omit local paths

- [x] 2.1 Error codes and allowed values in `vyasa.domain.index`; `_validate`, `_envelope` in `vyasa.application.query`.
- [x] 2.2 Tests: envelope fields, invalid inputs.

## 3. Slice: search

**Traceability:** Requirements: Search is deterministic and bounded; Search matches text and filters

- [x] 3.1 `search_projects` with filters, escaped text match, keyset cursor.
- [x] 3.2 Tests: 45-project paging, limits, bad cursor, repeat, name and remote match, wildcards, combined and multi-value filters, unknown value, no match.

## 4. Slice: project details

**Traceability:** Requirement: Project details carry identity and review state

- [x] 4.1 `get_project`.
- [x] 4.2 Tests: resolved with two checkouts, local project, candidates, unknown id.

## 5. Slice: index status

**Traceability:** Requirement: Index status reports reliability

- [x] 5.1 `get_index_status`.
- [x] 5.2 Tests: empty index, after a run.

## 6. Final Verification

- [x] 6.1 `python -m pytest`
- [x] 6.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [x] 6.3 `openspec validate be-project-query-basics`
- [x] 6.4 Each spec scenario has a test (391 pass, 2 skipped, both pre-existing).
- [x] 6.5 Read-only write attempt; no path in any result by default.
- [x] 6.6 Stored a real discovery of ~/PycharmProjects into a scratch index and ran status and search against a read-only connection.
- [x] 6.7 Review the diff for scope and the contract.

## 7. Documentation and Handover

- [x] 7.1 Add a dated entry to `knowledge/log.md` if behavior diverged.
- [ ] 7.2 Mark decisions accepted when the owner accepts them.

## 8. Review, Merge, and Archive

- [ ] 8.1 Pull request with the change ID.
- [ ] 8.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 8.3 Archive the change.
