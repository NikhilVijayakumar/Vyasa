# Grill Log: Quality Attributes

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 2 | 2 |
| Behaviour | 4 | 1 |
| Data | 2 | 1 |
| Integration | 1 | 0 |
| Architecture | 2 | 0 |
| Acceptance | 2 | 0 |
| Ambiguity | 2 | 0 |

## Intent

**Q1. Which qualities actually block a release?**

- **Recommendation:** Per the phase gates: determinism, integrity, offline MCP queries, read-only access, recovery, predictable responses, and automated tests of critical requirements. Proposed performance numbers do not block until accepted.
- **Why:** A gate everyone can verify beats a wish list.
- **Status:** Settled
- **Feeds:** NFR section 15


## Scope

**Q2. Which tools and versions (NFD-001, NFD-008)?**

- **Recommendation:** Python 3.12 or newer. `ruff` for linting and formatting, `mypy` (strict for domain and application, standard elsewhere), `pytest` with `pytest-cov`, one `pyproject.toml`. Pre-commit hooks optional.
- **Why:** A small, common toolchain with one configuration file.
- **Status:** Decision needed
- **Feeds:** NFR-026

**Q3. What coverage is required (NFD-009)?**

- **Recommendation:** No global percentage. At least 90% line and branch coverage on the domain and application packages, trend-tracked elsewhere. Every FR scenario tag has a test that cites it, enforced by the traceability check.
- **Why:** Coverage where the logic is, and traceability where the promises are.
- **Status:** Decision needed
- **Feeds:** NFR-041


## Behaviour

**Q4. How are performance targets validated (NFD-003, NFD-004)?**

- **Recommendation:** A harness in `tests/bench/` with seeded synthetic corpora of 10, 100, 500, and 1,000 projects, recording p95 for lookup, search, context, and related queries. Targets stay proposed until a reference machine and CI agree.
- **Why:** Numbers come from measurement, not from the requirement text.
- **Status:** Decision needed
- **Feeds:** NFR-006, NFR-010

**Q5. What is startup expected to do (NFR-009)?**

- **Recommendation:** Open the existing index without scanning and without touching Google Sheets or a provider. A proposed target is ready within one second for a 500-project index.
- **Why:** Fast, offline start is what lets an MCP client launch Vyasa freely.
- **Status:** Recommended
- **Feeds:** NFR-009

**Q6. How does concurrency work (NFR-015)?**

- **Recommendation:** WAL, one writer through a lock row, a 5 s busy timeout, read-only readers. Defined in the local-index package.
- **Why:** One definition in one place.
- **Status:** Settled
- **Feeds:** local-index

**Q7. What compatibility promises exist (NFR-028)?**

- **Recommendation:** Semantic versioning for MCP schemas, forward-only index migrations, a `schema_version` in configuration, and one minor version of deprecation warnings before removal.
- **Why:** Clients and users can plan around it.
- **Status:** Recommended
- **Feeds:** NFR-028


## Data

**Q8. Which platforms are supported (NFR-029)?**

- **Recommendation:** Linux, macOS, and Windows on Python 3.12 and 3.13, tested in a CI matrix. Paths use `pathlib`; evidence uses POSIX-style relative paths; symlink tests skip where privileges are missing.
- **Why:** Support that is not tested is not support.
- **Status:** Recommended
- **Feeds:** NFR-029

**Q9. How is Vyasa installed and configured (NFR-030, NFR-031)?**

- **Recommendation:** `uv tool install` or `pipx`, with entry points `vyasa` (CLI) and `vyasa-mcp` (stdio server). Configuration lookup: `--config`, then `$VYASA_CONFIG`, then the data directory. A `vyasa doctor` command checks the setup and changes nothing.
- **Why:** One obvious path to a working setup, and a command that explains failures.
- **Status:** Decision needed
- **Feeds:** NFR-031


## Integration

**Q10. How are dependencies controlled (NFR-027)?**

- **Recommendation:** Runtime: `mcp`, `pydantic`, `pyyaml`. Optional extras: `sheets`, `remote`, `keyring`. Lower bounds in `pyproject.toml`, a committed lockfile, `sca-audit` on every change, and a license check.
- **Why:** A short list is easier to audit and keeps phases 2 and 3 out of phase 1 installs.
- **Status:** Recommended
- **Feeds:** NFR-027


## Architecture

**Q11. How is modularity checked (NFR-023, NFR-024)?**

- **Recommendation:** An import-linter-style test asserts the dependency direction: adapters to application to domain, never the reverse. New detectors and providers register through a protocol, with no core edits.
- **Why:** Architectural rules that are not checked drift.
- **Status:** Recommended
- **Feeds:** NFR-023

**Q12. What does observability look like (NFR-032 to NFR-034)?**

- **Recommendation:** Structured log events with timestamp, level, event code, run id, and project id when relevant. Scan and sync reports share one summary shape. Freshness appears in every result and in index status.
- **Why:** A common shape makes logs, reports, and tests comparable.
- **Status:** Recommended
- **Feeds:** NFR-032..034


## Acceptance

**Q13. How is release readiness decided (NFR-043)?**

- **Recommendation:** The `phase-gate-verification` matrix has every row verified, the security gate passes, documentation commands run in a smoke test, and any deferred high-priority requirement has an owner and rationale.
- **Why:** Reuses the gate already defined instead of inventing another.
- **Status:** Recommended
- **Feeds:** NFR-043

**Q14. How is documentation kept honest (NFR-040)?**

- **Recommendation:** Commands in the README run in a smoke test. Knowledge and requirements are checked by the validators. Documentation changes ride in the same change as the behaviour.
- **Why:** Documentation that is tested stays accurate.
- **Status:** Recommended
- **Feeds:** NFR-040


## Ambiguity

**Q15. Do we state a minimum hardware requirement (NFD-002)?**

- **Recommendation:** No. Publish measured numbers for the reference machine and CI runners instead.
- **Why:** A guessed requirement misleads; a measurement informs.
- **Status:** Recommended
- **Feeds:** NFR-008

**Q16. What if a proposed target proves unreachable?**

- **Recommendation:** Record the measurement, change the target through a reviewed requirement update, and note the reason. Never quietly relax a test.
- **Why:** The requirements already forbid weakening tests to pass.
- **Status:** Settled
- **Feeds:** NFR section 2.4

## Decisions for you

- **Q2** — Which tools and versions (NFD-001, NFD-008)?
- **Q3** — What coverage is required (NFD-009)?
- **Q4** — How are performance targets validated (NFD-003, NFD-004)?
- **Q9** — How is Vyasa installed and configured (NFR-030, NFR-031)?
