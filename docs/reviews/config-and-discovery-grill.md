# Workspace Configuration and Discovery Grill

A review of changes `be-workspace-config` and `be-discover-one-root`, run with the `grill-me` skill. Each question was answered with a recommendation and a priority. Claims were tested by running the new discovery against the real `E:\Python` workspace and by adding repository tests that fail before the fix and pass after it.

**How it was run.** `discover_repositories` was run over `E:\Python` (63 project folders). Ten new tests were added to the repository; the five that exposed defects were seen failing first. `openspec validate` and `verify_knowledge.py` were run on the result. **What it was not.** Nothing was run on Linux; no workspace other than this one was tried; the walk has no entry or time bound, so a very large root was not tested.

**Status key.** *Fixed*: code or artifacts changed and tested. *Verified*: checked and fine. *Recommended*: my answer, low risk. *Decision needed*: yours. *Open*: not done, with a reason. **Priority:** P1 blocks the next change, P2 do soon, P3 later.

## Discovery

**Q1. Does it work on a real workspace?** (P1)

- **Finding:** Yes. 65 repositories (62 plain, 2 linked worktrees, 1 submodule) in 1.3 seconds; all 61 top-level folders with a `.git` were found and none missed. 682 excluded directories were counted, none listed.
- **Status:** Verified

**Q2. Can the bounded issue list hide a real problem?** (P1)

- **Finding:** Yes. 3,132 directories inside repositories were skipped at the depth limit, so the first 100 listed issues were all `max_depth`. A malformed or unreadable repository found later in the walk would have been counted but not listed.
- **Action:** Inaccessible and malformed candidates are listed before policy skips. Two tests failed before the fix. Spec, contract, and decision updated.
- **Status:** Fixed

**Q3. Is recognizing a submodule or worktree by a path segment safe?** (P1)

- **Finding:** No. A pointer to `/home/me/modules/repo.git` was labelled a submodule, and `/home/me/worktrees/repo.git` was ambiguous with a real bare-repository worktree. Git's real shapes are `<git dir>/worktrees/<name>` and `<super>/.git/modules/<name>`.
- **Action:** A worktree needs `worktrees/<name>` under a path that ends in `.git`; a submodule needs `.git` followed by `modules`. Tests for look-alikes, a bare-repository worktree, and a nested submodule were added. On the real workspace the kinds are unchanged (62, 2, 1).
- **Status:** Fixed

**Q4. What if the root itself is a symlink?** (P2)

- **Finding:** The root is never pruned, so it is searched. A test now proves it.
- **Status:** Verified

**Q5. Should a policy skip make a run partial?** (P1)

- **Finding:** On the real workspace the status is `partial` and always will be: 3,132 skips, all `max_depth`, none a failure. A status that is always partial carries no information, and a person would stop reading it. Failures (`inaccessible`, `malformed`) are what a person must act on.
- **Recommendation:** `partial` only when something failed (inaccessible or malformed). Policy skips stay in the counts and the list, and the record says the run is `complete` within its limits. Update the spec scenarios "Depth limit" and "Directory link not followed" and the decision to match.
- **Owner decision 2026-10-27:** a policy skip does not make the run partial. The user is informed with a warning, per reason, with advice, and decides whether to add an ignore entry to the repository or fix the cause. Implemented: warnings aggregate skips and never change the status; the default depth is now 8 (his repositories sit at most 3 levels below a root).
- **Status:** Fixed

**Q6. Is an unbounded walk acceptable?** (P2)

- **Finding:** Depth 6 and the exclusions kept the real run to 1.3 seconds, but a root such as a whole drive has no entry or time bound.
- **Action:** Limits belong to `be-discovery-boundaries`; recorded as a risk in the proposal.
- **Status:** Open

## Configuration

**Q7. Does a file saved by a Windows editor load?** (P1)

- **Finding:** No. A file starting with a UTF-8 byte-order mark failed to parse. Older Windows editors add one.
- **Action:** The file is read as UTF-8 with a tolerated byte-order mark. Test failed first, passes now.
- **Status:** Fixed

**Q8. Windows line endings, single-quoted paths, and variables in paths?** (P2)

- **Finding:** CRLF files and single-quoted literal paths with backslashes load. `$HOME/work` is rejected as not absolute, so nothing is expanded silently. Tests added; the README's backslash advice is now backed by a test.
- **Status:** Verified

**Q9. Are duplicate roots detected through symlinks?** (P3)

- **Finding:** No. Roots are normalized textually; the workspace-discovery package says to use the real path. A symlinked duplicate would be scanned twice.
- **Action:** Deduplication by real path belongs to the change that runs several roots together.
- **Status:** Open

**Q10. A relative `VYASA_HOME`?** (P3)

- **Finding:** It is used as given, so it resolves against the current directory. That is surprising for a data directory.
- **Recommendation:** Document it; reject relative values when the multi-root change arrives.
- **Status:** Recommended

**Q11. Keep or drop a root nested inside another?** (P2)

- **Finding:** The configuration keeps both and warns. The workspace-discovery package (Q8) recommends dropping the inner one with a warning. It does not matter for a single root, but it does when several run together.
- **Owner decision 2026-10-27:** drop the inner root with a warning. Implemented in the configuration loader; the outer root wins whatever the order.
- **Status:** Fixed

## Outcome

Five defects fixed with failing tests first (Q2, Q3, Q7, and the two pointer look-alikes), three questions verified (Q1, Q4, Q8), and both decisions were taken by the owner and implemented:

- **Q5 — partial status.** Only failures make a run partial; skips are warnings with advice.
- **Q11 — nested roots.** The inner root is dropped with a warning.

The default discovery depth is 8. Test count: 136 passing, none skipped on Windows.
