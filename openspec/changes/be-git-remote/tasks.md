# Implementation Tasks: be-git-remote

- **OpenSpec Change ID:** `be-git-remote`
- **Status:** Not Started
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

> Order of work, by owner instruction 2026-10-27: implement first, then write repository tests that anyone can re-run.

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [ ] 1.3 Confirm branch `feature/be-git-remote`.

## 2. Implementation Slice: parse, normalize, label, choose

**Traceability:** Requirements: Remotes are read from the config text; URLs are reduced to a credential-free identity; The provider comes from the host; One remote is chosen · Knowledge: `knowledge/decisions/git-remote-provider-labels.md`

- [ ] 2.1 Implement `vyasa.domain.git_remote`.
- [ ] 2.2 Tests: a URL-form table, credentials, ports, case, local forms, parsing, choice.

## 3. Implementation Slice: read and attach

**Traceability:** Requirements: The config is read safely; Discovery attaches the remote

- [ ] 3.1 Implement `read_remote`, the `Candidate` fields, and the walk calls.
- [ ] 3.2 Tests: config read, pointer file, oversized, linked, repository, child-folder Git, no Git, files opened.

## 4. Final Verification

- [ ] 4.1 `python -m pytest`
- [ ] 4.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [ ] 4.3 `openspec validate be-git-remote`
- [ ] 4.4 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [ ] 4.5 Run discovery on the real workspaces (read-only) and record the provider counts.
- [ ] 4.6 Review the diff for scope and the contract (no credential kept).

## 5. Documentation and Handover

- [ ] 5.1 Update the knowledge decision if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 5.2 Mark the decision concept accepted when the owner accepts it.

## 6. Review, Merge, and Archive

- [ ] 6.1 Pull request with the change ID.
- [ ] 6.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 6.3 Archive the change.
