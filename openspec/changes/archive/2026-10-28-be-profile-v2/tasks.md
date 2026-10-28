# Implementation Tasks: be-profile-v2

- **OpenSpec Change ID:** `be-profile-v2`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use `python` where `python3` is absent. Profile text is untrusted: run `code-review-security` over the validator before the final verification.

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` (798 passed, 2 skipped on `develop`) and `python scripts/verify_workflows.py`.
- [x] 1.3 Confirm branch `feature/be-profile-v2`.

## 2. Implementation Slice: kinds and the table walker

**Traceability:** Requirements: Text, contacts, and paths are safe; Lists, tables, and text are bounded; Enumerations, dates, and commits have fixed forms · Knowledge: `knowledge/decisions/profile-schema-v2-full-template.md`

- [x] 2.1 Test first: each kind (text, contact, path, label, date, tri, commit, enum, list, rows) with valid, boundary, and hostile values; rejection reasons never echo the value.
- [x] 2.2 Implement the kind validators and the generic table walker in `vyasa/domain/profile_v2.py`.
- [x] 2.3 Run tests; refactor.

## 3. Implementation Slice: version 2 fields and dispatch

**Traceability:** Requirements: A version 2 profile is read field by field; Version 1 profiles keep working; Unknown fields and versions are reported; Declared ids are labels only

- [x] 3.1 Test first: a full valid profile, an empty profile, one invalid field among valid ones, unknown fields and tables, wrong table shapes, unsupported version 3, version 1 unchanged, the accessor for either version, and a scan test with two repositories declaring the same `project.id`.
- [x] 3.2 Add the field definitions, `validate_v2`, version dispatch in `validate_profile`, and `declared`.
- [x] 3.3 Run tests (existing version 1 tests unchanged); refactor.

## 4. Implementation Slice: guide and JSON Schema

**Traceability:** Requirement: The guide and the JSON Schema describe version 2

- [x] 4.1 Test first: the guide lists every field with limits and allowed values and says version 1 is still read; its example validates; the committed `schemas/project-profile.v2.json` equals the generated schema; every storable name has a description.
- [x] 4.2 Build the version 2 guide and schema from the definitions; add `supported_versions`; commit the schema file; update the guide tool description and regenerate the MCP snapshot.
- [x] 4.3 Run tests; refactor.

## 5. Final Verification

- [x] 5.1 `python -m pytest`
- [x] 5.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [x] 5.3 `openspec validate be-profile-v2`
- [x] 5.4 Security review of the validator with `code-review-security`: two findings, both fixed with tests — (1) low to medium: an unknown key in a profile was echoed into the problems that agents read, a prompt-injection surface; keys are now reduced to letters, digits, `_`, `.`, and `-` and cut to 40 characters; (2) low: `owner.team`, `owner.role`, and `maintained_by` accepted email addresses and URLs; they now follow the same no-email, no-URL rule as the contact reference. Not detected by design: a token in a URL query string, which the text rules cannot distinguish from ordinary text; the guide tells writers to keep credentials out.
- [x] 5.5 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [x] 5.6 Review the diff for scope and the contract (no echo of rejected values, no identity use of declared ids).

## 6. Documentation and Handover

- [x] 6.1 Behavior matches the decision concept; the people-field rule and the key sanitizing are covered by the validator and its tests.
- [x] 6.2 Mark the decision concept stable when the owner accepts it.

## 7. Review, Merge, and Archive

- [x] 7.1 Pull request with the change ID. Skipped: owner chose direct merge to develop (solo repository).
- [x] 7.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 7.3 Archive the change.

## Verification Record

`python -m pytest`: 891 passed, 2 skipped (baseline 798 passed, 2 skipped; 93 new tests in tests/test_profile_v2.py, adjusted tests in tests/test_profile_guide.py and tests/test_project_profile.py, which asserted that version 2 was unsupported). The skips are the existing link tests. The MCP tool snapshot was regenerated; its diff is the guide tool's description only. `openspec validate` is clean apart from the usual warnings.

## Completion Summary

Not yet complete.
