# Change Proposal: be-standalone-build

## Why

The MCP server can be built as a standalone executable, but the `vyasa` command that creates the index cannot. A coding agent working in another repository can only run `vyasa scan` through this repository's `venv`, and the data directory is wherever the user's profile points. Vyasa needs one install folder, chosen by an environment variable, that holds both executables and the data (configuration and index), so any process on the machine can scan or query the same data without this repository.

## What Changes

- **standalone-build**: `scripts/build_mcp.py` builds both `vyasa` and `vyasa-mcp` into one install root, and seeds `data/config.toml` from the example when absent.
- **workspace-configuration**: a built (frozen) executable with no `VYASA_HOME` uses the `data/` folder beside its `bin` folders as the data directory, so the two executables and every caller share it with no environment setup.

## 1. Problem and Motivation

### Current Situation

`scripts/build_mcp.py` writes `<out>/<name>/vyasa-mcp.exe`. `vyasa scan` exists only as a venv script. The data directory defaults to the per-user application-data folder.

### Problem

Scanning needs this repository's venv. The data lives apart from the executables, so moving or sharing an install means also setting `VYASA_HOME` everywhere.

### Evidence

- Verified: `pyproject.toml` defines `vyasa` and `vyasa-mcp` scripts; only `vyasa-mcp` is built.
- Verified: `data_directory()` resolves `VYASA_HOME`, then a per-platform folder.

## 2. Desired Outcome

### Goals

- [ ] One build produces `bin`-style folders for both executables and a `data` folder under one root taken from the environment.
- [ ] The built executables find that `data` folder without `VYASA_HOME`.
- [ ] `VYASA_HOME` and `VYASA_CONFIG` still override.
- [ ] Source and venv runs behave exactly as before.

### Team Focus

Trust boundary of the data directory, no behavior change outside frozen builds, never overwriting a user's config or index on rebuild.

### Success Criteria

- [ ] A frozen executable resolves `<root>/data`; a non-frozen run is unchanged.
- [ ] Rebuilding preserves `data/`.
- [ ] `vyasa.exe scan` and `vyasa-mcp.exe` share one index with no environment variable.

## 3. Scope

### In Scope

- `data_directory()` frozen-build rule; `scripts/build_mcp.py` builds both executables and seeds the config; `docs/setup.md`; `.env.example`.

### Out of Scope

- An MCP refresh tool (the MCP stays read-only).
- Installers, code signing, cross-compiling, auto-start of the MCP server.

### Constraints

Standard library only; PyInstaller stays an optional `build` extra; builds are per OS.

## 4. Stakeholders and Impact

- **Primary stakeholders:** the maintainer; coding agents in other repositories.
- **Affected components or capabilities:** `vyasa.application.configuration.workspace`, `scripts/build_mcp.py`, setup guide.
- **Dependencies:** `be-workspace-config`, `be-mcp-server` (merged).
- **Compatibility considerations:** the MCP executable moves to `<root>/vyasa-mcp/vyasa-mcp[.exe]`; clients update their command path once.

## 5. Proposed Direction

Install layout under `<VYASA_MCP_OUT>/<name>/`: `vyasa/vyasa[.exe]`, `vyasa-mcp/vyasa-mcp[.exe]`, `data/`. Each executable is its own PyInstaller one-folder build because one folder cannot hold two onedir bundles without clashing. A frozen executable looks one folder up from its own folder for `data/`. Considered: one executable with a `mcp` subcommand (changes the MCP client command), and an installer-managed data folder (out of scope).

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Both executables are built into one root | one place to install | Must |
| REQ-002 | Frozen executables use the sibling `data` folder | shared data, no setup | Must |
| REQ-003 | Environment overrides still win | flexibility | Must |
| REQ-004 | A rebuild never overwrites `data/` | no data loss | Must |

## 7. Risks and Open Questions

### Risks

| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Rebuild deletes the index | Lost data | Build removes only `vyasa/` and `vyasa-mcp/`, never `data/` |
| Frozen detection misfires in tests | Wrong data directory | Frozen flag and executable path are parameters |

### Assumptions

- The install root is writable by the user who scans.

### Open Questions

- [ ] An MCP refresh tool, later, if agents need it.

## 8. Acceptance Summary

- [ ] Every spec scenario has a test.
- [ ] `pytest`, `verify_workflows.py`, `verify_knowledge.py`, `openspec validate` pass.
- [ ] A real build on this machine runs `vyasa scan` and `vyasa-mcp` against one `data/`.

## 9. Traceability

- **OpenSpec Change ID:** `be-standalone-build`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-standalone-build`
- **Requirement package:** `docs/requirements/` (workspace configuration)
- **Knowledge references:**
  - `knowledge/decisions/configuration-file-format-and-location.md` — data directory rule
  - `knowledge/decisions/index-lifecycle-and-single-writer.md` — the CLI writes, the MCP reads
  - `knowledge/decisions/mcp-local-paths-omitted-by-default.md` — paths stay in the data folder
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/workspace-configuration`, `openspec/specs/mcp-server`
- **Related ADRs:** `knowledge/decisions/configuration-file-format-and-location.md`

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
