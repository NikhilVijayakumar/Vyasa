---
name: openspec-git-discipline
description: >-
  Enforces the shared branch naming, change-ID traceability, review and
  verification gates, merge and hotfix reconciliation, and archive timing for
  OpenSpec changes. Use when creating branches, committing, opening or merging
  pull requests, handling hotfixes, or archiving a change.
metadata:
  scope: shared
---

# OpenSpec Git Discipline

Shared policy for how OpenSpec changes move through version control. This is the
policy layer; the mechanics live in `git-flow-branch-creator` (branching),
`git-commit` (commits), and `git-guardrails-claude-code` (destructive-command
safety). Apply this policy through those skills rather than restating them.

## Branching

- `main` — release branch.
- `develop` — integration branch.
- `feature/<change-id>-<short-description>` — new functionality.
- `fix/<change-id>-<short-description>` — bug fixes.

Feature and fix branches originate from `develop` and merge back into `develop`
after review and verification. Releases are promoted from `develop` to `main`
through the repository's release process.

## Change-ID traceability

The OpenSpec change ID must be consistent and findable across:

- the change directory under `openspec/changes/<change-id>/`;
- the branch name;
- the pull request title and body;
- the relevant commits;
- the verification report.

A change that cannot be traced from branch to archive is incomplete.

## Gates

- Do not merge to `develop` until review and verification have passed.
- Do not commit directly to protected branches (`main`, `develop`).
- Respect the consuming repository's protected-branch settings and review
  policy; never bypass required review or branch protection.

## Hotfixes

Production hotfixes may originate from `main`. After release, reconcile the
hotfix back into `develop` so the fix is not lost on the next promotion.

## Archive timing

Archive the OpenSpec change only after it is integrated according to this policy
and verification is complete. Do not archive a change that is still open,
unmerged, or unverified.
