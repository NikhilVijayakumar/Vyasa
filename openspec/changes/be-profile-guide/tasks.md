# Implementation Tasks: be-profile-guide

- **OpenSpec Change ID:** `be-profile-guide`
- **Status:** Planned
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `.venv/bin/python -m pytest` and `python3 scripts/verify_knowledge.py`.
- [ ] 1.3 Confirm branch `feature/be-profile-guide`.

## 2. Slice: the guide and the schema

**Traceability:** Requirements: The guide is generated from the validation rules; A JSON Schema is committed

- [ ] 2.1 `profile_guide`, `json_schema`, `schemas/project-profile.v1.json`.
- [ ] 2.2 Tests: example valid and complete, limits equal constants, writer rules present, schema file equals generated, example conforms to the schema.

## 3. Slice: the tool

**Traceability:** Requirement: The profile guide needs no index

- [ ] 3.1 `get_profile_guide`; snapshot update.
- [ ] 3.2 Tests: no index, equals the domain guide, read-only and no properties, four tools listed.

## 4. Final Verification

- [ ] 4.1 `.venv/bin/python -m pytest` and `python3 -m pytest`
- [ ] 4.2 `python3 scripts/verify_workflows.py` and `python3 scripts/verify_knowledge.py`
- [ ] 4.3 `openspec validate be-profile-guide`
- [ ] 4.4 Each spec scenario has a test; skips reported.
- [ ] 4.5 Real run: call the tool over stdio, write the example into a scratch repository, scan, and read it back.
- [ ] 4.6 Review the diff for scope and the contract.

## 5. Documentation and Handover

- [ ] 5.1 README note; log entry.

## 6. Review, Merge, and Archive

- [ ] 6.1 Pull request with the change ID.
- [ ] 6.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 6.3 Archive the change.
