# Grill Log: Workspace Discovery and Scan Reporting

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 2 | 0 |
| Scope | 3 | 1 |
| Behaviour | 7 | 0 |
| Data | 2 | 1 |
| Integration | 2 | 0 |
| Architecture | 2 | 1 |
| Acceptance | 2 | 0 |
| Ambiguity | 2 | 0 |

## Intent

**Q1. Why scan instead of asking developers to register projects?**

- **Recommendation:** Scan. Registration drifts as soon as someone forgets; a scanner keeps the index true. Allow a recognized marker so a project can opt in explicitly.
- **Why:** Manual registries go stale, and staleness is the failure mode the whole product exists to remove.
- **Status:** Recommended
- **Feeds:** FR-002 scope

**Q2. Where does configuration live and who edits it?**

- **Recommendation:** One typed TOML file (stdlib `tomllib`), found via `--config`, `$VYASA_CONFIG`, then `<data dir>/config.toml`. No default roots are ever implied.
- **Why:** TOML needs no dependency, is human-editable, and an explicit file prevents scanning an unintended location.
- **Status:** Recommended
- **Feeds:** FR-001 S4, S5


## Scope

**Q3. Does a directory without Git count as a project (DFR-003)?**

- **Recommendation:** Yes. A directory is a project with a `.git` entry; or with a manifest (`pyproject.toml`, `requirements.txt`, `setup.py`, `package.json`, `Cargo.toml`, `go.mod`, or a `.uproject`), with Git optional and looked for in child folders (Unreal keeps it in `Source`). Source files, a README, or documentation alone are not enough: a documentation-only repository is tracked when it has Git and ignored otherwise.
- **Why:** Prevents noise (scratch folders, downloads) while covering Unreal projects and projects without version control, without tracking folders of notes. Owner decision 2026-10-27.
- **Status:** Settled
- **Feeds:** FR-002 S2, S4; DFR-003

**Q4. How are nested repositories, submodules, and worktrees treated?**

- **Recommendation:** A project is a boundary: Vyasa recognizes it and does not walk inside it, so nested projects and submodules are not found by default. A user who has them can enable nested repositories; then each is its own candidate and nothing is merged by directory nesting. A linked worktree is a sibling directory and is found normally.
- **Why:** Owner decision 2026-10-27: his projects in general contain no other project, and walking inside them produced hundreds of skips on a real workspace.
- **Status:** Settled
- **Feeds:** FR-002 S3

**Q5. What is traversed, how deep, and what is excluded by default?**

- **Recommendation:** Depth 8 below each root (owner decision 2026-10-27: his repositories sit at most 3 levels below a root). Default exclusions: `.git` internals, `node_modules`, `.venv`, `venv`, `__pycache__`, `build`, `dist`, `target`, `.tox`, caches, `.idea`, `.vscode`. Patterns match a directory name or a root-relative glob. Inside a project root the scanner descends only to find nested Git roots.
- **Why:** Bounds the work, keeps dependency trees out of the index, and makes matching rules testable.
- **Status:** Recommended
- **Feeds:** FR-001 S2; SE-001


## Behaviour

**Q6. What happens with symlinks (NFD-006, SP-004)?**

- **Recommendation:** Directory symlinks are not followed. With `follow_symlinks = true`, each target is resolved with `realpath`, rejected if it leaves the configured roots, and cycles are broken with a visited set of (device, inode).
- **Why:** Closes the main path-escape route by default while keeping an escape hatch for people who rely on links.
- **Status:** Settled
- **Feeds:** SEC-012, SEC-013

**Q7. What if some roots are missing and what if all are?**

- **Recommendation:** Missing roots are reported as inaccessible and the scan continues; the run ends `partial`. If no root is usable the run is `failed` with reason `not_configured` and nothing is scanned.
- **Why:** Matches FR-001 and gives `get_index_status` something truthful to say.
- **Status:** Recommended
- **Feeds:** FR-001 S3, S5

**Q8. What if two configured roots overlap, or one repository is reachable twice?**

- **Recommendation:** Roots are normalized with `realpath` and `normcase`. A root nested inside another configured root is dropped with a warning. Candidates are deduplicated by real path.
- **Why:** A gap in the current requirements: without it one repository is scanned twice and may produce duplicate checkouts.
- **Status:** Recommended
- **Feeds:** new scenario

**Q9. Which outcomes can a candidate have?**

- **Recommendation:** A closed set: eligible, excluded, not_recognized, inaccessible, malformed, skipped_by_policy, identity_unresolved. Each non-eligible outcome carries a reason code. Excluded paths are counted, not stored one by one.
- **Why:** A closed vocabulary makes reports comparable and tests exhaustive.
- **Status:** Settled
- **Feeds:** FR-015 S1


**Q15. How does a repository tell Vyasa what to skip inside it (FR-022)?**

- **Recommendation:** A plain `.vyasaignore` file at the repository root listing directories: a bare name at any depth, or a path from the root, with `*`, `**`, and `?`. It can only remove directories from scanning.
- **Why:** Vyasa cannot know which directories hold reference data or fixtures; the repository's owner does. On a real workspace 868 directories below the depth limit were such folders.
- **Status:** Settled
- **Feeds:** FR-022 S1–S6

