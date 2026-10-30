# Proposal

## Why

People need to refresh one indexed project after an external analysis without scanning all configured workspaces.

## What Changes

Introduce a backend-owned project-scoped scan selected by project identifier, with an explicit scope in persisted scan history. Expose the operation in the desktop project detail view after confirmation.

## Scope and constraints

Only indexed checkouts of the requested project within currently configured roots are eligible. A project may have multiple checkouts and each outcome must be reported. A missing, inaccessible, moved, or identity-conflicting checkout must not be treated as a successful complete observation. Scanning cannot mark unrelated checkouts missing or execute repository content. Project-scoped runs cannot refresh the index-wide freshness indicator.

Existing index data must migrate safely, with old runs interpreted as workspace-scoped. Desktop clients use the backend CLI; no renderer database access or embedded terminal is introduced. The operation must return explicit failure and partial results.

## Knowledge References

- `knowledge/architecture/data-model/relationships-and-runs.md` — scan scope and per-item outcomes.
- `knowledge/architecture/scanning-and-evidence/incremental-and-partial.md` — incomplete scope and absence.
- `knowledge/concepts/field-ownership.md` — preserve human and repository-owned data.

## Traceability

Change `be-project-scan`, branch `feature/be-project-scan`; workspace discovery and local-index requirements; desktop `phase1-vyasa-desktop` task 4.6.
