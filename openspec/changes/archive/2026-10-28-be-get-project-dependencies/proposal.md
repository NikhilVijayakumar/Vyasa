# Change Proposal: be-get-project-dependencies

## Why

Coding agents cannot ask what a project depends on or what depends on it, although the index already holds each checkout's direct dependencies. FR-012 is a Phase 1 requirement. This change adds a read-only tool that answers from recorded evidence and states its coverage.

## What Changes

- **project-dependencies**: new MCP tool `get_project_dependencies` returning a project's direct dependencies and its dependents, each marked internal, ambiguous, or external, with a coverage object.
- **framework-detection**: each parsed root manifest also records the package name it declares (migration 0010), so a dependency can be mapped to an indexed project.

## 1. Problem and Motivation

### Current Situation
`get_project` shows per-manifest dependencies with scope and constraint under `frameworks`. Nothing links a dependency to another indexed project, and nothing answers "who depends on this project".

### Problem
An agent deciding whether to reuse or change a project cannot see its place in the portfolio. Manifests are parsed, but the package name each manifest declares is discarded, so no mapping is possible.

### Evidence
Verified: migration 0009 stores `checkout_dependencies(name, constraint_text, scope)` per manifest and the parsers return no declared name (`src/vyasa/domain/manifests.py`). Requirements FR-012 and decision Q6 (`docs/requirements/decisions-for-review.md`) define the behavior. Assumption: declared names are available in the four supported manifest types.

## 2. Desired Outcome

### Goals
- [ ] An agent can list a project's direct dependencies and its dependents in one call.
- [ ] Internal edges are shown only where the manifests support them.
- [ ] Every answer states what was and was not parsed.

### Team Focus
Changes are judged on MCP tool and interface contracts, data model, and trust boundaries; failure modes, data integrity, provenance of detected facts, and migration impact; and the verification layer that owns each behavior.

### Success Criteria
- [ ] A dependency whose normalized name equals another project's declared package in the same ecosystem is internal; with several such projects it is ambiguous and lists all; otherwise it is external.
- [ ] Dependents are the reverse relation and name the manifest that declares each edge.
- [ ] Coverage reports unparsed manifests, partial or not-assessed observations, nested manifests, and missing declared names.
- [ ] The tool reads only the index and returns no local path.

## 3. Scope

### In Scope
- The `get_project_dependencies` tool, its query, and its MCP declaration and snapshot.
- Capturing the declared package name per manifest, migration 0010, and parser changes.
- Documentation of the tool.

### Out of Scope
- Transitive dependencies and lockfiles.
- Related-project discovery (a separate change).
- Dependencies from nested manifests, unsupported formats, and remote projects.
- A refresh tool.

### Constraints
Read-only tool; standard library only; repository content is untrusted; no new dependency; results bounded (200 dependencies per manifest already stored; at most 100 dependents returned, with the total).

## 4. Stakeholders and Impact

- **Primary stakeholders:** coding agents using the MCP server; the maintainer.
- **Affected components or capabilities:** manifest parsers, framework detection, scan storage, SQLite schema, query layer, MCP server.
- **Dependencies:** `be-framework-detector` (archived) supplies the stored dependencies.
- **Compatibility considerations:** a new nullable column and a new tool; existing tools and observations unchanged. Observations made before the migration have no declared names until the next scan; coverage says so.

## 5. Proposed Direction

Parse the declared name with the dependencies, store it on the manifest row, and answer with one index query: the project's own dependencies from its active checkouts' latest observation, each resolved against the declared names of other projects, plus the reverse. The rules are the decision concept `knowledge/decisions/internal-dependencies-by-declared-package-name.md`. Alternatives (remote or path matching, cross-ecosystem matching, lockfiles) are rejected there.

## 6. Requirements Overview

| ID | Requirement | Expected Outcome | Priority |
|---|---|---|---|
| REQ-001 | Record declared package names | Parsed manifests keep their declared name | Must |
| REQ-002 | List direct dependencies | Name, constraint, scope, ecosystem, source manifest | Must |
| REQ-003 | Resolve internal edges | Internal, ambiguous, or external by exact normalized name in one ecosystem | Must |
| REQ-004 | List dependents | Reverse relation with source manifests, bounded | Must |
| REQ-005 | State coverage | Parsed, unparsed, nested, partial, and unknown declared names are reported | Must |

## 7. Risks and Open Questions

### Risks
| Risk | Impact | Mitigation or Investigation |
|---|---|---|
| Different projects declare the same package name | A wrong single edge | Ambiguous results list every candidate |
| Old observations lack declared names | Missing internal edges | Coverage reports it; a scan fixes it |
| Output grows large | Slow or noisy answers | Existing per-manifest cap; dependents capped at 100 with a total |

### Assumptions
- Root manifests are enough for Phase 1; nested manifests are only counted.

### Open Questions
- [ ] None blocking; pagination of dependents is deferred until a portfolio needs it.

## 8. Acceptance Summary

- [ ] Each specification scenario has a passing test.
- [ ] The MCP snapshot adds only the new tool; the full suite and workflow checks pass.
- [ ] A built executable answers the tool against a scanned fixture workspace.

## 9. Traceability

- **OpenSpec Change ID:** `be-get-project-dependencies`
- **Proposing team:** be (backend — the default workflow for this repository)
- **Proposed branch:** `feature/be-get-project-dependencies`
- **Requirement package:** `docs/requirements/project-query/requirement.md` (FR-012, Q6)
- **Knowledge references:** `knowledge/decisions/internal-dependencies-by-declared-package-name.md` — the mapping rule; `knowledge/decisions/framework-detection-from-manifests.md` — where dependencies come from; `knowledge/decisions/partial-results-never-imply-absence.md` — coverage wording
- **Related issues or references:** None
- **Related existing specifications:** `openspec/specs/framework-detection/spec.md`, `openspec/specs/project-query/spec.md`
- **Related ADRs:** `knowledge/decisions/internal-dependencies-by-declared-package-name.md`

## 10. Readiness Review

- [x] The problem and motivation are clear.
- [x] Goals and success criteria are observable.
- [x] Scope and non-goals are explicit.
- [x] Important stakeholders, constraints, and dependencies are identified.
- [x] Assumptions and unresolved questions are visible.
- [x] The proposing team is identified and its focus and skills applied.
- [x] The proposal is consistent with existing specifications and project conventions.
- [x] Significant ambiguities have been challenged and resolved, or explicitly recorded.
- [x] The change has a stable OpenSpec ID and follows the project's Git discipline.

**Status:** Ready for specification and design
