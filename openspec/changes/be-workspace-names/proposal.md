# Proposal

## Why

People need meaningful names for local workspace roots when browsing projects. A root path alone is not always recognizable.

## What Changes

Allow an explicit local display name for each configured workspace root, list it through the existing CLI, and preserve names across scans. Do not rewrite the hand-maintained configuration file or create an index merely to name a root.

## Scope and Impact

Phase 1; CLI and local metadata only. No scanning, root selection, project identity, MCP contract, or SQLite schema changes. Names are local, may be duplicated, and paths remain available for disambiguation. Unnamed roots show their path.

## Risks

Metadata must not be silently lost or confused with configured roots. Validate before writing, use atomic replacement, preserve malformed files on failure and never accept an unconfigured root. Root names are not shared.

## Knowledge References

- `knowledge/concepts/workspace-names.md` — name ownership and local identity.
- `knowledge/concepts/field-ownership.md` — human and machine-local data ownership.
- `knowledge/decisions/configuration-file-format-and-location.md` — configuration precedence and fail-closed roots.

## Traceability

Change `be-workspace-names`; branch `feature/be-workspace-names`; requirements `docs/requirements/workspace-discovery/requirement.md` and desktop UI-011.
