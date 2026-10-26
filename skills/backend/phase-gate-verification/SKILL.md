---
name: phase-gate-verification
description: >-
  Verifies a Vyasa roadmap phase is complete: every acceptance criterion
  backed by an executed check, no later-phase dependencies leaked in, and
  unverified items reported explicitly. Use before declaring phase 1, 2, or 3
  complete, or before tagging a release.
---

# Phase Gate Verification

Sources of truth: `docs/requirements/phase-acceptance-criteria.md` (acceptance
criteria per phase) and `knowledge/product/scope-and-roadmap.md` (phase 1 §4,
phase 2 §5, phase 3 §6: In Scope, Out of Scope, Deliverables).

## Procedure

1. **Build the matrix.** One row per acceptance criterion and deliverable of
   the phase: criterion, requirement IDs from `docs/requirements/`, the
   check that proves it (test ID, command, or manual step), and its result.
2. **Run the checks.** Execute the test suite and every listed command now.
   A result counts only if it was observed in this run; quote the command
   and the decisive output line.
3. **Classify every row:** `verified`, `failed`, `not run`, `unverifiable`
   (no check exists). Never fold `not run` into `verified`.
4. **Leak check.** The phase must not depend on out-of-scope work. For
   phase 1: no Google Sheets client, no provider API client, and no network
   access in the import graph or test run. For phase 2: no provider discovery.
   Grep imports and dependency manifests; list any hit.
5. **Cross-cutting checks.**
   - Security: `code-review-security`, `secrets-scan`, `sca-audit`, and
     `mcp-server-review` run on the phase's code.
   - Migrations: the SQLite schema migrates from the previous release and from
     empty (`database-integration-testing`).
   - Failure behavior: inaccessible roots, malformed manifests, locked
     index, and missing credentials produce documented statuses or errors.
   - Documentation: `neat-freak` reconciles `docs/` with what was built.
6. **Verdict.** The phase is complete only when every row is `verified`, or
   each remaining row has an explicit, accepted exception.

## Output

The matrix, the leak-check result, the cross-cutting results, and a one-line
verdict. List `failed`, `not run`, and `unverifiable` rows first.
