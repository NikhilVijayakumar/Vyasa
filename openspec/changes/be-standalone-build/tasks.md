# Implementation Tasks: be-standalone-build

- **OpenSpec Change ID:** `be-standalone-build`
- **Status:** Ready for implementation
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, specs, contract, design, and ADR.
- [x] 1.2 Record the baseline: `venv\Scripts\python.exe -m pytest` (1000 passed, 2 skipped).
- [x] 1.3 Confirm branch `feature/be-standalone-build`.

## 2. Slice: frozen data directory

**Traceability:** Requirement: Locate the configuration file

- [x] 2.1 Tests first: frozen, `VYASA_HOME` override, and source cases.
- [x] 2.2 `frozen_executable` parameter on `data_directory`.

## 3. Slice: install layout

**Traceability:** Requirements: Both executables are built into one root; A rebuild preserves the data; The output root comes from the environment

- [x] 3.1 Tests first: `install()` places both bundles, seeds config once, preserves existing data.
- [x] 3.2 Parameterise the PyInstaller call; build both bundles in a temp directory; `install()`.

## 4. Documentation and verification

- [x] 4.1 Update `docs/setup.md` and `.env.example`.
- [x] 4.2 Real build here; `vyasa.exe scan` and `vyasa-mcp.exe` share one `data/`.
- [x] 4.3 `pytest`, `verify_workflows.py`, `verify_knowledge.py`, `openspec validate be-standalone-build`.
- [x] 4.4 Knowledge capture: update the configuration decision.
