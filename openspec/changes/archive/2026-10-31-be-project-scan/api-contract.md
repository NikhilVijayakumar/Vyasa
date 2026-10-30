# Interface and Data Contract: be-project-scan

Status: Draft. This is a proposed contract for review and implementation planning.

## CLI operation

`vyasa scan --project PROJECT_ID --json` selects one indexed project by its opaque project identifier. `--project` and `--workspace` are mutually exclusive; `--config` keeps its existing meaning. The process uses configured roots and the local index. It accepts no checkout path from the caller and does not create an index for an unknown project. Existing scan commands keep their current behavior. No new MCP or synchronization operation is introduced.

On a terminal result, stdout is one JSON object with `schema_version: "1"` and `data` containing `project_id`, `run_id`, `status` (`completed`, `partial`, or `failed`), and `checkouts`: an array of objects with `checkout_id`, `status` (`completed` or `failed`), and `reason` (null on success, otherwise a stable code). Reason codes include `MISSING`, `INACCESSIBLE`, `MOVED`, `IDENTITY_CONFLICT`, and `SCAN_FAILED`. A checkout outside configured roots is not inspected and is reported as `OUTSIDE_CONFIGURED_ROOTS`. The run is completed only if all required checkout observations complete; useful observations with failures yield partial, and failure to accomplish the essential operation yields failed. Diagnostics must not include credentials or raw exception text.

## Trust and ownership

Configured roots and the local index determine eligible paths; repository contents and Git metadata are untrusted data and are never executed. Checkout paths and root paths are machine-local and must not be exported to Sheets or remote callers. Scan scope and item outcomes are Vyasa-generated operational state. Repository-owned and portfolio-owned fields remain authoritative at their existing sources. Before schema implementation, update the field-level ownership matrix in `docs/requirements/data-ownership.md` for the new scope and outcome fields and verify the ownership rules using `data-ownership-review`.

## Persistence and compatibility

Each run retains its existing lifecycle and additionally records scope kind (`workspace` or `project`) and, for a project run, the selected project identifier. Per-checkout outcomes retain the checkout identifier, status and reason. Project runs do not invoke whole-root absence reconciliation and cannot change unrelated checkout state. Index-wide freshness is computed only from workspace-scoped runs, including for existing status queries. A forward-only migration uses the existing backup and transaction policy, preserves existing rows, and interprets old runs as workspace-scoped. Existing clients and workspace scan behavior remain supported; no Sheets layout change is in scope.

## Traceability and verification

The selection and per-checkout response satisfy project-scoped selection and honest incomplete-observation requirements. Scope persistence and migration satisfy project scan history; the workspace-only freshness query satisfies index-wide freshness. Isolation of paths and field ownership satisfies preservation of unrelated data and repository content. Verify CLI responses and exit codes at the contract boundary; test migration, locking, freshness and reconciliation against disposable real SQLite databases; use isolated temporary workspace roots and repositories for integration tests.

## Open design details

The contract and UI transport require independent re-review before implementation.

## Capability discovery and precise validation

`vyasa query capabilities` is a read-only command independent of configuration and index. Its sole success response is `{"schema_version":"1","data":{"capabilities":{"project_scan":1}}}` and exit 0. Version 1 denotes this JSON operation and its fields; a caller must probe it before enabling project scanning. A missing command, malformed response, absent capability or unknown version is unsupported; the client disables the action without launching a scan. Existing `query version` retains its response and behavior.

The project identifier is an opaque nonempty string of at most 200 Unicode code points, copied from the indexed project query without interpreting its format. `checkout_id` is a positive integer; `run_id` is a nonempty opaque string. `--project` requires `--json`; a project request lacking `--json`, missing or malformed identifier, unknown argument, missing option value or simultaneous `--workspace` fails before index access with exit 2 and one stdout error object using `INVALID_INPUT`. A nonempty identifier not in the index returns `PROJECT_NOT_FOUND`, exit 2, and performs no scan. The existing human-readable scan behavior remains unchanged when `--project` is absent. Argument parsing for project requests must produce this structured error rather than argparse usage text.

Missing configuration returns `CONFIG_NOT_FOUND`; invalid configuration returns `CONFIG_INVALID`; both use exit 2 and the same stdout error envelope, without echoing untrusted configuration contents, and neither opens or creates the index. A missing index returns `INDEX_UNAVAILABLE` and exit 4. A held writer lock returns `OPERATION_IN_PROGRESS` and exit 3; other index or internal failures return their safe stable error code and exit 4. Pre-run errors have no `data` and no run identifier. Stderr is not a machine-readable contract and contains no repository contents or credentials.

An indexed project with no checkout produces a persisted project-scoped run with `status: "failed"`, `checkouts: []`, and exit 1. Runs with at least one completed and at least one failed checkout are `partial`; runs with no completed checkout are `failed`; all required checkouts completed is `completed`. Exit 1 alone therefore does not distinguish partial from failed: the desktop must parse and render the returned status and item outcomes, and reject malformed or inconsistent output instead of labeling every exit 1 partial.

Every pre-run error is exactly one stdout JSON object shaped `{ "error": { "code": "...", "message": "..." } }`: both members are strings, and `data` and `schema_version` are absent. Version 1 is the only supported project-scan response and capability version in this contract. Clients accept `schema_version` equal to string `"1"` and `project_scan` equal to integer `1`; any other or missing version is unsupported. A completed project run exits 0; partial and failed runs exit 1. A caller validates the response shape and consistency with the exit code before displaying the outcome.

MOVED is reserved for future evidence-backed behavior; this operation currently has no move-evidence source and reports a missing indexed path as MISSING.


`--json` without `--project` is rejected as `INVALID_INPUT` before any scan starts; the JSON error envelope and exit 2 apply.
