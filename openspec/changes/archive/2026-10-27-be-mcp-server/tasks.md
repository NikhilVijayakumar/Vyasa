# Implementation Tasks: be-mcp-server

- **OpenSpec Change ID:** `be-mcp-server`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `.venv/bin/python -m pytest` and `python3 scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-mcp-server`.

## 2. Prerequisite: packaging

**Traceability:** Requirement: The SDK is an optional extra

- [x] 2.1 `[mcp]` extra, `vyasa-mcp` script, `python -m` entry, hint on missing SDK.
- [x] 2.2 Tests: core works with `mcp` blocked; entry point exits non-zero with a hint.

## 3. Slice: server and index status

**Traceability:** Requirements: The server speaks stdio and lists its tools; Tools return structured, read-only results

- [x] 3.1 `build_server`, `_run`, `get_index_status`.
- [x] 3.2 Tests: list tools, status envelope, file bytes unchanged.

## 4. Slice: search and project tools

**Traceability:** Requirement: Tools return structured, read-only results

- [x] 4.1 `search_projects`, `get_project`.
- [x] 4.2 Tests: search envelope, project record, unregistered tool.

## 5. Slice: structured failures

**Traceability:** Requirement: Failures are structured results

- [x] 5.1 Error mapping including missing index and unexpected exceptions.
- [x] 5.2 Tests: each code; no file created for a missing index.

## 6. Slice: pinned contract and no paths

**Traceability:** Requirements: The tool contract is pinned; No paths cross the boundary

- [x] 6.1 Snapshot file and update switch.
- [x] 6.2 Tests: snapshot match, read-only hints, no path property, no path in results.

## 7. Slice: stdio smoke

**Traceability:** Requirement: The server speaks stdio and lists its tools

- [x] 7.1 Subprocess test over stdio: list tools and call a tool; output is protocol only.

## 8. Final Verification

- [x] 8.1 `.venv/bin/python -m pytest`: 409 passed, 2 skipped. System `python3 -m pytest`: 391 passed, 3 skipped (the MCP test file skips, reason reported).
- [x] 8.2 `python3 scripts/verify_workflows.py` and `python3 scripts/verify_knowledge.py`
- [x] 8.3 `openspec validate be-mcp-server`
- [x] 8.4 Each spec scenario has a test; skips reported.
- [x] 8.5 Started `vyasa-mcp` over stdio against a scratch index of ~/PycharmProjects (35 projects): three tools listed, search found this repository, status current.
- [x] 8.6 Review the diff for scope and the contract.

## 9. Documentation and Handover

- [x] 9.1 README note on running the server; log entry if behavior diverged.
- [ ] 9.2 Mark decisions accepted when the owner accepts them.

## 10. Review, Merge, and Archive

- [ ] 10.1 Pull request with the change ID.
- [ ] 10.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 10.3 Archive the change.
