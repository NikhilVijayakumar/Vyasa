# Requirement: Metadata Extraction and Evidence

- **Package:** `docs/requirements/metadata-and-evidence/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1
- **Owns:** FR-004, FR-005, FR-006, NFR-001, NFR-002, NFR-005
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-004-deterministic-metadata-extraction.feature](features/fr-004-deterministic-metadata-extraction.feature), [fr-005-documentation-and-standards-detection.feature](features/fr-005-documentation-and-standards-detection.feature), [fr-006-evidence-and-unknown-values.feature](features/fr-006-evidence-and-unknown-values.feature), [grill-additions.feature](features/grill-additions.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/architecture/scanning-and-evidence.md` — detector architecture (§6), detector inventory (§9), evidence model (§10), statuses (§11)
- `knowledge/concepts/evidence-and-provenance.md` — evidence record shape and observation statuses
- `knowledge/technologies/okf.md` — OKF recognition rule and conformance
- `knowledge/architecture/c4-system-views.md` — detector registry within the server components
- `knowledge/concepts/field-ownership.md` — declared versus observed values

## Intent

Every fact Vyasa reports comes from a recognized source through a documented deterministic rule, carries the evidence behind it, and says plainly when it is unknown. This is the product's trust guarantee: a smaller index of verifiable facts is better than a larger one that guesses.

## Scope

- **Included:**
  - Detectors for identity, name, purpose, Git, languages, frameworks, README, documentation, OpenSpec, OKF, agent instructions, tests, and dependencies.
  - The evidence record and the observation statuses.
  - Freshness vocabulary for observations.
- **Excluded:**
  - Subjective README quality.
  - Semantic summaries and any LLM-produced metadata.
  - Import-statement or source-code analysis.
  - Remote file inspection (remote-discovery).
- **Deferred:**
  - README quality checklist, until agreed.
  - Lockfile-based transitive dependencies.
  - Further ecosystems after the first five.

## Requirements

### FR-004 — Deterministic Metadata Extraction (P1)

Vyasa MUST extract supported project metadata through documented, deterministic rules applied to recognized repository sources.

#### Supported metadata categories

- Project name.
- Explicitly documented purpose or description.
- Git origin and repository URL.
- Programming languages.
- Frameworks and technologies.
- Recognized manifests and configuration files.
- Project-owned profile fields.
- Relevant source paths and observation timestamps.

### FR-005 — Documentation and Standards Detection (P1)

Vyasa MUST identify supported documentation, engineering configuration, and agent instruction artifacts.

#### Required detection categories

- README presence and path.
- Documentation directories and recognized documentation entry points.
- Recognized documentation structure.
- OpenSpec directory and configuration presence.
- OpenSpec configuration validity according to supported rules.
- Presence of meaningful OpenSpec specification or change files.
- Recognized agent instruction files.
- Test-related files and configuration.
- Other explicitly supported conventions, once defined.

### FR-006 — Evidence and Unknown Values (P1)

Vyasa MUST make the origin and certainty of extracted metadata understandable to users and calling agents.

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- Recognized evidence yields a value with its source; unrecognized text yields nothing (`fr-004`).
- Presence, validity, and meaning of OpenSpec and OKF are reported separately (`fr-005`).
- Every value says whether it is observed, declared, unknown, unsupported, inaccessible, stale, or conflicting (`fr-006`).

## Constraints

- Deterministic: same inputs and detector version give the same output (NFR-001).
- Evidence stores locations and fingerprints, never matched text or document bodies (security §4.3).
- No LLM in extraction, search, or ranking (FR-004 S8).
- A detector failure is isolated; other detectors and projects continue.

## Acceptance Expectations

- Phase 1 criteria 3 and 4 in `phase-acceptance-criteria.md`.
- Golden-file fixtures give identical normalized output, including under shuffled directory order.
- Each detector has positive, absent, invalid, and boundary tests.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| DFR-006 | First detector set: Python, JavaScript/TypeScript, Rust, Go, and Docker. | Q2 |
| DFR-002 | README quality stays not_assessed in phase 1. | Q3 |
| DO-005 | Purpose comes only from the canonical profile or a manifest description, never README prose. | Q5 |
| SE-006 | OpenSpec validity is structural: config parses as a mapping with known keys. | Q13 |
| NFR-005 | Observations are marked stale by the next scan or age, not by checking files at query time. | Q15 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-detector-framework`: registry, contract, versioning, failure isolation, golden-file harness.
- `be-manifest-detectors`: Python manifests end to end with evidence.
- `be-doc-and-standards-detectors`: README, documentation, OpenSpec, OKF, agent files, tests.
- `be-observation-statuses`: statuses, conflicts, and freshness in results.
