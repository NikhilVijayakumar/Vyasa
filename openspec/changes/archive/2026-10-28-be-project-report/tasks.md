# Implementation Tasks: be-project-report

- **OpenSpec Change ID:** `be-project-report`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, specs, contract, design, and ADR.
- [x] 1.2 Record the baseline: `venv\Scripts\python.exe -m pytest` (1005 passed, 2 skipped) and `python scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-project-report`.

## 2. Slice: template over MCP

**Traceability:** Requirements: The template is generated from the section definition; The report template needs no index

- [x] 2.1 Tests first: example reads clean, limits equal constants, rules present, tool works with no index.
- [x] 2.2 `vyasa.domain.report` (`SECTIONS`, limits, `read_report`, `report_template`, `EXAMPLE`); `get_report_template` tool; tool snapshot update.

## 3a. Slice: configurable limits

**Traceability:** Requirement: Report limits are configurable inside bounds

- [x] 3a.1 Tests first: defaults, values, out of bounds, section above file, wrong type, unknown key.
- [x] 3a.2 `ReportLimits`, the `report` table in `load_workspace_config`, `examples/config.toml` comment.

## 3. Slice: scan reads and stores the report

**Traceability:** Requirements: The report is read safely; Sections are kept by name and bounded; Stored reports keep their provenance; Vyasa writes no report and starts no agent

- [x] 3.1 Tests first: configured limit applied and recorded, missing, link, oversize, valid, unknown and duplicate headings, credential URL, control characters, failed read keeps rows, repository hash unchanged.
- [x] 3.2 Scanner step with the safe-read helper; migration `0011_project_report.sql`; store step.

## 4. Slice: serve the report

**Traceability:** Requirements: The stored report is served as declared data; Project details show the report status only

- [x] 4.1 Tests first: whole, one section, unknown section, no report, unknown project, status without text, no path.
- [x] 4.2 `get_project_report` tool; `report` object in `get_project`.

## 5. Slice: workflow step

**Traceability:** Requirement: The workflow names the report

- [x] 5.1 Tests first: step present, status per checkout.
- [x] 5.2 Context bundle change.

## 6. Documentation and verification

- [x] 6.1 Update `docs/setup.md` (tools, report path, rescan) and the README tool list.
- [x] 6.2 End to end with the built MCP: write a report in a temp repo, `vyasa scan`, fetch it.
- [x] 6.3 `pytest`, `verify_workflows.py`, `verify_knowledge.py`, `verify_requirements.py`, `openspec validate be-project-report`.
- [x] 6.4 Knowledge capture: accept the decision; update the profile-context decision if the workflow wording changes.
