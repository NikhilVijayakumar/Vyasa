# Implementation Tasks: be-profile-read

- **OpenSpec Change ID:** `be-profile-read`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `.venv/bin/python -m pytest` and `python3 scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-profile-read`.

## 2. Slice: validate a profile

**Traceability:** Requirement: Fields are validated one by one · Knowledge: `knowledge/decisions/canonical-profile-and-draft.md`

- [x] 2.1 `vyasa.domain.profile`.
- [x] 2.2 Tests: valid, one bad field, unsupported version, limits, relative entry point, unknown fields, control characters.

## 3. Slice: read the file safely

**Traceability:** Requirement: The profile is read safely

- [x] 3.1 `read_profile`; `Candidate.profile`; attach in the walk.
- [x] 3.2 Tests: valid, absent, link, oversize, malformed, manifest project with Git in a child folder, tree hash unchanged.

## 4. Slice: store declared values

**Traceability:** Requirement: Declared values keep their source

- [x] 4.1 `0005_checkout_profiles.sql`; store and replace per checkout.
- [x] 4.2 Tests: stored after restart, edited, removed, migration from schema 4.

## 5. Slice: show it in project details

**Traceability:** Requirement: Project details show the profile

- [x] 5.1 `profile` in `get_project`; checkout choice rule.
- [x] 5.2 Tests: declared values, absent, invalid, name does not replace display name, two checkouts, MCP snapshot unchanged.

## 6. Final Verification

- [x] 6.1 `.venv/bin/python -m pytest`: 472 passed, 2 skipped. `python3 -m pytest`: 454 passed, 3 skipped (the MCP test file skips, reason reported).
- [x] 6.2 `python3 scripts/verify_workflows.py` and `python3 scripts/verify_knowledge.py`
- [x] 6.3 `openspec validate be-profile-read`
- [x] 6.4 Each spec scenario has a test; skips reported.
- [x] 6.5 A scratch repository with a profile was scanned by `vyasa scan`; `get_project` over real MCP stdio returned the declared name, purpose, lifecycle, and tags with their source.
- [x] 6.6 Review the diff for scope and the contract.

## 7. Documentation and Handover

- [x] 7.1 Update the profile decision to TOML; README note; log entry.
- [ ] 7.2 Mark the decision concept accepted when the owner accepts it.

## 8. Review, Merge, and Archive

- [ ] 8.1 Pull request with the change ID.
- [ ] 8.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 8.3 Archive the change.
