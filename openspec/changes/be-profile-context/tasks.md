# Implementation Tasks: be-profile-context

- **OpenSpec Change ID:** `be-profile-context`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## Task Planning Rules

Each slice is test first (Red–Green–Refactor) and ends green. Use `python` where `python3` is absent. This change depends on `be-profile-v2` being merged.

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_workflows.py` on `develop` after `be-profile-v2`.
- [x] 1.3 Confirm branch `feature/be-profile-context`.

## 2. Implementation Slice: the differences

**Traceability:** Requirement: Differences compare only where the observation supports it · Knowledge: `knowledge/decisions/profile-context-for-agents.md`

- [x] 2.1 Test first: every finding code with a complete observation, no claim for partial, not assessed, and failed observations, nothing declared in a category, unmatched names as not comparable, version 1 technologies, ubiquitous technologies never undeclared, OpenSpec both ways, agent instruction files including the more-matches-than-stored case, fixed details, sorted and stable output.
- [x] 2.2 Implement `differences` and the fixed detail table in `application/profile_context.py`.
- [x] 2.3 Run tests; refactor.

## 3. Implementation Slice: the stored bundle and the MCP tool

**Traceability:** Requirements: The context bundle contains facts, profile, differences, and workflow; The MCP tool serves the stored observation; The bundle holds no absolute path and no file text; The workflow tells the agent what to do with the facts

- [x] 3.1 Test first: complete bundle, no profile, never-assessed observations, unknown project and invalid input, no absolute path and no manifest text in the serialized bundle, fixed workflow, the tool through the MCP client, and the regenerated snapshot with five tools.
- [x] 3.2 Implement `profile_context`, the `WORKFLOW` constant, and `get_profile_context`; update the tool-count and tool-list tests.
- [x] 3.3 Run tests; regenerate the snapshot and check its diff only adds the tool; refactor.

## 4. Implementation Slice: the live scan

**Traceability:** Requirement: The command scans one checkout live and writes nothing (library part)

- [x] 4.1 Test first: `open_memory_index` is migrated and leaves no file; `enrich_run` behaves as the former private function; `live_context` on a real temporary repository gives a bundle with source `live_scan`, a null project id, and the same observed facts as the stored bundle of the same repository; a non-project directory raises `NotAProject`.
- [x] 4.2 Add `open_memory_index`, make `enrich_run` public and used by `scan_workspace`, and implement `live_context`.
- [x] 4.3 Run tests; refactor.

## 5. Implementation Slice: the command

**Traceability:** Requirements: The command scans one checkout live and writes nothing; Vyasa starts no agent and writes no profile

- [x] 5.1 Test first: default path is the current directory; JSON on standard output with exit 0; missing path and non-project exit 2 with a message on standard error and nothing on standard output; an unexpected failure exits 4 with a generic message; before/after hash of the repository and of a data directory is identical; a profile with differences is unchanged.
- [x] 5.2 Add the `profile-context` subcommand and exit handling to the CLI.
- [x] 5.3 Run tests; refactor.

## 6. Final Verification

- [x] 6.1 `python -m pytest`
- [x] 6.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py`
- [x] 6.3 `openspec validate be-profile-context`
- [x] 6.4 Each spec scenario has a test; record commands, outcomes, failures, skips.
- [x] 6.5 Review the diff for scope and the contract (no write APIs, no absolute path, no file text, no process started).

## 7. Documentation and Handover

- [x] 7.1 README usage updated for the tool and the command. Behavior matches the decision concept.
- [x] 7.2 Mark the decision concepts stable when the owner accepts them.

## 8. Review, Merge, and Archive

- [ ] 8.1 Pull request with the change ID.
- [ ] 8.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 8.3 Archive the change.

## Verification Record

`python -m pytest`: 944 passed, 2 skipped (baseline 891 passed, 2 skipped; 53 new tests in tests/test_profile_context.py, tests/test_profile_context_live.py, tests/test_profile_context_cli.py, and tests/test_mcp_server.py). The skips are the existing link tests. The MCP tool snapshot was regenerated; its diff only adds the tool. A real run of `vyasa profile-context .` on this repository printed an 11 KB bundle with source `live_scan`, exit 0, and changed nothing. `openspec validate` is clean apart from the usual warnings.

## Completion Summary

Not yet complete.
