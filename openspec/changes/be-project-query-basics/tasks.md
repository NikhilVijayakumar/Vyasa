# Implementation Tasks: be-project-query-basics

- **OpenSpec Change ID:** `be-project-query-basics`
- **Status:** Planned
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [ ] 1.3 Confirm branch `feature/be-project-query-basics`.

## 2. Prerequisite: errors, envelope, validation

**Traceability:** Requirement: Queries are read-only and omit local paths

- [ ] 2.1 Error codes and allowed values in `vyasa.domain.index`; `_validate`, `_envelope` in `vyasa.application.query`.
- [ ] 2.2 Tests: envelope fields, invalid inputs.

## 3. Slice: search

**Traceability:** Requirements: Search is deterministic and bounded; Search matches text and filters

- [ ] 3.1 `search_projects` with filters, escaped text match, keyset cursor.
- [ ] 3.2 Tests: 45-project paging, limits, bad cursor, repeat, name and remote match, wildcards, combined and multi-value filters, unknown value, no match.

## 4. Slice: project details

**Traceability:** Requirement: Project details carry identity and review state

- [ ] 4.1 `get_project`.
- [ ] 4.2 Tests: resolved with two checkouts, local project, candidates, unknown id.

## 5. Slice: index status

**Traceability:** Requirement: Index status reports reliability

- [ ] 5.1 `get_index_status`.
- [ ] 5.2 Tests: empty index, after a run.

## 6. Final Verification

- [ ] 6.1 `python -m pytest`
- [ ] 6.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [ ] 6.3 `openspec validate be-project-query-basics`
- [ ] 6.4 Each spec scenario has a test; skips reported.
- [ ] 6.5 Read-only write attempt; no path in any result by default.
- [ ] 6.6 Run the queries against the real workspace index.
- [ ] 6.7 Review the diff for scope and the contract.

## 7. Documentation and Handover

- [ ] 7.1 Add a dated entry to `knowledge/log.md` if behavior diverged.
- [ ] 7.2 Mark decisions accepted when the owner accepts them.

## 8. Review, Merge, and Archive

- [ ] 8.1 Pull request with the change ID.
- [ ] 8.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 8.3 Archive the change.
