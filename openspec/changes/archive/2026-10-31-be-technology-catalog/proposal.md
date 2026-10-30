# Proposal

## Why

Desktop users need a selectable list of supported technologies when searching projects. Typing internal registry keys is error-prone.

## What Changes

Expose the existing versioned detector registry as a read-only CLI catalog. The desktop uses registry keys for the existing indexed technology search.

## Scope and Impact

Phase 1. CLI only; no MCP, index schema, technology inference, scanning or registry editing changes. Catalog entries describe supported detection, not technologies observed in any project.

## Risks

Catalog availability and detection coverage are different. UI labels must not imply that every entry occurs in the index. Catalog reads must not create or modify an index.

## Knowledge References

- `knowledge/decisions/technology-registry-as-data.md` — registry ownership and versioning.
- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — technology detector meaning.
- `knowledge/concepts/evidence-and-provenance.md` — observed evidence and unknown states.

## Traceability

Change `be-technology-catalog`; branch `feature/be-technology-catalog`; requirement `docs/requirements/framework-detection/requirement.md` (FR-025).
