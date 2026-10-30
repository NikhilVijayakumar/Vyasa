# Tasks: be-project-scan

All tasks require evidence before completion. Use disposable SQLite files and isolated temporary workspace roots for all scan tests. Apply test-first development for each behavior. Knowledge references: `knowledge/architecture/data-model/relationships-and-runs.md`, `knowledge/architecture/scanning-and-evidence/incremental-and-partial.md`, `knowledge/concepts/field-ownership.md`, and `knowledge/decisions/project-scoped-scan-freshness.md`.

## Prerequisites

- [x] 1.1 Independently review the specification, contract and design with the UI consumer; settle provisional or remote-less identity handling and moved-checkout evidence without treating missing as proof of a move.
- [x] 1.2 Verify the field ownership matrix, branch and repository baseline; run required planning validators and record results.

## Vertical slices

- [x] 2.1 Implement and test migration preserving old run history as workspace-scoped, per-checkout outcomes, and both workspace-only freshness queries against disposable real SQLite databases.
- [x] 2.2 Implement and test selection and safe successful scanning of all eligible indexed checkouts for one project, including preservation of other projects and repository bytes.
- [x] 2.3 Implement and test explicit outcomes for missing, inaccessible, out-of-root, moved when evidenced, identity-conflicting and failing checkouts, including useful partial results and writer-lock behavior.
- [x] 2.4 Implement and contract-test the structured CLI operation, invalid identifiers and options, error codes, exit codes and backward-compatible workspace scans.

## Verification and handoff

- [x] 3.1 Run requirement-traced unit, contract, isolated filesystem and database migration tests and the backend's required workflow and knowledge validators; record commands, results, failures and skips.
- [x] 3.2 Independently review implementation for identity, containment, data preservation and contract compliance; verify the UI integration against the actual backend CLI.
- [x] 3.3 Update user and developer documentation, capture durable lessons in knowledge, and report outstanding limitations and verification evidence.

## Planning evidence

Backend branch: feature/be-project-scan; pre-existing untracked scripts, logs and change artifacts were preserved. Field ownership matrix records local scope and checkout outcomes. `openspec validate be-project-scan` passed; backend venv `scripts/verify_workflows.py`, `scripts/verify_knowledge.py`, `scripts/verify_requirements.py`, `-m unittest scripts.test_verify_knowledge scripts.test_verify_requirements`, `scripts/smoke_team_schemas.py` and `-m unittest scripts.test_sync_skills` passed. Requirements verification reports 45 existing grill questions needing decisions. Independent review resolved identity, storage and CLI contract findings; UI consumer requires capability probing and structured outcome parsing.

Migration evidence: pytest tests/test_project_scan_legacy.py tests/test_project_scan_scope.py tests/test_local_index.py tests/test_project_query.py: 85 passed, 1 POSIX-only skip; full backend pytest: 1096 passed, 4 skipped. Tests use disposable SQLite files, including legacy child references, backup, foreign-key checks and rollback. Independent reviewer confirmed the legacy read-only fix and slice coverage.

Project scan evidence: isolated tests in test_project_scan_command.py, test_project_scan_failures.py, test_project_scan_review.py, test_project_scan_child_git.py, test_project_scan_pointers.py and test_project_scan_coverage.py cover selection, multi-root outcomes, incomplete evidence, conflicts, containment, lock, CLI errors and preservation. Full backend pytest: 1121 passed, 4 skipped (one POSIX-only and three symbolic-link privilege checks). No move evidence source exists; MOVED is reserved and missing paths report MISSING. Independent reviewer confirmed these slice checks.

Final backend verification: `venv/Scripts/python.exe -m pytest -q -rs`: 1122 passed, 4 skipped (POSIX permissions and three Windows symlink-privilege cases); the subsequently added malformed-manifest preservation test passed separately. `openspec validate be-project-scan`, `venv/Scripts/python.exe scripts/verify_workflows.py` and `scripts/verify_knowledge.py` passed. Trace: selection and per-checkout reporting -> test_project_scan_command.py and test_project_scan_coverage.py; failure and safety -> test_project_scan_failures.py and test_project_scan_review.py; pointer and indexed child compatibility -> test_project_scan_pointers.py and test_project_scan_child_git.py; history and freshness -> test_project_scan_scope.py and test_project_scan_legacy.py. Tests provision temporary roots and file-backed databases.

Review evidence (3.2): reviewed the scan path against the contract and design: identity conflicts surface as IDENTITY_CONFLICT through `projects.upsert` and never attach to another project; only checkouts under a configured root are inspected, and a link or junction on the path reports OUTSIDE_CONFIGURED_ROOTS; per-checkout upserts preserve other projects, break on incomplete observations before storing, and never call root-wide absence reconciliation; project runs are excluded from `latest_workspace_run`, so freshness and status keep reading workspace runs. No separate reviewer was used; the review was carried out in-session by the implementing agent at the user's instruction to proceed without subagents.

CLI integration evidence (3.2): `node tests/project-scan-integration.cjs` and `node tests/project-scan-electron.cjs` in VyasaUI passed against `E:\Python\Vyasa\venv\Scripts\vyasa.exe`, covering the isolated IPC path and the keyboard/scan journey. A direct contract spot-check with an isolated `VYASA_HOME` and temporary roots verified: `query capabilities` returns `{"schema_version":"1","data":{"capabilities":{"project_scan":1}}}` without config or index; `--json` alone, `--project` without `--json`, an extra argument and `--workspace` with `--project` each return INVALID_INPUT with exit 2; a project request before any index returns INDEX_UNAVAILABLE with exit 4; an unindexed identifier returns PROJECT_NOT_FOUND with exit 2 and scans nothing; a completed project run exits 0; after removing one checkout the same project run reports `failed` with `MISSING` and exits 1. Backend suite: 1123 passed, 4 skipped.

Documentation and knowledge evidence (3.3): README, `docs/usage.md` and `docs/cli-queries.md` describe the command, capability probe, JSON status versus exit 1 and unchanged freshness; `docs/requirements/data-ownership.md` gained the scope and outcome rows; `knowledge/decisions/project-scoped-scan-freshness.md` (with its index entry and log line) records the decision and the no-move-evidence limit. `openspec validate be-project-scan`, `scripts/verify_workflows.py`, `scripts/verify_knowledge.py` (152 concepts, 0 errors) and `scripts/verify_requirements.py` (0 errors) passed.

Outstanding limitations: `MOVED` has no evidence source and is never emitted, so an absent recorded path is `MISSING`; project runs deliberately do not refresh index-wide freshness or status; checkouts reached through a link or junction are reported OUTSIDE_CONFIGURED_ROOTS rather than followed. The installed distribution at `E:\MCP\Vyasa MCP` was rebuilt after this review: `vyasa.exe` reports 0.1.4 and advertises `project_scan` 1, and a project scan of a copy of the real index migrated schema 11 to 12 while keeping 74 projects and 74 checkouts and reading the three old runs as workspace-scoped.
