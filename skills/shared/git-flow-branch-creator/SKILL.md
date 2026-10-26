---
name: git-flow-branch-creator
description: >-
  Creates the right working branch for this repository's Git Flow: feature or
  fix from develop, hotfix from master, creating develop from master first if
  it is missing. Use when starting any work that will be committed.
metadata:
  scope: shared
---

# Git Flow Branch Creator

Mechanics for the policy in `openspec-git-discipline`. Branch types and their
bases are fixed there; this skill picks the type and creates the branch.

## Steps

1. **Check state.** `git status`. Uncommitted changes that belong to the new
   work move with the switch; anything unrelated must be committed or stashed
   by the user first.
2. **Ensure `develop` exists.** If `git rev-parse --verify develop` fails:
   ```bash
   git switch master && git pull --ff-only
   git switch -c develop
   ```
   Tell the user `develop` was created; push it only when they ask.
3. **Choose the type:**
   - Production is broken and the fix must ship from `master` → `hotfix`.
   - Corrects a defect not yet released (on `develop`) → `fix`.
   - Anything else: new behaviour, enhancement, refactor, docs, framework or
     process change → `feature`.
   If both feature and fix work are mixed, split into separate branches.
4. **Name it** `<type>/<change-id>-<short-description>`, lowercase kebab-case.
   Use the OpenSpec change ID (`be-…` for product, `openspec-…` for framework
   and process). If no change exists yet, use a short descriptive slug and
   rename once the change ID is allocated.
5. **Create from the correct base:**
   ```bash
   # feature / fix
   git switch develop && git pull --ff-only
   git switch -c feature/<change-id>-<desc>

   # hotfix
   git switch master && git pull --ff-only
   git switch -c hotfix/<change-id>-<desc>
   ```
   Skip `git pull` when the repository has no remote or the user is offline.
6. **Report** the branch, its base, and where it will merge
   (`feature`/`fix` → `develop`; `hotfix` → `master`, tagged, then `master`
   merged into `develop`).

## Edge cases

- **Already on a matching working branch** — continue on it; do not nest.
- **Name exists** — reuse it if it is the same work, otherwise add a suffix.
- **On `master` or `develop` with uncommitted work** — create the working
  branch now; the changes move with `git switch -c`.
