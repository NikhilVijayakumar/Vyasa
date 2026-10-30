# Design: be-project-scan

## Scope and boundaries

The CLI adapter parses a project identifier, selects the existing configuration and emits the JSON contract. The application service resolves the indexed project's checkout IDs and paths, checks them against configured roots and orchestrates bounded inspection. Filesystem adapters classify and inspect each selected checkout using existing discovery and detector rules; SQLite adapters persist runs, per-item outcomes and observations. No renderer database access, repository execution, network operation, or whole-root discovery is needed.

## Flow and failure handling

Validate options, configuration, existing index and project identifier before scanning. Acquire the existing writer lock before recording a run or updating observations. Record a project-scoped running run; for each indexed checkout, first check its canonical path is within a currently configured root without traversing links or junctions outside it. A checkout outside the configured scope is reported, never inspected. Inspect only the selected path with existing recognition, profile, report and detector logic. Compare evidence of identity with the existing project's identity before storing: conflicts are failures, never an attachment to another project. Preserve existing data on incomplete inspections. Each checkout receives a persisted terminal result, and failures do not suppress inspection of other eligible checkouts. Release the lock on every exit; interrupted work retains a non-success run state.

An absent recorded path is missing; do not infer its new location from absence, search a root, or report a move without evidence. When a move is established by reliable existing evidence, report it, not success. Inaccessible paths, malformed repository evidence, detection failures and conflicts similarly do not prove successful observation. Results and diagnostics use fixed safe codes. A project with no successfully observed required checkout fails; a mix of success and failure is partial; all required checkouts completing yields completed. Out-of-root indexed checkouts are non-success outcomes.

Reuse per-checkout transaction and locking policies; do not call root-wide `mark_absent` for this path. Ensure duplicate reconciliation cannot modify unrelated projects. Preserve repository- and portfolio-owned values, and never write files in the checkout.

## Storage and freshness

Add a forward-only SQLite migration to extend scan runs with a constrained scope kind defaulting to workspace and nullable project identifier (required for project scope). Add a per-run checkout outcome table with foreign keys, status and safe reason; enforce one outcome per run/checkout. Preserve old runs and all existing data through the existing backup and migration transaction mechanism. Update both `application/indexing/store.py` freshness and `application/query.py` latest-run selection to consider only workspace runs; project scan results remain available through their own operation/history. Verify existing workspace behavior remains intact.

## Verification and sequencing

First complete the data ownership matrix and independent review of this design and the interface with the UI consumer. Implement test-first: migrations and legacy data, scope-aware freshness and no unrelated reconciliation; checkout selection, path containment and identity handling; per-item errors and lock lifecycle; CLI contract and exit codes. Use disposable real SQLite files and temporary isolated roots; no shared index or existing workspace is scan-test input. Verify absence of repository modification, no execution of repository content, and preservation of human fields. Run backend project verification using its virtual environment and record actual outcomes. Validate CLI transport together with UI after backend integration.

## Architecture decision checkpoint

A new draft ADR is warranted for the storage and desktop contract boundary; see `knowledge/decisions/project-scoped-scan-freshness.md`. Persisted scope and per-item outcomes follow existing `knowledge/architecture/data-model/relationships-and-runs.md` and partial-observation semantics follow `knowledge/architecture/scanning-and-evidence/incremental-and-partial.md`. Field ownership follows `knowledge/concepts/field-ownership.md`. The implementation approach reuses the existing scanner and index rather than introducing a new architecture.

## Risks and review

Path containment must account for symlinks and junctions and must be checked at inspection time; tests must prove paths escaping a configured root are not read. A missing path alone cannot establish a move; incomplete inspection cannot be treated as success. Path-based provisional identity remains valid under existing identity rules. Review remains required; this document is a draft and is not evidence of implementation or test completion.

## Reconciliation with existing identity and storage rules

Identity matching follows `openspec/specs/project-identity/spec.md` and `knowledge/decisions/stored-identity-with-aliases.md`: a known checkout path is sufficient for a provisional remote-less project. A newly observed remote at that path becomes an alias when unclaimed; a removed remote preserves existing aliases and identity; a remote alias owned by a different project conflicts with the path's project and is not merged or moved. Unknown evidence alone does not create an identity conflict. These rules do not make an unreadable or otherwise incomplete checkout a successful observation. A missing path is reported missing; because a targeted scan does not discover elsewhere, a move is not inferred or searched for. Existing separately established move evidence may be reported as moved but cannot by itself complete the old checkout observation.

The migration changes `scan_runs.root` to nullable: workspace runs require a nonempty root and null project ID; project runs require a null root and a nonempty project ID. Add `scope_kind`, defaulting old rows to `workspace`, and `scope_project_id`; constrain valid combinations. This requires a table rebuild that preserves run IDs and all referencing foreign keys. Use the existing backup and transactional migration framework, validate foreign keys after migration and test rollback on failure, including existing dependent rows. Checkout outcomes retain checkout IDs, whose index records carry the actual root, so a project can span multiple configured roots. Legacy rows retain their original roots.

The desktop transport must probe `query capabilities` before offering the action and parse the project scan JSON for exit 1: `failed` and `partial` are distinct. Existing generic scan handling that maps every exit 1 to partial is not sufficient for this operation. Add consumer contract tests against version 1 and unsupported/malformed capability responses before integration.

## Migration runner compatibility

The current runner enables foreign keys before wrapping migration SQL in `BEGIN` and `COMMIT`. With referenced `scan_runs` rows, SQLite rejects dropping and rebuilding the parent even with deferred foreign keys. The migration must use a narrowly identified rebuild path: disable foreign-key enforcement on that connection before beginning the migration transaction; copy and replace the parent while keeping its name and IDs; execute `foreign_key_check` before committing and roll back if any violation exists; restore enforcement in a finally path on success or failure. Preserve the existing backup, per-migration atomicity, version-update and controlled-error behavior. Do not globally disable checks for unrelated migrations. Test enforcement restoration and rollback on deliberately invalid references and migration failure, with an existing child reference in a disposable file database. The required mechanism must be independently reviewed before implementation.

The current selected-checkout operation has no established source of move evidence and never emits MOVED; a missing indexed path is MISSING. MOVED remains reserved for a future evidence-backed operation, without searching other roots or claiming relocation now.
