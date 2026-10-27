# File Composition Counts Grill

A review of change `be-file-composition-counts`, run with the `grill-me` skill. The author answered each question with a recommendation and a priority, testing claims against the real platform and the real workspace instead of reasoning from memory.

**How it was run.** A Windows junction was created and walked with `os.walk`; the walk rules were run over the 63 project folders under `E:\Python` (build and dependency directories excluded) at several depth and entry limits; the "documentation only" definition was tried in a loose and a strict form on the same folders; tooling (`python`, `pytest`) was checked; the change was validated with `openspec validate`. **What it was not.** No production code exists yet, so nothing here exercised the implementation; the workspace is one developer's, so the numbers are starting points, not guarantees.

**Status key.** *Fixed*: artifacts changed. *Verified*: checked and fine. *Recommended*: my answer, low risk. *Decision needed*: yours. **Priority:** P1 blocks implementation, P2 do during implementation, P3 later.

## Questions

**Q1. Is depth 6 right for counting?** (P1)

- **Finding:** No. Measured on 2026-10-27 over 63 projects: depth 6 leaves 30 partial (48%); depth 8 leaves 14; 10 leaves 4; 12 leaves 2; 16 leaves 0. The deepest natural depth is 13. The accepted depth of 6 serves discovery and parsing, not a name-only count.
- **Action:** Counting uses its own depth of 20. Knowledge decision, contract, design, and proposal updated. The package's earlier confirmation (Q4) said "depth and time unchanged", so the owner must confirm this.
- **Status:** Decision needed (recommended: depth 20)

**Q2. Was the reason for the 50,000-entry cap correct?** (P1)

- **Finding:** Not as written. The decision claimed most repositories exceed 5,000 entries. Measured: only 5 of 63 do, and the largest holds 14,315. A cap of 50,000 still gives about 3.5 times headroom and costs nothing, but the justification was overstated.
- **Action:** The decision's Context now cites the measurement instead of the claim. The cap stays at 50,000.
- **Status:** Fixed

**Q3. Does `followlinks=False` keep the walk inside the checkout on Windows?** (P1)

- **Finding:** No. A directory junction was walked and its file listed (`junc\secret.md`) although `followlinks=False`. `os.path.islink` is false for a junction; `os.path.isjunction` is true. Symlinks were creatable on this machine, so both can be tested for real.
- **Action:** The walk prunes every subdirectory for which `islink` or `isjunction` is true. New spec scenario "Junction escape"; the package scenario S8 is satisfied by it. The root itself is never pruned.
- **Status:** Fixed

**Q4. Are exclusions case-sensitive?** (P2)

- **Finding:** On Windows `Node_Modules` and `node_modules` are the same directory. A case-sensitive match would count dependency files.
- **Action:** Exclusion names compare by `casefold`. New scenario.
- **Status:** Fixed

**Q5. What if the checkout itself is named `build` or `dist`?** (P2)

- **Finding:** A predecessor skipped any path with an ignored name in any part, so a workspace under `build` was skipped entirely. Pruning only children of the root avoids it.
- **Action:** The root is never excluded by name. New scenario.
- **Status:** Fixed

**Q6. Is a partial result repeatable?** (P2)

- **Finding:** Not with `os.walk` order alone; which files are counted before a cap depends on directory order, so the same tree could give different partial counts. The spec's determinism scenario covered only complete counts.
- **Action:** Names are sorted at each level. New scenario "Partial counts are repeatable".
- **Status:** Fixed

**Q7. Can a reader interpret a partial count?** (P2)

- **Finding:** `stopped_by` names the bound but not its value, so "depth" alone does not say how deep the walk was allowed to go.
- **Action:** Evidence now includes the limits used.
- **Status:** Fixed

**Q8. What if an unreadable directory and a bound both occur?** (P3)

- **Finding:** `stopped_by` is one value. An unreadable directory does not stop the walk; a bound does.
- **Action:** `stopped_by` records the first cause observed, written into the contract.
- **Status:** Fixed

**Q9. Does "documentation only" mean anything on real projects?** (P1)

- **Finding:** Tested both forms over the 63 folders. The strict form (documentation exists, no code, no other files) matches 0 projects. The loose form (documentation exists, no code) matches 7, all plausible documentation or planning scaffolds, with 39% to 90% other files (configuration). A dataset repository with one README would also match the loose form.
- **Action:** Keep the loose form. All three counts are returned, so a consumer can judge the other share. No change to the spec.
- **Status:** Recommended

**Q10. Which default exclusions?** (P2)

- **Finding:** The tasks said "the default exclusion set" without defining it.
- **Action:** `DEFAULT_EXCLUSIONS` is exported and listed in the contract: `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `target`, `build`, `dist`. Workspace configuration (a later change) overrides it.
- **Status:** Fixed

**Q11. Packaging: a build backend is a dependency.** (P2)

- **Finding:** `pyproject.toml` with a source layout needs a build backend. Dependency policy says need before dependency. Setuptools ships with standard Python tooling and is build-time only; the runtime has none.
- **Action:** Setuptools backend, `pytest` with `pythonpath = src`, no runtime dependency. Recorded in the proposal and design.
- **Status:** Recommended

**Q12. Is the "one walk for languages and counts" scenario covered?** (P3)

- **Finding:** No. The language detector does not exist, so the package's Q6 scenario cannot be tested here. `walk_checkout` yields names and a stop reason, which a later detector can reuse.
- **Status:** Open (belongs to the change that adds the language detector)

**Q13. Does the platform have the tooling?** (P2)

- **Finding:** Python 3.12.10 and pytest 8.3.4 are present. The repository's commands say `python3`, which is not on this machine's path; `python` works.
- **Action:** Task 1.2 notes the difference.
- **Status:** Verified

## Outcome

Eight fixes (Q2–Q8, Q10), two verified or recommended with no change (Q9, Q11, Q13), one open for a later change (Q12), and one decision for you:

- **Q1 — counting depth.** Recommended: 20. Your earlier confirmation of the entry cap assumed depth 6; with depth 6, about half of real counts would be partial. If you agree, the file-composition package's Q4 text ("depth and time unchanged") and its Constraints line need the same edit; I have not changed the confirmed package.
