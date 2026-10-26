---
name: openspec-git-discipline
description: >-
  Enforces the repository's Git Flow: develop created from master, feature and
  fix branches from develop merged back to develop, releases merged from
  develop to master and tagged, hotfixes from master merged back to master and
  tagged; plus change-ID traceability, review gates, and archive timing. Use
  when creating branches, committing, merging, releasing, tagging, handling a
  production hotfix, or archiving a change.
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

## Flows

### Feature or fix

1. `git switch develop && git pull --ff-only`
2. `git switch -c feature/<change-id>-<desc>` (or `fix/…`)
3. Implement and commit (`git-commit`).
4. When implementation, review, and verification are complete:
   `git switch develop && git merge --no-ff feature/<change-id>-<desc>`
5. Delete the working branch once merged.

### Release

1. Confirm `develop` is verified (tests, `verify_workflows.py`, phase gate
   when applicable).
2. `git switch master && git pull --ff-only`
3. `git merge --no-ff develop -m "Release vX.Y.Z"`
4. `git tag -a vX.Y.Z -m "Release vX.Y.Z"` on that merge commit.
5. Push `master` and the tag only when the user asks:
   `git push origin master vX.Y.Z`.

### Hotfix

1. `git switch master && git pull --ff-only`
2. `git switch -c hotfix/<change-id>-<desc>`
3. Fix with a regression test; commit.
4. `git switch master && git merge --no-ff hotfix/<change-id>-<desc>`
5. Tag the patch release: `git tag -a vX.Y.(Z+1) -m "Hotfix vX.Y.(Z+1)"`.
6. Bring the fix into integration: `git switch develop && git merge --no-ff master`,
   so the next release does not regress it.
7. Delete the hotfix branch.

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
- Push, release, and tag only when the user asks.
- Respect protected-branch settings; never bypass required review.

## Archive timing

Archive the OpenSpec change only after its branch is merged into `develop`
and verification is complete.
