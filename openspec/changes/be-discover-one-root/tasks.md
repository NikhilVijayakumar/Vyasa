# Implementation Tasks: be-discover-one-root

- **OpenSpec Change ID:** `be-discover-one-root`
- **Status:** Implemented, pending review and merge
- **Related artifacts:** `proposal.md`, `specs/`, `design.md`, `api-contract.md`, `adr.md`

> Order of work, by owner instruction 2026-10-27: implement first, then write repository tests that anyone can re-run.

> Amended 2026-10-27 on owner instruction after the first merge: projects are also recognized by manifest (`pyproject.toml`, `package.json`, `Cargo.toml`, `.uproject`, ...); a documentation-only folder counts only if it has Git; Git is optional and looked for in child folders; a project is a boundary not entered unless nested repositories are enabled; skips are warnings; default depth 8. Implemented in `repository_walk.py` with added tests (210 total).

## 1. Preparation and Baseline

- [x] 1.1 Review the proposal, spec, contract, design, and ADR.
- [x] 1.2 Record the baseline: `python -m pytest` and `python scripts/verify_knowledge.py`.
- [x] 1.3 Confirm branch `feature/be-discover-one-root`.

## 2. Prerequisite: shared helpers

**Prerequisite, not a slice:** behavior-preserving refactors; the existing tests must stay green.

- [x] 2.1 Extract `prune` into `vyasa.adapters.filesystem.pruning` and use it in `checkout_walk`.
- [x] 2.2 Expose `check_root(path)` from `vyasa.application.configuration.workspace` and use it in `check_roots`.

## 3. Implementation Slice: find repositories

**Traceability:** Requirements: Recognize Git repositories; Nested repositories stay separate · Knowledge: `knowledge/decisions/repository-recognition-and-run-status.md`

- [x] 3.1 Implement `vyasa.domain.discovery`, `repository_walk`, and `discover_repositories` for eligible repositories with kinds.
- [x] 3.2 Tests: Git directory, root repository, submodule, worktree, elsewhere, ordinary directories, nested.

## 4. Implementation Slice: outcomes and issues

**Traceability:** Requirement: Every candidate has one closed outcome

- [x] 4.1 Implement malformed, inaccessible, and skipped outcomes with reason codes.
- [x] 4.2 Tests: missing HEAD, invalid and unreadable `.git` file, unreadable directory.

## 5. Implementation Slice: boundaries

**Traceability:** Requirement: Traversal boundaries · Knowledge: `knowledge/decisions/scan-limits-and-symlink-defaults.md`

- [x] 5.1 Implement depth, exclusions with counts, and link handling.
- [x] 5.2 Tests: depth limit and boundary, exclusions, `.git` not counted, symlink, junction (Windows), `.git` link.

## 6. Implementation Slice: status and record

**Traceability:** Requirements: Run status; Run record; Nothing is executed or read beyond pointers

- [x] 6.1 Implement status, counts, bounded issues, and the record.
- [x] 6.2 Tests: complete, partial, failed (three root cases), record contents, bounded issues, repeatable, listing order, only pointer files opened.

## 7. Final Verification

- [x] 7.1 `python -m pytest`
- [ ] 7.2 `python scripts/verify_workflows.py` and `python scripts/verify_knowledge.py` — knowledge passes; workflows has 1 failure, the skill-reference check, which predates this change
- [x] 7.3 `openspec validate be-discover-one-root`
- [x] 7.4 Each spec scenario has a test (124 tests pass in total; none skipped on Windows; the junction test skips off Windows by design; not yet run on Linux).
- [ ] 7.5 Review the diff for scope and the contract.

## 8. Documentation and Handover

- [ ] 8.1 Update the knowledge decision if behavior diverged; add a dated entry to `knowledge/log.md`.
- [ ] 8.2 Mark the decision concept accepted when the owner accepts it.

## 9. Review, Merge, and Archive

- [ ] 9.1 Pull request with the change ID.
- [ ] 9.2 `git fetch`, merge into `develop` after review and verification (never force-push).
- [ ] 9.3 Archive the change.
