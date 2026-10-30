# Proposal

## Why

Desktop users need to browse projects within one configured workspace and explicitly scan that workspace. The existing CLI only searches the entire index and scans every root.

## What Changes

Add a local CLI contract for listing configured roots, filtering indexed searches by one configured root, and scanning one configured root. Keep queries read-only and preserve whole-root reconciliation semantics.

## Scope

Phase 1. Project-level scanning, editing workspace configuration, canonical workspace names, MCP changes, remote discovery and synchronization are outside this slice. Roots are already locally configured; an unconfigured root must be rejected.

## Impact and Risks

The CLI, query service and scan selection change. The database schema and MCP contract do not change. Filtering must occur before pagination. A selected-root scan must never mark checkouts in another root missing. Paths remain local and are passed as arguments, never executed as shell text.

## Knowledge References

- `knowledge/architecture/scanning-and-evidence.md` — configured boundaries and evidence.
- `knowledge/architecture/scanning-and-evidence/incremental-and-partial.md` — absence and scan completeness.
- `knowledge/concepts/evidence-and-provenance.md` — uncertainty and observations.

## Traceability

Change `be-workspace-desktop`; branch `feature/be-workspace-desktop`; requirements `docs/requirements/workspace-discovery/requirement.md` and `docs/requirements/project-query/requirement.md`.
