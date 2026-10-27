# Implementation Tasks: be-profile-v2

- **OpenSpec Change ID:** `be-profile-v2`
- **Status:** Not started
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use `python` where `python3` is absent. Profile text is untrusted: run `code-review-security` over the validator before the final verification.

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `python -m pytest` (798 passed, 2 skipped on `develop`) and `python scripts/verify_workflows.py`.
- [ ] 1.3 Confirm branch `feature/be-profile-v2`.

## 2. Implementation Slice: kinds and the table walker

**Traceability:** Requirements: Text, contacts, and paths are safe; Lists, tables, and text are bounded; Enumerations, dates, and commits have fixed forms · Knowledge: `knowledge/decisions/profile-schema-v2-full-template.md`

- [ ] 2.1 Test first: each kind (text, contact, path, label, date, tri, commit, enum, list, rows) with valid, boundary, and hostile values; rejection reasons never echo the value.
- [ ] 2.2 Implement the kind validators and the generic table walker in `vyasa/domain/profile_v2.py`.
- [ ] 2.3 Run tests; refactor.

## 3. Implementation Slice: version 2 fields and dispatch

**Traceability:** Requirements: A version 2 profile is read field by field; Version 1 profiles keep working; Unknown fields and versions are reported; Declared ids are labels only

- [ ] 3.1 Test first: a full valid profile, an empty profile, one invalid field among valid ones, unknown fields and tables, wrong table shapes, unsupported version 3, version 1 unchanged, the accessor for either version, and a scan test with two repositories declaring the same `project.id`.
- [ ] 3.2 Add the field definitions, `validate_v2`, version dispatch in `validate_profile`, and `declared`.
- [ ] 3.3 Run tests (existing version 1 tests unchanged); refactor.

## 4. Implementation Slice: guide and JSON Schema

**Traceability:** Requirement: The guide and the JSON Schema describe version 2

- [ ] 4.1 Test first: the guide lists every field with limits and allowed values and says version 1 is still read; its example validates; the committed `schemas/project-profile.v2.json` equals the generated schema; every storable name has a description.
- [ ] 4.2 Build the version 2 guide and schema from the definitions; add `supported_versions`; commit the schema file; update the guide tool description and regenerate the MCP snapshot.
- [ ] 4.3 Run tests; refactor.

## 5. Final Verification

- [ ] 5.1 `python -m pytest`
- [ ] 5.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [ ] 5.3 `openspec validate be-profile-v2`
- [ ] 5.4 Security review of the validator with `code-review-security`; record findings.
- [ ] 5.5 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [ ] 5.6 Review the diff for scope and the contract (no echo of rejected values, no identity use of declared ids).

## 6. Documentation and Handover

- [ ] 6.1 Update the decision concept if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 6.2 Mark the decision concept stable when the owner accepts it.

## 7. Review, Merge, and Archive

- [ ] 7.1 Pull request with the change ID.
- [ ] 7.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 7.3 Archive the change.

## Verification Record

Not yet run.

## Completion Summary

Not yet complete.
