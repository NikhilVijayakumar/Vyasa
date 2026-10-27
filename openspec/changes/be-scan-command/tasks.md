# Implementation Tasks: be-scan-command

- **OpenSpec Change ID:** `be-scan-command`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `.venv/bin/python -m pytest` and `python3 scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-scan-command`.

## 2. Slice: scan configured roots

**Traceability:** Requirements: Only configured roots are scanned; Scanning does not change repositories

- [x] 2.1 `scan_workspace`.
- [x] 2.2 Tests: two roots plus an outside sibling, nested roots, tree hash unchanged.

## 3. Slice: bootstrap and report

**Traceability:** Requirements: The first run creates what it needs; Each root is reported

- [x] 3.1 CLI `scan`, report formatting, entry points.
- [x] 3.2 Tests: first and repeated scan, complete root, skipped directories, missing root.

## 4. Slice: exit codes

**Traceability:** Requirement: The exit code tells the truth

- [x] 4.1 Exit-code mapping for configuration, concurrency, and index errors.
- [x] 4.2 Tests: 0, 1, 2 (absent, invalid), 3, 4; nothing created on configuration errors.

## 5. Final Verification

- [x] 5.1 `.venv/bin/python -m pytest`: 423 passed, 2 skipped. `python3 -m pytest`: 405 passed, 3 skipped (the MCP test file skips, reason reported).
- [x] 5.2 `python3 scripts/verify_workflows.py` and `python3 scripts/verify_knowledge.py`
- [x] 5.3 `openspec validate be-scan-command`
- [x] 5.4 Each spec scenario has a test; skips reported.
- [x] 5.5 Scanned ~/PycharmProjects and a scratch workspace from a scratch config: 36 projects, exit 0; a second scan reported everything unchanged; the MCP server read the same index and reported freshness current.
- [x] 5.6 Review the diff for scope and the contract.

## 6. Documentation and Handover

- [x] 6.1 README section; log entry if behavior diverged.

## 7. Review, Merge, and Archive

- [ ] 7.1 Pull request with the change ID.
- [ ] 7.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 7.3 Archive the change.
