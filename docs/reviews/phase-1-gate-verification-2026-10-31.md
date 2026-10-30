# Phase 1 gate verification — 2026-10-31

Phase 1 (Local Workspace Intelligence) against `docs/requirements/phase-acceptance-criteria.md` and
`knowledge/product/scope-and-roadmap/phase-1.md` §4.

**Verdict:** all 12 acceptance criteria verified by checks run in this session. Every §4.2 deliverable is
present except `find_related_projects`, which is a documented deferral (`docs/usage.md` §7) needing an explicit
accepted exception before Phase 2 is declared open.

**Executed on:** `develop` at `eac236a`, Python 3.12 venv, installed backend `E:\MCP\Vyasa MCP` (0.1.4).

## Acceptance criteria

| # | Criterion | Check | Result |
|---|---|---|---|
| 1 | Multiple roots and exclusions configured | Scratch workspace with two roots and a `node_modules` repository; `vyasa scan` reported `ws1: completed - 1 repositories`, `ws2: completed - 1 repositories`, excluded copy not indexed. Also `test_workspace_config.py`, `test_ignore.py` | verified |
| 2 | Projects discovered reproducibly | Second run of the same scan: `1 unchanged` in both roots, `projects.total` stayed 2. Also `test_discovery.py` | verified |
| 3 | Metadata from documented rules only | `test_manifests.py`, `test_manifest_reader.py`, `test_git_remote.py`, `test_languages.py`, `test_markers.py`, `test_file_composition.py`, `test_framework_detection.py` | verified |
| 4 | Unknown fields not fabricated | `test_markers_query.py::test_partial_shows_unknown_for_what_was_not_found`, `test_languages.py::test_partial_makes_absence_unknown`, `test_manifests.py::test_unknown_dependency_creates_nothing` | verified |
| 5 | Queries return records with evidence | `test_project_query.py`, `test_frameworks_query.py`, `test_composition_query.py`, `test_language_query.py` | verified |
| 6 | Query from a different repository | From `E:\Python\VyasaUI`, `vyasa query search --limit 2` returned `"display_name": "agasthya"` and page meta from the installed index | verified |
| 7 | Failures keep previously valid data | Deleted one repository, rescanned: `ws2: completed - 0 repositories (1 missing)`, status `projects: total 2, active 1, missing 1`. Also `test_scan_command.py`, `test_project_scan_failures.py` | verified |
| 8 | Repeats do not duplicate projects | Repeat scan reported `1 unchanged` per root and `total 2`. Also `test_project_identity.py` (rename keeps identity) | verified |
| 9 | Refresh does not overwrite human data | `test_project_profile.py::test_a_scan_leaves_the_repository_untouched`, `::test_declared_name_does_not_replace_the_display_name` | verified |
| 10 | MCP works without external services | Stdio probe of `E:\MCP\Vyasa MCP\vyasa-mcp\vyasa-mcp.exe`: `tools: 8` (`get_index_status`, `get_profile_context`, `get_profile_guide`, `get_project`, `get_project_dependencies`, `get_project_report`, `get_report_template`, `search_projects`). Also `test_mcp_server.py` | verified |
| 11 | Tests cover normal, error, identity, detection | Full suite: `1123 passed, 4 skipped in 35.91s` (48 test modules) | verified |
| 12 | Setup instructions sufficient | Followed `docs/setup.md` and `docs/cli-queries.md` on a fresh `VYASA_HOME`; scan, query and MCP config matched the documented behaviour and layout | verified |

## §4.2 deliverables

| Deliverable | Check | Result |
|---|---|---|
| A. Workspace discovery | Criteria 1–2 rows; `test_discovery.py`, `test_walk_paths.py`, `test_ignore.py` | verified |
| B. Project identity | `test_project_identity.py`, `test_identity_review.py` | verified |
| C. Deterministic metadata | Criterion 3 row; detector modules cover name, remote, languages, frameworks, markers, file composition, profiles, reports | verified |
| D. Local index | `test_local_index.py` (empty create, pending migration with backup, data retained), `test_checkout_scan.py`; real index migrated 11 → 12 in the previous session with 74 projects preserved | verified |
| E. MCP interface | 8 tools served read-only over stdio; planned `get_project_context` ships as `get_profile_context`; `find_related_projects` and an MCP refresh tool are documented as not provided (`docs/usage.md` §7) | verified with deviation |
| F. Profile lifecycle | `test_project_profile.py`, `test_profile_v2.py`, `test_profile_context.py`, `test_profile_guide.py` | verified |
| G. Quality and verification | Criterion 11 row; fixtures, migration and end-to-end temp-workspace tests present | verified |

## Leak check

- `pyproject.toml`: `dependencies = []`; optional extras are `pytest`, `mcp`, `pyinstaller`.
- No provider-API, Google Sheets or HTTP client import in `src/` (only github/bitbucket string labels in
  `domain/git_remote.py` and query enums).
- No network access during the test run or the CLI/MCP probes above.

## Cross-cutting

- **Security:** no secret-shaped literal found in `src/`; scan reads files as text, does not follow links, does not
  execute repository content; report/profile redaction rules are covered by `test_project_report.py`/`test_report_*`.
  This review was performed by the implementing agent in-session, not independently.
- **Dependencies (SCA):** no runtime third-party dependency to audit.
- **Migrations:** covered by `test_local_index.py`; real-index migration verified previously.
- **Failure behaviour:** inaccessible/missing checkouts, malformed manifests, malformed profile/report and a locked
  index are covered by the scanner, scan, profile and index tests.
- **Documentation:** `docs/setup.md`, `docs/usage.md`, `docs/cli-queries.md` commands were executed as written.

## Open items

1. `find_related_projects` is not implemented; related-project data is only partially exposed through profiles.
   Either add it or record an accepted exception for Phase 1.
2. `knowledge/architecture/mcp-interface/*` still describes `get_project_context` and `find_related_projects` as the
   tool contracts; reconcile with the shipped names (`get_profile_context`) when that knowledge is reviewed.
3. Security and MCP reviews above were not independent; an independent review remains advisable before release.
