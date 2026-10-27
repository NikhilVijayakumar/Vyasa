# Requirement: Framework and Technology Detection

- **Package:** `docs/requirements/framework-detection/`
- **Status:** Grilled — Q7, Q11, Q12, Q13, Q14, and Q15 are recommendations awaiting owner confirmation
- **Roadmap phase:** P1
- **Owns:** FR-025
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-025-framework-detection.feature](features/fr-025-framework-detection.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing. The reading and state rules were captured in `knowledge/` first.

- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.4 framework and technology detector, §9.10 dependency detector
- `knowledge/decisions/framework-detection-from-manifests.md` — manifests read strictly, scoped dependencies, per-ecosystem states
- `knowledge/decisions/technology-registry-as-data.md` — the registry maps dependency names to technologies
- `knowledge/decisions/scan-limits-and-symlink-defaults.md` — 1 MiB per file, links not followed
- `knowledge/decisions/partial-results-never-imply-absence.md` — a bound means not assessed, never absent
- `knowledge/decisions/checkout-walk-observation.md` — one walk and one observation per checkout
- `knowledge/concepts/deterministic-extraction.md` — no LLM, no heuristics beyond documented rules

## Intent

An agent choosing between projects wants to know what each is built with — web framework, test framework, database library — without opening the project. The declared dependencies in the standard manifests answer that. They are also the first thing the scan reads from a repository it does not trust, so the requirement is as much about what is not done: nothing is executed, a bad file is reported rather than guessed at, and an absent framework is never claimed unless the whole assessment was complete.

## Scope

- **Included:**
  - Four ecosystems, each from its root manifest: Python (`pyproject.toml`, `requirements*.txt`), JavaScript and TypeScript (`package.json`), Rust (`Cargo.toml`), Go (`go.mod`).
  - Per-manifest status and the direct dependencies with declared constraint and scope (runtime, dev, optional, build), capped.
  - Technologies mapped from dependencies through a versioned registry, with the scopes they were declared in.
  - An ecosystem state per checkout; a count of nested manifests that were not parsed.
  - Technologies and dependencies in project details; a `technology` filter in project search.
- **Excluded:**
  - Executing anything; reading `setup.py`; resolving dependency graphs or lock files; transitive dependencies; matching dependencies to indexed projects (§9.10).
  - Dockerfile, compose files, `setup.cfg`, `tsconfig.json`, Maven, Gradle, Unreal; nested and workspace member manifests.
  - Any claim about versions actually installed or used at runtime.
- **Deferred:**
  - The additional manifest formats, each as its own detector.
  - Synchronizing technologies to the shared registry.

## Requirements

### FR-025 — Framework and Technology Detection (P1)

Vyasa MUST report, for each scanned checkout, the technologies declared by its supported root manifests, with the evidence that established them and a state for each ecosystem.

- Detection MUST read only regular files at the checkout root, MUST NOT follow a link, MUST NOT read more than 1 MiB of a file, MUST decode strictly as UTF-8, and MUST NOT execute or import anything from the repository.
- Each manifest MUST get its own status — `parsed`, `malformed`, `too_large`, or `unreadable` — with a fixed reason code, never file text; one bad manifest MUST NOT hide the others.
- For a parsed manifest, direct dependencies MUST be recorded with name, declared constraint, and scope (`runtime`, `dev`, `optional`, `build`); scopes MUST NOT be merged, and a dependency kind the parser does not support (platform-specific tables, Go indirect requirements) MUST be counted as skipped, not dropped silently.
- At most 200 dependencies per manifest MUST be stored, with the total.
- A technology MUST come only from the registry: a dependency matching a registry entry yields that technology with the set of scopes in which it was declared; an unknown dependency MUST remain a dependency and create no technology.
- Each ecosystem MUST be `detected` (a root manifest of that ecosystem was read), `not_detected` (complete assessment, no root manifest), `unknown` (the walk stopped early before one was seen), or `not_assessed` (observation made before this detector); a technology MUST NOT be reported absent for any state but a complete assessment of a parsed manifest.
- Nested manifests of a supported name MUST be counted per ecosystem and MUST NOT be parsed; a workspace declaration in a root manifest MUST be recorded as a flag and its members MUST NOT be expanded.
- Results MUST be stored on the checkout's observation, from the same walk, with the registry version.
- `search_projects` MUST accept `technology` (list of registry keys, case-insensitive, OR); a project matches when any active checkout's current observation declares any of them; an unknown key MUST be rejected with `INVALID_INPUT` listing the allowed keys.
- A detection failure MUST be isolated to its checkout.

## Expected Behaviour

- Each supported manifest is read safely and yields dependencies and technologies (`fr-025`).
- Hostile or odd files are reported by status, never interpreted (`fr-025`).
- Ecosystem states keep absence honest; technologies are filterable (`fr-025`).

## Constraints

- Deterministic: same files and registry give the same result (NFR-001).
- Repository content is untrusted and never executed (NFR-020); no file text is stored beyond names, constraints, and keys.
- Bounded: 1 MiB per file, 200 dependencies per manifest, the walk's limits.
- A detector failure is isolated; other checkouts continue.

## Acceptance Expectations

- Golden fixtures per ecosystem: a typical manifest, one with dev/optional/build scopes, one with a workspace, an empty one.
- Hostile fixtures: an oversized file, a symlinked manifest, binary content, a non-UTF-8 file, deeply nested JSON, truncated TOML, a very long dependency list.
- Persistence tests against a real database file; the MCP snapshot test for the new parameter.

## Open Decisions

| Decision | Recommended direction | Grill |
|---|---|---|
| FD-001 | Four ecosystems from root manifests; Docker, compose, and others deferred. | Q2 |
| FD-002 | Technologies plus capped scoped dependencies. | Q3 |
| FD-003 | Dev and optional dependencies create technologies tagged with scope. | Q4 |
| FD-004 | Per-ecosystem states with honest absence. | Q5 |
| FD-005 | Seeded registry v1; `technology` filter only. | Q6, Q8 |
| FD-006 | Root manifests only; nested counted, not parsed. | Q9 |
| FD-007 | Strict read rules. | Q10 |

## Delivery

- `be-framework-detector`: registry and parsers, strict reader, detection on the shared walk, storage on the observation, details, and the `technology` filter.