**Q16. What stops the file from being used against Vyasa?**

- **Recommendation:** It is untrusted repository content. Negation, drive letters, and `..` are invalid and reported; the file is at most 64 KiB and 1,000 patterns; it affects only directories below its own repository; a mistake makes Vyasa scan more, never less than the repository asked.
- **Why:** The worst a hostile file can do is hide its own repository's directories.
- **Status:** Recommended
- **Feeds:** FR-022 S7–S9

**Q17. How do the files of nested repositories combine?**

- **Recommendation:** A nested repository has its own file, and the files of every enclosing repository still apply to it.
- **Why:** An outer repository's decision to ignore a directory must not be undone by an inner one.
- **Status:** Recommended
- **Feeds:** FR-022 S10, S11

## Data

**Q10. What does a scan run record?**

- **Recommendation:** Run id, scope, start and end, status, counts per outcome, tool and detector versions, and a bounded list of failed or skipped items with reason codes. Absolute paths stay in the local index only.
- **Why:** Enough to explain any scan afterwards without keeping repository content.
- **Status:** Settled
- **Feeds:** FR-015 S4

**Q11. How long is scan history kept (SP-005)?**

- **Recommendation:** The last 50 runs or 90 days, whichever is larger, both configurable; per-item detail for the last 10 runs.
- **Why:** History is diagnostic, not archival. Bounded retention keeps the database small.
- **Status:** Decision needed
- **Feeds:** FR-015 S4; SP-005


## Integration

**Q12. Does discovery ever touch the network?**

- **Recommendation:** No. Remotes are read from `.git/config`; discovery never fetches or pulls.
- **Why:** Phase 1 must work offline and must not change repository state.
- **Status:** Settled
- **Feeds:** NFR-011, NFR-016

**Q13. How is Git metadata read without executing repository-controlled code?**

- **Recommendation:** Parse `.git/config` and `HEAD` directly. A closed set of read-only plumbing commands (defined in the project-identity grill log, local-fallback question) may run with a sanitized environment and `-c core.fsmonitor=false`, a timeout, and no hooks.
- **Why:** Running Git inside an untrusted repository can execute commands named in its config; parsing files avoids that surface.
- **Status:** Recommended
- **Feeds:** SEC-016; NFR-020


## Architecture

**Q14. Where do limits live and what happens when one is hit (SP-003)?**

- **Recommendation:** Configuration holds `max_depth` (8), `max_file_bytes` (1 MiB; 256 KiB for profiles), `max_inventory_entries` (5,000), and `project_timeout` (60 s). Hitting a limit gives `skipped_by_policy` naming the limit, never a claim that the thing is absent.
- **Why:** Conservative defaults validated by benchmarks later; the rule that a limit is not absence is already in the architecture.
- **Status:** Decision needed
- **Feeds:** NFR-007; SEC-015

**Q15. Sequential or parallel scanning?**

- **Recommendation:** Sequential in version 1, with paths visited in sorted order. Parallel inspection can be added behind the same interface once benchmarks justify it.
- **Why:** Deterministic reports need a deterministic order; parallelism is an optimization to earn, not assume.
- **Status:** Recommended
- **Feeds:** FR-002 S6


## Acceptance

**Q16. How do we prove discovery is reproducible and safe?**

- **Recommendation:** `tmp_path` fixture trees for each outcome; scan twice and compare project set and order; a symlink-escape fixture; a permission-denied fixture (skipped on Windows); a before/after hash of the whole tree to prove nothing was written.
- **Why:** Each risk gets a cheap automated check, per the verification layers in `test-strategy`.
- **Status:** Recommended
- **Feeds:** Phase 1 criteria 1, 2, 7

**Q17. What exactly do completed, partial, and failed mean?**

- **Recommendation:** The knowledge bundle's run vocabulary: `pending`, `running`, `completed` (every candidate inspected; skips allowed by policy are counted and listed, not a separate status), `partial` (at least one inaccessible or failed item or root), `failed` (nothing usable), `cancelled` (stopped by the user), `interrupted` (the process stopped mid-run).
- **Why:** FR-015 requires partial results to be distinguishable; a fixed enum is the testable form.
- **Status:** Recommended
- **Feeds:** FR-015 S1


## Ambiguity

**Q18. Is a run recorded when configuration is invalid and nothing is scanned?**

- **Recommendation:** Yes: a `failed` run with reason `not_configured`, so `get_index_status` can explain why the index is empty or stale.
- **Why:** An empty index with no explanation looks the same as a broken one.
- **Status:** Recommended
- **Feeds:** FR-001 S5

**Q19. Can an interrupted scan resume?**

- **Recommendation:** No resume in version 1. The run is marked `interrupted`; per-project work already committed stays; the next scan starts fresh and reuses unchanged results.
- **Why:** Resume adds state that must itself be recovered; incremental reuse already gives most of the benefit.
- **Status:** Settled
- **Feeds:** FR-008 S5

## Decisions for you

- **Q11** — How long is scan history kept (SP-005)?
- **Q14** — Where do limits live and what happens when one is hit (SP-003)?
