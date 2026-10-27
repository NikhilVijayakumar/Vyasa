# Implementation Tasks: be-scan-command

- **OpenSpec Change ID:** `be-scan-command`
- **Status:** Planned
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `.venv/bin/python -m pytest` and `python3 scripts/verify_knowledge.py`.
- [ ] 1.3 Confirm branch `feature/be-scan-command`.

## 2. Slice: scan configured roots

**Traceability:** Requirements: Only configured roots are scanned; Scanning does not change repositories

- [ ] 2.1 `scan_workspace`.
- [ ] 2.2 Tests: two roots plus an outside sibling, nested roots, tree hash unchanged.

## 3. Slice: bootstrap and report

**Traceability:** Requirements: The first run creates what it needs; Each root is reported

- [ ] 3.1 CLI `scan`, report formatting, entry points.
- [ ] 3.2 Tests: first and repeated scan, complete root, skipped directories, missing root.

## 4. Slice: exit codes

**Traceability:** Requirement: The exit code tells the truth

- [ ] 4.1 Exit-code mapping for configuration, concurrency, and index errors.
- [ ] 4.2 Tests: 0, 1, 2 (absent, invalid), 3, 4; nothing created on configuration errors.

## 5. Final Verification

- [ ] 5.1 `.venv/bin/python -m pytest` and `python3 -m pytest`
- [ ] 5.2 `python3 scripts/verify_workflows.py` and `python3 scripts/verify_knowledge.py`
- [ ] 5.3 `openspec validate be-scan-command`
- [ ] 5.4 Each spec scenario has a test; skips reported.
- [ ] 5.5 Real run: configure scratch roots and scan, then query over MCP.
- [ ] 5.6 Review the diff for scope and the contract.

## 6. Documentation and Handover

- [ ] 6.1 README section; log entry if behavior diverged.

## 7. Review, Merge, and Archive

- [ ] 7.1 Pull request with the change ID.
- [ ] 7.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 7.3 Archive the change.
