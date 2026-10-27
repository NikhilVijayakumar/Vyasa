# Implementation Tasks: be-mcp-server

- **OpenSpec Change ID:** `be-mcp-server`
- **Status:** Planned
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [ ] 1.1 Review the proposal, spec, contract, design, and ADR.
- [ ] 1.2 Record the baseline: `.venv/bin/python -m pytest` and `python3 scripts/verify_knowledge.py`.
- [ ] 1.3 Confirm branch `feature/be-mcp-server`.

## 2. Prerequisite: packaging

**Traceability:** Requirement: The SDK is an optional extra

- [ ] 2.1 `[mcp]` extra, `vyasa-mcp` script, `python -m` entry, hint on missing SDK.
- [ ] 2.2 Tests: core works with `mcp` blocked; entry point exits non-zero with a hint.

## 3. Slice: server and index status

**Traceability:** Requirements: The server speaks stdio and lists its tools; Tools return structured, read-only results

- [ ] 3.1 `build_server`, `_run`, `get_index_status`.
- [ ] 3.2 Tests: list tools, status envelope, file bytes unchanged.

## 4. Slice: search and project tools

**Traceability:** Requirement: Tools return structured, read-only results

- [ ] 4.1 `search_projects`, `get_project`.
- [ ] 4.2 Tests: search envelope, project record, unregistered tool.

## 5. Slice: structured failures

**Traceability:** Requirement: Failures are structured results

- [ ] 5.1 Error mapping including missing index and unexpected exceptions.
- [ ] 5.2 Tests: each code; no file created for a missing index.

## 6. Slice: pinned contract and no paths

**Traceability:** Requirements: The tool contract is pinned; No paths cross the boundary

- [ ] 6.1 Snapshot file and update switch.
- [ ] 6.2 Tests: snapshot match, read-only hints, no path property, no path in results.

## 7. Slice: stdio smoke

**Traceability:** Requirement: The server speaks stdio and lists its tools

- [ ] 7.1 Subprocess test over stdio: list tools and call a tool; output is protocol only.

## 8. Final Verification

- [ ] 8.1 `.venv/bin/python -m pytest` and system `python3 -m pytest` (MCP tests skipped and reported)
- [ ] 8.2 `python3 scripts/verify_workflows.py` and `python3 scripts/verify_knowledge.py`
- [ ] 8.3 `openspec validate be-mcp-server`
- [ ] 8.4 Each spec scenario has a test; skips reported.
- [ ] 8.5 Real workspace: start the server and query the scratch index over stdio.
- [ ] 8.6 Review the diff for scope and the contract.

## 9. Documentation and Handover

- [ ] 9.1 README note on running the server; log entry if behavior diverged.
- [ ] 9.2 Mark decisions accepted when the owner accepts them.

## 10. Review, Merge, and Archive

- [ ] 10.1 Pull request with the change ID.
- [ ] 10.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 10.3 Archive the change.
