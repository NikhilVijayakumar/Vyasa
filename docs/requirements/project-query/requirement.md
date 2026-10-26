# Requirement: Project Search, Context, Relations and Dependencies

- **Package:** `docs/requirements/project-query/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1
- **Owns:** FR-009, FR-010, FR-011, FR-012
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-009-project-search.feature](features/fr-009-project-search.feature), [fr-010-project-details-and-context.feature](features/fr-010-project-details-and-context.feature), [fr-011-related-project-discovery.feature](features/fr-011-related-project-discovery.feature), [fr-012-project-dependencies.feature](features/fr-012-project-dependencies.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/architecture/mcp-interface.md` — tool inventory (§7 onward), response conventions (§6), limits (§15.3)
- `knowledge/architecture/data-model.md` — projects, observations, relationships
- `knowledge/concepts/evidence-and-provenance.md` — evidence and status carried in every result
- `knowledge/concepts/project-identity.md` — stable identifiers returned to callers

## Intent

A coding agent working in one repository can ask what else exists across the portfolio and get a deterministic, explainable, bounded answer from the index: search by name or technology, details and a structured context for one project, related projects, and declared dependencies. The goal is to stop people and agents rebuilding what already exists.

## Scope

- **Included:**
  - Search with filters, ordering, and match provenance.
  - Project details and structured context.
  - Related projects by documented rules.
  - Dependencies and dependents from recognized manifests.
- **Excluded:**
  - The MCP transport and tool schemas (mcp-server).
  - Any scanning or synchronizing triggered by a query.
  - Semantic or LLM-based similarity.
- **Deferred:**
  - Transitive dependencies from lockfiles.
  - Free-text search over document bodies.

## Requirements

### FR-009 — Project Search (P1)

Vyasa MUST support searching the indexed project portfolio using supported metadata fields.

### FR-010 — Project Details and Context (P1)

Vyasa MUST provide detailed metadata and a concise, structured context view for a selected project.

### FR-011 — Related-Project Discovery (P1)

Vyasa MUST support deterministic discovery of potentially related projects.

### FR-012 — Project Dependencies (P1)

Vyasa MUST expose dependency information only where it can be established from recognized evidence.

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- Searches return matches with the matching field and evidence, in a stable order (`fr-009`).
- Details and context mark missing fields instead of failing (`fr-010`).
- Related and dependency results explain their basis and never invent edges (`fr-011`, `fr-012`).

## Constraints

- Read-only: queries never write or scan (mcp-interface §2.5).
- Bounded: default 20 results, maximum 100, with pagination.
- Deterministic ordering with a documented tie-break.
- Proposed p95 latency targets in NFR-006 apply once validated.

## Acceptance Expectations

- Phase 1 criteria 5 and 6 in `phase-acceptance-criteria.md`.
- Every filter combination is covered by parametrized fixtures; identical queries return identical output.
- Dependency results carry a coverage object stating what was and was not parsed.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| search | Name and technology matching rules, AND across filters, FTS5 when available. | Q2 |
| DFR-007 | Relation types: explicit dependency, profile-declared, shared technologies (excluding ubiquitous ones). | Q5 |
| DFR-008 | Direct dependencies from manifests only; internal mapping by package name within one ecosystem. | Q6 |
| technology vocabulary | A versioned built-in registry maps dependency names to technology keys. | Q12 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-search-by-name`: name search with stable ordering and match provenance.
- `be-search-by-technology`: technology filter, combined filters, empty results.
- `be-project-context`: details and context with missing-field marking and availability.
- `be-related-and-dependencies`: relation rules and the dependency table with coverage.
