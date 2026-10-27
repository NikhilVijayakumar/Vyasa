# Change Proposal: be-scan-command

## Why

The index and the MCP server exist, but nothing builds the index, so every MCP tool reports it unavailable. Vyasa needs an explicit `vyasa scan` command that scans only the workspace roots in the configuration, creates the data directory and index on first use, and reports exactly what it did per root.

## What Changes

- **scan-command**: a new capability. A `vyasa scan` command (console script and `python -m vyasa`) that loads the configured roots, discovers repositories in each, stores one run per root in the local index, and prints a per-root report with a status-based exit code.

## 1. Problem and Motivation

### Current Situation

`load_workspace_config`, `discover_repositories`, and `store_run` exist and are tested, but only callable from Python. There is no entry point. The MCP server never scans (by decision).

### Problem

An owner cannot populate or refresh the index. FR-001, FR-015 and the explicit-operations principle require a deliberate command that stays inside configured roots and reports partial results honestly.

### Evidence

- Verified: the data directory, index, and configuration locations are resolved by `data_directory`, `index_path`, and `load_workspace_config`; the first `open_index` creates the directory and file.
- Verified: no detector cache exists yet because no detector exists; the index is the only metadata store.
- Verified: the owner asked on 2026-10-27 that scanning cover only the configured workspace roots (several allowed), create what it needs on first run, and not touch the rest of the system.

## 2. Desired Outcome

### Goals

- [ ] Scan every configured root, and nothing else.
- [ ] Create the data directory and index on first use.
- [ ] Report each root's status, counts, and skipped directories.
- [ ] Exit non-zero when anything is partial, failed, or misconfigured.

### Team Focus

Trust boundary (only configured roots), explicit operation, failure modes (bad config, missing root, concurrent scan), honest partial reporting.

### Success Criteria

- [ ] A sibling directory outside the roots is never visited.
- [ ] The first run creates the index; a second run reports unchanged projects and no duplicates.
- [ ] A missing root is reported and does not stop the other roots.
- [ ] A second concurrent scan exits with `OPERATION_IN_PROGRESS`.

## 3. Scope

### In Scope

- `vyasa.application.indexing.scan` (multi-root orchestration) and `vyasa.adapters.cli` (argument parsing, output, exit codes).
- `vyasa` console script and `python -m vyasa`.
- Options: `--config PATH` only.

### Out of Scope

- Detectors and their cache (languages, frameworks, README, tests); the profile (next change).
- Scheduling, watching, incremental skipping of unchanged repositories, parallel roots.
- Any MCP refresh tool (disabled by decision).
- Configuration editing commands.

### Constraints

Standard library (`argparse`); read-only toward repositories; bounded by existing discovery limits.

## 4. Stakeholders and Impact

- **Primary stakeholders:** the owner.
- **Affected components or capabilities:** new `vyasa.adapters.cli`, `vyasa.application.indexing.scan`; `pyproject.toml` script.
- **Dependencies:** all merged index and discovery changes.
- **Compatibility considerations:** new surface; core stays dependency-free.

## 5. Proposed Direction

`scan_workspace(config, connection, owner)` loops over `config.roots` in order, runs `discover_repositories` and `store_run` for each, and returns a result per root. The CLI loads configuration, opens the index (creating it), calls the function, prints a report, and maps outcomes to exit codes. Considered: one combined run across roots (the run model is per root) and a long-lived service (not local-first-simple).

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Scan only configured roots | no outside access | Must |
| REQ-002 | First run bootstraps | directory and index created | Must |
| REQ-003 | Per-root reporting | status, counts, skips | Must |
| REQ-004 | Honest exit codes | partial and failure visible | Must |
| REQ-005 | Misconfiguration is clear | no scan, exit 2 | Must |

## 7. Risks and Open Questions

### Risks

| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| One slow root delays the rest | Long first scan | Roots are independent; discovery limits apply |
| A root on another drive is unplugged | Failed run for that root | Reported; nothing marked missing |

### Assumptions

- Roots are scanned sequentially.

### Open Questions

- [ ] Whether `vyasa scan` should accept a root subset (`--root`) later.

## 8. Acceptance Summary

- [ ] Every spec scenario has a test.
- [ ] `pytest`, `verify_workflows.py`, `verify_knowledge.py`, `openspec validate` pass.

## 9. Traceability

- **OpenSpec Change ID:** `be-scan-command`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-scan-command`
- **Requirement package:** `docs/requirements/workspace-discovery/requirement.md`
- **Knowledge references:**
  - `knowledge/concepts/explicit-operations.md` — scanning is a deliberate command
  - `knowledge/decisions/configuration-file-format-and-location.md` — where roots come from
  - `knowledge/decisions/index-lifecycle-and-single-writer.md` — one writer
  - `knowledge/decisions/partial-results-never-imply-absence.md` — honest reporting
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/workspace-configuration`, `openspec/specs/repository-discovery`, `openspec/specs/local-index`
- **Related ADRs:** `knowledge/concepts/explicit-operations.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved, or explicitly recorded.
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
