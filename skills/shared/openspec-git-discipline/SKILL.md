---
name: openspec-git-discipline
description: >-
  Enforces the repository's Git Flow: develop created from master, feature and
  fix branches from develop merged back to develop, releases merged from
  develop to master and tagged, hotfixes from master merged back to master and
  tagged; always pull and check remote changes before committing, then push;
  plus change-ID traceability, review gates, and archive timing. Use when
  creating branches, committing, pushing, merging, releasing, tagging,
  handling a production hotfix, or archiving a change.
metadata:
  scope: shared
---

# OpenSpec Git Discipline

The policy for how work moves through Git. Mechanics live in
`git-flow-branch-creator` (creating branches), `git-commit` (commits), and
`git-guardrails-claude-code` (destructive-command safety).

## Long-lived branches

| Branch | Role | Created from | Receives merges from |
|---|---|---|---|
| `master` | Production. Every merge is a release and is tagged. | — | `develop` (release), `hotfix/*` |
| `develop` | Integration. All development lands here first. | `master` | `feature/*`, `fix/*`, `master` (after a hotfix) |

If `develop` does not exist, create it from `master` before any other work:

```bash
git switch master && git pull --ff-only
git switch -c develop && git push -u origin develop
```

Never commit directly to `master` or `develop`; they change only through
merges.

## Working branches

| Type | Use for | Branch from | Merge into | Name |
|---|---|---|---|---|
| `feature` | New behaviour, enhancements, process/framework changes | `develop` | `develop` | `feature/<change-id>-<short-description>` |
| `fix` | A defect found before release (on `develop`) | `develop` | `develop` | `fix/<change-id>-<short-description>` |
| `hotfix` | A defect in production (on `master`) | `master` | `master` | `hotfix/<change-id>-<short-description>` |

There are no release branches: a release is a merge of `develop` into
`master`.

## Sync, commit, push

Every commit — and every merge into `develop` or `master` — goes through
this sequence. Never commit on a stale branch.

1. **Fetch:** `git fetch origin --prune`.
2. **Check for remote changes** and report them before going on:
   ```bash
   git log --oneline HEAD..@{u}            # new commits on this branch's remote
   git log --oneline HEAD..origin/<base>   # new commits on the base: develop (feature/fix) or master (hotfix)
   ```
   Skip a line whose ref does not exist (branch never pushed, no remote).
3. **Pull everything in:**
   ```bash
   git pull --rebase --autostash           # this branch's own remote commits, if it has an upstream
   git merge --no-ff origin/<base>         # only when the base has new commits
   ```
   On a conflict, stop: show the conflicting files and resolve them with the
   user. Never commit or push over an unresolved pull.
4. **Verify and commit** with `git-commit` once the branch contains all
   remote changes and the relevant checks pass.
5. **Push:** `git push -u origin <branch>`. Never force-push.

For a merge into a long-lived branch: `git switch <target> && git pull --ff-only`,
then merge, then `git push origin <target>`.

## Flows

### Feature or fix

1. `git switch develop && git pull --ff-only`
2. `git switch -c feature/<change-id>-<desc>` (or `fix/…`)
3. Implement; commit and push through **Sync, commit, push**.
4. When implementation, review, and verification are complete:
   ```bash
   git switch develop && git pull --ff-only
   git merge --no-ff feature/<change-id>-<desc>
   git push origin develop
   ```
5. Delete the local working branch; delete the remote branch when the user
   asks (or when the pull request is merged).

### Release

1. Confirm `develop` is verified (tests, `verify_workflows.py`, phase gate
   when applicable).
2. `git switch master && git pull --ff-only`
3. `git fetch origin` and confirm `develop` has nothing unpulled
   (`git log --oneline develop..origin/develop` is empty).
4. `git merge --no-ff develop -m "Release vX.Y.Z"`
5. `git tag -a vX.Y.Z -m "Release vX.Y.Z"` on that merge commit.
6. `git push origin master vX.Y.Z`.

### Hotfix

1. `git switch master && git pull --ff-only`
2. `git switch -c hotfix/<change-id>-<desc>`
3. Fix with a regression test; commit and push through **Sync, commit, push**.
4. `git switch master && git pull --ff-only && git merge --no-ff hotfix/<change-id>-<desc>`
5. Tag the patch release: `git tag -a vX.Y.(Z+1) -m "Hotfix vX.Y.(Z+1)"`;
   `git push origin master vX.Y.(Z+1)`.
6. Bring the fix into integration so the next release does not regress it:
   `git switch develop && git pull --ff-only && git merge --no-ff master && git push origin develop`.
7. Delete the local hotfix branch.

## Tags

- Annotated, semantic: `vMAJOR.MINOR.PATCH`, only on `master` merge commits.
- Release from `develop` bumps MAJOR or MINOR; a hotfix bumps PATCH.
- Never move or delete a pushed tag.

## Change-ID traceability

The OpenSpec change ID must be consistent across the change directory
(`openspec/changes/<change-id>/`), the branch name, the pull request, the
relevant commits, and the verification report. Product changes use `be-`;
framework and process changes use `openspec-`.

## Gates

- Merge into `develop` only after review and verification pass.
- Merge into `master` only as a release (from `develop`) or a hotfix.
- Pull before every commit and merge; push after every commit and merge.
- Release (develop → master) and tagging happen only when the user asks;
  a hotfix is released as soon as it is merged into `master`.
- Never force-push, and never push over an unresolved pull or conflict.
- Respect protected-branch settings; never bypass required review.

## Archive timing

Archive the OpenSpec change only after its branch is merged into `develop`
and verification is complete.
