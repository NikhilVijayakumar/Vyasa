# Implementation Tasks: be-profile-guide

- **OpenSpec Change ID:** `be-profile-guide`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `.venv/bin/python -m pytest` and `python3 scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-profile-guide`.

## 2. Slice: the guide and the schema

**Traceability:** Requirements: The guide is generated from the validation rules; A JSON Schema is committed

- [x] 2.1 `profile_guide`, `json_schema`, `schemas/project-profile.v1.json`.
- [x] 2.2 Tests: example valid and complete, limits equal constants, writer rules present, schema file equals generated, example conforms to the schema.

## 3. Slice: the tool

**Traceability:** Requirement: The profile guide needs no index

- [x] 3.1 `get_profile_guide`; snapshot update.
- [x] 3.2 Tests: no index, equals the domain guide, read-only and no properties, four tools listed.

## 4. Final Verification

- [x] 4.1 `.venv/bin/python -m pytest`: 483 passed, 2 skipped. `python3 -m pytest`: 462 passed, 3 skipped (the MCP test file skips, reason reported).
- [x] 4.2 `python3 scripts/verify_workflows.py` and `python3 scripts/verify_knowledge.py`
- [x] 4.3 `openspec validate be-profile-guide`
- [x] 4.4 Each spec scenario has a test; skips reported.
- [x] 4.5 Called `get_profile_guide` over stdio, wrote its example into a scratch repository as an agent would, ran `vyasa scan`, and `get_project` returned status valid with the declared purpose and no problems.
- [x] 4.6 Review the diff for scope and the contract.

## 5. Documentation and Handover

- [x] 5.1 README note; log entry.

## 6. Review, Merge, and Archive

- [ ] 6.1 Pull request with the change ID.
- [ ] 6.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 6.3 Archive the change.
