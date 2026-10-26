# Grill Log: Project Search, Context, Relations and Dependencies

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 1 | 1 |
| Behaviour | 5 | 2 |
| Data | 2 | 0 |
| Integration | 1 | 0 |
| Architecture | 2 | 1 |
| Acceptance | 1 | 0 |
| Ambiguity | 2 | 0 |

## Intent

**Q1. Which questions must phase 1 answer?**

- **Recommendation:** Find projects by name, technology, or documentation traits; show one project; give an agent a structured context; list related projects; list dependencies. These are the examples in the interface document.
- **Why:** A short list tied to real examples keeps the tool surface small.
- **Status:** Settled
- **Feeds:** FR-009..FR-012


## Scope

**Q2. What are the matching rules?**

- **Recommendation:** Name: case-insensitive, matches exact, prefix, or token. Technology: exact normalized key through the registry; no fuzzy or stemmed matching. Several filters combine with AND; several values inside one filter combine with OR unless `match=all`. Text search uses SQLite FTS5 over name, declared purpose, and technology names, with a LIKE fallback.
- **Why:** Predictable semantics beat clever ones, and the fallback covers builds without FTS5.
- **Status:** Decision needed
- **Feeds:** FR-009 S1..S3


## Behaviour

**Q3. What is the ordering (FR-009 S6)?**

- **Recommendation:** Exact name, then prefix, then token, then technology-only. Ties break by casefolded display name, then project id. No score is exposed. Pagination is keyset on (name, id), so pages are stable.
- **Why:** A documented ladder is testable; scores invite false precision.
- **Status:** Recommended
- **Feeds:** FR-009 S6

**Q4. How is 'no matches' told apart from 'nothing indexed'?**

- **Recommendation:** An empty result is not an error. When the index is empty or never scanned, `meta.freshness` is `unknown` and a hint code `INDEX_EMPTY` is returned.
- **Why:** An agent should not conclude a project does not exist from an empty index.
- **Status:** Recommended
- **Feeds:** FR-009 S4

**Q5. What makes projects related (DFR-007)?**

- **Recommendation:** Relation types: explicit dependency on another indexed project; profile-declared relation; at least two shared recognized technologies, excluding a ubiquitous list (git, markdown, docker). Ranking is explicit dependency, then profile-declared, then shared-technology count, then name. Counts are integers; no similarity scores.
- **Why:** Rules a person can read and check. The ubiquitous list prevents noise.
- **Status:** Decision needed
- **Feeds:** FR-011

**Q6. Which dependencies are reported (DFR-008)?**

- **Recommendation:** Direct dependencies from recognized manifests, with name, constraint, scope (runtime, dev, optional), ecosystem, and source file. A dependency maps to an indexed project when its name equals a package name that project's manifest declares in the same ecosystem. Dependents use the same table in reverse. Transitive dependencies are out of scope.
- **Why:** Establishable from evidence now; lockfile parsing is a separate, larger decision.
- **Status:** Decision needed
- **Feeds:** FR-012

**Q7. What does a context look like (FR-010)?**

- **Recommendation:** Sections for identity, purpose, technologies, documentation, conventions, tests, and repository. Each holds `value` or `items`, a `status`, `evidence[]`, and `observed_at`. An `availability` block says whether a local checkout or a shared record exists. Lists are capped (for example 50) with `truncated` and a total.
- **Why:** Structured fields let agents act without parsing prose.
- **Status:** Recommended
- **Feeds:** FR-010 S3..S6


## Data

**Q8. How big can a response be?**

- **Recommendation:** Default 20 and maximum 100 items; a response size cap near 64 KiB with `truncated: true` when hit.
- **Why:** Bounded output protects agent context and the server.
- **Status:** Settled
- **Feeds:** mcp-interface §15.3

**Q9. Do queries record usage?**

- **Recommendation:** No. Queries never write, not even counters.
- **Why:** Read-only means read-only, and it lets the connection be opened in read-only mode.
- **Status:** Settled
- **Feeds:** FR-013 S6


## Integration

**Q10. What if the repository is not on this device?**

- **Recommendation:** `availability.local_checkout` is `unavailable_on_this_device`. A path recorded on another device is never shown as usable.
- **Why:** Example E of the ownership requirements.
- **Status:** Settled
- **Feeds:** FR-010 S6


## Architecture

**Q11. Where does query logic live?**

- **Recommendation:** In application-layer services returning Pydantic models. The MCP adapter only validates and maps. Queries use read-only connections.
- **Why:** Keeps the contract testable without a protocol client.
- **Status:** Settled
- **Feeds:** NFR-023

**Q12. Who maintains technology names?**

- **Recommendation:** A versioned built-in registry file maps dependency names to technology keys, display names, and categories. An unknown dependency is listed as a dependency and creates no technology.
- **Why:** Search needs one vocabulary, and unknowns must stay unknown.
- **Status:** Decision needed
- **Feeds:** FR-004; FR-009 S2


## Acceptance

**Q13. How do we prove the queries?**

- **Recommendation:** Fixture indexes; parametrized filter combinations; the same query ten times gives identical bytes; benchmark corpora from local-index measure p95.
- **Why:** Determinism and bounds are the two promises most easily broken later.
- **Status:** Recommended
- **Feeds:** FR-009 S6; NFR-006


## Ambiguity

**Q14. How do we avoid implying a complete dependency graph (FR-012 S5)?**

- **Recommendation:** Every dependency result includes `coverage`: manifests parsed, unsupported manifests seen, and whether any source was skipped. Absence of a dependency is only meaningful relative to that coverage.
- **Why:** The honest unit is what was examined, not what exists.
- **Status:** Recommended
- **Feeds:** FR-012 S2, S5

**Q15. Do registry-only projects appear in search?**

- **Recommendation:** Yes, labelled `source: shared_registry` with no local availability (phase 2).
- **Why:** Keeps one search surface across phases.
- **Status:** Settled
- **Feeds:** shared-registry

## Decisions for you

- **Q2** — What are the matching rules?
- **Q5** — What makes projects related (DFR-007)?
- **Q6** — Which dependencies are reported (DFR-008)?
- **Q12** — Who maintains technology names?
