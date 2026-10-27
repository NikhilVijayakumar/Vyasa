# Requirement: Project Markers

- **Package:** `docs/requirements/project-markers/`
- **Status:** Grilled — Q4, Q7, Q8, Q11, and Q12 are recommendations awaiting owner confirmation
- **Roadmap phase:** P1
- **Owns:** FR-024
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-024-project-markers.feature](features/fr-024-project-markers.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing. The storage and state rules were captured in `knowledge/` first.

- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.5 README, §9.6 documentation structure, §9.7 OpenSpec, §9.8 agent instructions, §9.9 test indicators
- `knowledge/decisions/project-marker-observations.md` — presence-only markers, three states, capped relative paths
- `knowledge/decisions/checkout-walk-observation.md` — one walk and one observation per checkout
- `knowledge/decisions/partial-results-never-imply-absence.md` — a bound means not assessed, never absent
- `knowledge/decisions/mcp-local-paths-omitted-by-default.md` — no absolute path in tool results
- `knowledge/concepts/evidence-and-provenance.md` — evidence and observation statuses

## Intent

An agent choosing between projects wants to know, without opening them, whether a project has a README, documentation, agent instructions, an OpenSpec setup, and tests. Each is answered from file and directory names alone. The risk is overstating: a directory named `docs` is not documentation quality, and a missing marker may only mean the scan stopped early or never looked. This requirement keeps those states apart.

## Scope

- **Included:**
  - Eight markers: `readme`, `docs`, `agent_instructions`, `openspec_directory`, `openspec_config`, `openspec_specs`, `openspec_changes`, `tests`, by names and directories only.
  - A state per marker and checkout: detected, not detected, or unknown.
  - Repository-relative evidence paths, capped.
  - Markers in project details and a `marker` filter in project search.
- **Excluded:**
  - Reading any file: README parsing or quality, OpenSpec configuration validity, OKF bundles (need content reads), test execution.
  - Test framework configuration and dependencies (framework detector).
- **Deferred:**
  - OKF detection, OpenSpec validity indicator, README sections.
  - Synchronizing markers to the shared registry.

## Requirements

### FR-024 — Project Marker Detection (P1)

Vyasa MUST report, for each scanned checkout, which of the eight markers were detected, using documented deterministic rules over file and directory names only.

- Rules MUST come from versioned data: README names (root only), documentation directories (root only), agent instruction file names (any depth, with scope), the OpenSpec directory and its config, specs, and changes entries (root only), and test directories and file-name patterns (any depth).
- Each marker MUST be reported as `detected`, `not_detected`, or `unknown`: `not_detected` only when the assessment was complete; `unknown` when the walk stopped early and the marker was not found.
- The OpenSpec indicators MUST stay separate markers; a directory without a config MUST NOT imply a configuration.
- Each detected marker MUST carry evidence: the rules version, the matching rule, the repository-relative paths (at most 20 stored, with the total), and for agent instructions the scope (root or nested path).
- Detection MUST NOT open any file and MUST NOT execute anything; no absolute path MAY be stored or returned.
- Markers MUST be detected during the scan from the same walk as the counts and languages, and stored on the same observation.
- An observation made before marker detection MUST report `not_assessed`, never `not_detected`.
- `search_projects` MUST accept `marker` (list of marker names, OR) and `marker_state` (`detected`, the default, or `not_detected`); a project matches when any active checkout matches; an unknown name or state MUST be rejected with `INVALID_INPUT` listing the allowed values.
- A detection failure MUST be isolated to its checkout.

## Expected Behaviour

- Each marker is found by its rule and reported with evidence (`fr-024`).
- Partial, failed, and older observations never read as not detected (`fr-024`).
- Markers are filterable, per checkout, with unknown matching neither state (`fr-024`).

## Constraints

- Deterministic: same tree and rules give the same result (NFR-001).
- File content is never read; only repository-relative paths are stored (security §4.3).
- Bounded by the FR-021 walk; one walk per checkout.
- Detector failure is isolated; other checkouts continue.

## Acceptance Expectations

- Golden fixtures: a tree with every marker, an empty tree, a monorepo with nested agent files and tests, an OpenSpec directory without config, a tree over the entry cap, and shuffled directory order.
- Persistence tests against a real database file; MCP snapshot test for the new parameters.

## Open Decisions

| Decision | Recommended direction | Grill |
|---|---|---|
| PM-001 | Presence-only markers; OKF, validity, and parsing deferred. | Q2 |
| PM-002 | Capped repository-relative evidence paths. | Q5 |
| PM-003 | `marker` and `marker_state` filter. | Q6 |
| PM-004 | Per-marker location rules in versioned data. | Q9 |
| PM-005 | Old observations are `not_assessed`. | Q10 |

## Delivery

- `be-project-markers`: rules data, detection on the shared walk, storage on the observation, details, and the filter.
