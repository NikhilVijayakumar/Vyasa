# Requirement: Workspace Discovery and Scan Reporting

- **Package:** `docs/requirements/workspace-discovery/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1
- **Owns:** FR-001, FR-002, FR-015, FR-022
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-001-configuration-and-workspace-roots.feature](features/fr-001-configuration-and-workspace-roots.feature), [fr-002-project-and-repository-discovery.feature](features/fr-002-project-and-repository-discovery.feature), [fr-015-error-handling-and-scan-reporting.feature](features/fr-015-error-handling-and-scan-reporting.feature), [fr-022-repository-ignore-file.feature](features/fr-022-repository-ignore-file.feature), [grill-additions.feature](features/grill-additions.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/architecture/scanning-and-evidence.md` — discovery rules (§4), inspection limits (§5), candidate outcomes (§4.6)
- `knowledge/architecture/system-architecture.md` — Configuration Manager and Workspace Discovery components
- `knowledge/architecture/c4-system-views.md` — shared container and component vocabulary
- `knowledge/concepts/evidence-and-provenance.md` — observation statuses used for inaccessible and unsupported sources
- `knowledge/decisions/repository-ignore-file.md` — the repository-provided ignore file
- `knowledge/decisions/repository-recognition-and-run-status.md` — outcomes, warnings, and run status

## Intent

A developer points Vyasa at one or more workspace roots. Vyasa finds the eligible projects reproducibly, stays inside the configured boundaries, and reports exactly what it did, including what it skipped or could not read, so a partial scan is never mistaken for a complete one.

## Scope

- **Included:**
  - Configuration of roots, exclusions, depth, symlink policy, and limits.
  - Candidate discovery, nested repositories, and per-candidate outcomes.
  - Scan reporting: partial results, run history, and redacted diagnostics.
- **Excluded:**
  - Metadata extraction (metadata-and-evidence).
  - Identity resolution (project-identity).
  - Index persistence and incremental reuse (local-index).
  - Remote repositories (remote-discovery).
- **Deferred:**
  - Filesystem watching for automatic refresh.
  - Project markers beyond the default list, until requested.

## Requirements

### FR-001 — Configuration and Workspace Roots (P1)

Vyasa MUST allow users to configure the local filesystem locations that it scans.

### FR-002 — Project and Repository Discovery (P1)

Vyasa MUST discover eligible local projects and Git repositories according to documented discovery rules.

### FR-015 — Error Handling and Scan Reporting (P1)

Vyasa MUST report scan and indexing outcomes in a way that makes failures and partial results distinguishable from successful complete operations.

### FR-022 — Repository-Provided Ignore File (P1)

Vyasa MUST skip the directories that a repository lists in its own `.vyasaignore` file, and MUST NOT let that file widen what is scanned.

- Patterns name directories: a bare name at any depth, or a path from the repository root, with `*`, `**`, and `?`.
- An ignored directory is not entered, is counted as excluded, and is not reported as a skip.
- Negation, drive letters, and `..` are invalid; an invalid line is reported in a warning and skipped, and the valid lines still apply.
- The file is bounded (64 KiB, 1,000 patterns); a larger file is skipped and reported.
- The patterns apply only below the repository holding the file; nested repositories have their own files and keep the enclosing ones.

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- Valid roots are scanned; invalid roots are reported and do not stop the others (`fr-001`).
- Only recognized candidates become projects; nested repositories stay separate (`fr-002`).
- Every scan ends with a status, counts, and a list of failed or skipped items (`fr-015`).
- A repository's `.vyasaignore` removes directories from scanning, can never add any, and its mistakes are reported (`fr-022`).

## Constraints

- Scan only configured roots; never follow a path out of them (SEC-011..018).
- Read-only access to repositories (NFR-016); no execution of repository content (NFR-020).
- Exclusions are applied before expensive inspection (NFR-007).
- Sequential, sorted traversal so reports are reproducible.

## Acceptance Expectations

- Phase 1 criteria 1, 2, 7, 8 and 12 in `phase-acceptance-criteria.md`.
- Fixture-tree tests cover every candidate outcome, including symlink escape and unreadable directories.
- Two consecutive scans of an unchanged tree report the same projects in the same order.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| DFR-003 | Non-Git directories qualify only with a recognized marker (profile or supported manifest), never bare. | Q3 |
| NFD-006 / SP-004 | Do not follow directory symlinks by default; opt-in resolves targets and rejects any outside the roots. | Q6 |
| SP-003 | Defaults: depth 8 (owner, 2026-10-27), 1 MiB per file, 5,000 inventory entries per project, 60 s per project. | Q14 |
| SP-005 | Keep the last 50 runs or 90 days, whichever is larger. | Q11 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-workspace-config`: load and validate configuration; report a not-configured state.
- `be-discover-one-root`: discover Git repositories in one root with outcomes and a run record.
- `be-discovery-boundaries`: exclusions, nesting, symlink policy, limits.
- `be-scan-reporting`: partial status, history, and redacted diagnostics.
