# Requirement: Quality Attributes

- **Package:** `docs/requirements/quality-attributes/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1–P3
- **Owns:** NFR-006, NFR-007, NFR-008, NFR-009, NFR-010, NFR-011, NFR-012, NFR-013, NFR-014, NFR-015, NFR-023, NFR-024, NFR-025, NFR-026, NFR-027, NFR-028, NFR-029, NFR-030, NFR-031, NFR-032, NFR-033, NFR-034, NFR-040, NFR-041, NFR-042, NFR-043
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [operational-qualities.feature](features/operational-qualities.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/architecture/local-storage.md` — WAL, locking, backup, and recovery behaviour
- `knowledge/architecture/system-architecture.md` — modularity, dependency direction, testing architecture
- `knowledge/practices/vertical-slices.md` — how quality checks ride along with each slice
- `knowledge/architecture/c4-system-views.md` — components the qualities apply to

## Intent

Vyasa has to stay fast enough to be used, dependable enough to be trusted, and simple enough to be maintained by a small team. This package sets the measurable bar for performance, reliability, maintainability, portability, observability, documentation, testing, and release, and states which numbers are firm and which are still proposals.

## Scope

- **Included:**
  - Performance and resource targets and how they are validated.
  - Reliability, recovery, idempotency, and concurrency.
  - Architecture, code quality, dependencies, and compatibility.
  - Portability, configuration, installation, logging, reporting, and freshness.
  - Documentation, regression testing, and release readiness.
- **Excluded:**
  - Security requirements (security-and-privacy).
  - Functional behaviour of any single capability.
- **Deferred:**
  - A published minimum hardware specification.
  - Service-level commitments.

## Requirements

Each requirement keeps its full text, priority, and acceptance criteria in
`docs/requirements/non-functional-requirements.md`. This package owns them and decides how they are verified.

| Group | Requirements |
|---|---|
| Performance and resources | NFR-006 search latency, NFR-007 scanning, NFR-008 memory, NFR-009 startup, NFR-010 scalability |
| Reliability | NFR-011 offline, NFR-012 fault isolation, NFR-013 recoverability, NFR-014 idempotency, NFR-015 concurrency |
| Architecture and maintainability | NFR-023 modularity, NFR-024 extensibility, NFR-025 testability, NFR-026 code quality, NFR-027 dependencies, NFR-028 backward compatibility |
| Portability and configuration | NFR-029 cross-platform, NFR-030 configuration, NFR-031 installation and setup |
| Observability | NFR-032 structured logging, NFR-033 scan and sync reporting, NFR-034 freshness |
| Documentation, testing, release | NFR-040 documentation, NFR-041 regression tests, NFR-042 reproducible environments, NFR-043 release readiness |

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- Operational qualities that can be observed are scenarios (`operational-qualities.feature`).
- Targets that need measurement stay proposed until a benchmark confirms them.

## Constraints

- Correctness and safety outrank performance (NFR section 2.4).
- Proposed numbers do not block a release until validated and accepted.
- Quality checks are part of every vertical slice, not a final phase.

## Acceptance Expectations

- The phase gates in `non-functional-requirements.md` section 15 and in `phase-acceptance-criteria.md`.
- Every FR scenario tag has at least one test that cites it.
- The same test suite passes on Linux, macOS, and Windows.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| NFD-001 | Python 3.12 or newer. | Q2 |
| NFD-008 | ruff for lint and format; mypy; pytest with coverage. | Q2 |
| NFD-009 | At least 90% line and branch coverage on domain and application packages; a test for every FR scenario tag. | Q3 |
| NFD-003/004 | Benchmark harness with seeded corpora; targets stay proposed until measured. | Q4 |
| NFD-002 | No minimum hardware stated; publish measured numbers. | Q15 |
| NFR-031 | Install with uv or pipx; entry points `vyasa` and `vyasa-mcp`; a doctor command. | Q9 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-quality-tooling`: pyproject, ruff, mypy, pytest, and the CI matrix.
- `be-traceability-check`: every scenario tag cited by a test.
- `be-benchmark-harness`: seeded corpora and p95 recording.
- `be-doctor-and-logging`: the doctor command and structured logs.
