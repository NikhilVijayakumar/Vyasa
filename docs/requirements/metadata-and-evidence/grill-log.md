# Grill Log: Metadata Extraction and Evidence

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 2 | 2 |
| Behaviour | 5 | 1 |
| Data | 2 | 0 |
| Integration | 1 | 0 |
| Architecture | 2 | 0 |
| Acceptance | 1 | 0 |
| Ambiguity | 2 | 1 |

## Intent

**Q1. Why not let an LLM summarize each project?**

- **Recommendation:** Not in the pipeline. An LLM may consume Vyasa's output; it never produces it. Extraction, search, and ranking stay deterministic.
- **Why:** Reproducible tests and privacy depend on it; the architecture already forbids it.
- **Status:** Settled
- **Feeds:** FR-004 S8


## Scope

**Q2. Which manifests and languages come first (DFR-006)?**

- **Recommendation:** Phase 1: Python (`pyproject.toml`, `requirements*.txt`, `setup.cfg`, parsed statically, never executing `setup.py`), JavaScript/TypeScript (`package.json`, `tsconfig.json`), Rust (`Cargo.toml`), Go (`go.mod`), Docker (`Dockerfile`, compose files). Others later, each as its own versioned detector.
- **Why:** Covers the likely portfolio with the fewest parsers; each addition is a self-contained detector.
- **Status:** Decision needed
- **Feeds:** FR-004 S4; DFR-006

**Q3. Is README quality assessed (DFR-002)?**

- **Recommendation:** No. It stays `not_assessed`. An optional later checklist reports separate structural facts (has title, install heading) and never a grade.
- **Why:** A quality grade is subjective and cannot be tested deterministically.
- **Status:** Decision needed
- **Feeds:** FR-005 S7


## Behaviour

**Q4. How are languages detected?**

- **Recommendation:** From manifests (observed) and an extension histogram over the bounded inventory, reported with the sample size. No content heuristics.
- **Why:** Cheap, deterministic, and honest about coverage.
- **Status:** Recommended
- **Feeds:** FR-004

**Q5. What counts as a documented purpose (DO-005)?**

- **Recommendation:** The canonical profile `purpose`, or the manifest `description` field. README prose is not a purpose source in phase 1; the README is recorded by presence and path only.
- **Why:** Extracting a sentence from prose is inference, and FR-004 forbids fabricated facts.
- **Status:** Decision needed
- **Feeds:** FR-004 S2, S3

**Q6. What qualifies as evidence of a technology?**

- **Recommendation:** A key in a recognized manifest (dependencies, dev-dependencies, requires) mapped through the technology registry. Import statements, mentions in text, and file names alone do not count.
- **Why:** Matches FR-004 S5 and keeps scanning cheap and testable.
- **Status:** Recommended
- **Feeds:** FR-004 S4, S5

**Q7. What happens when two sources disagree?**

- **Recommendation:** Each field has a documented precedence list. Equal-precedence disagreement gives status `conflicting`, keeps both observations, and sets no resolved value.
- **Why:** No silent winner; the ownership concept already requires it.
- **Status:** Settled
- **Feeds:** FR-004 S6

**Q8. Is 'enabled' a boolean for OpenSpec or OKF?**

- **Recommendation:** No. The result is `observed`, `not_detected`, `unsupported`, or `unknown`, with the indicators kept separate. A false is never inferred from absence.
- **Why:** Absence of evidence is not a statement that the thing is off.
- **Status:** Settled
- **Feeds:** FR-005, FR-006 S4


## Data

**Q9. How much history do observations keep?**

- **Recommendation:** The current value plus the previous value per field and source. Older values live only in scan-run summaries.
- **Why:** Supports 'README removed' reporting without unbounded growth.
- **Status:** Recommended
- **Feeds:** FR-006 S5

**Q10. What exactly does an evidence record hold?**

- **Recommendation:** Source type, repository-relative path, field or key, line range only when reliable, a truncated SHA-256 content fingerprint, detector id and version, observed time, and revision when known. Never the matched line.
- **Why:** A matched line can contain a password; a fingerprint supports invalidation without content.
- **Status:** Recommended
- **Feeds:** FR-006 S1; SEC-003


## Integration

**Q11. How are YAML and TOML files parsed safely?**

- **Recommendation:** `tomllib` and `json` from the standard library. YAML only through `yaml.safe_load` behind a size cap (256 KiB) and an alias-expansion guard. No code is evaluated and no includes are followed.
- **Why:** YAML aliases can expand without bound; limits turn a denial of service into a skipped file.
- **Status:** Recommended
- **Feeds:** NFR-020


## Architecture

**Q12. What is a detector?**

- **Recommendation:** A pure function of the file inventory and a bounded reader, returning observations. It is registered with an id and version; a version change invalidates cached results. An exception becomes an item error and other detectors continue.
- **Why:** Pure detectors are trivially testable and cacheable.
- **Status:** Settled
- **Feeds:** NFR-001

**Q13. What makes an OpenSpec configuration valid (SE-006)?**

- **Recommendation:** Structural only: `openspec/config.yaml` parses to a mapping, `schema` if present is a string, unknown keys are ignored. The `openspec` command is never run. Spec and change files are counted separately.
- **Why:** Validity rules tied to a CLI version would break silently; structure is stable.
- **Status:** Recommended
- **Feeds:** FR-005 S3, S4


## Acceptance

**Q14. How is determinism proven?**

- **Recommendation:** Golden-file tests: fixture repositories give normalized JSON compared byte for byte; the same input is scanned twice and under shuffled directory order and must match.
- **Why:** Directly tests NFR-001 and FR-004 S7.
- **Status:** Recommended
- **Feeds:** FR-004 S7


## Ambiguity

**Q15. When does an observation become stale (FR-006 S5)?**

- **Recommendation:** At the next scan when its fingerprint or detector version differs, or when the index freshness threshold is exceeded. Queries never stat files, so a change since the last scan is visible only as the observation's age.
- **Why:** A query that inspects files is hidden work. The honest signal is when the fact was last observed.
- **Status:** Decision needed
- **Feeds:** FR-006 S5, S6

**Q16. How is OKF treated?**

- **Recommendation:** Only a bundle whose `index.md` declares `okf_version` is recognized, with version support and conformance counts reported separately; undeclared bundles are `not_detected`, a documented limitation.
- **Why:** Settled in the OKF knowledge concept and the scanning architecture.
- **Status:** Settled
- **Feeds:** FR-005

**Q17. Which remote does a project report, and how is its provider known?**

- **Recommendation:** The remote is read from `.git/config` as text. `origin` is chosen, else the only remote, else none with status ambiguous. The URL is reduced to a credential-free `host/org/repo`, and the provider is derived from the host: `github`, `bitbucket`, `gitlab`, any other host as `other` with the host kept, a path or `file:` URL as `local`, and `none` when there is no remote. The original URL is never stored.
- **Why:** Credentials in URLs must not be persisted; running Git would execute repository-influenced code; owners use self-hosted hosts that no fixed list covers. Owner decision 2026-10-27: unknown hosts stay as `other`.
- **Status:** Settled
- **Feeds:** FR-004 Git origin and repository URL; the remote identity decision

**Q18. What about linked worktrees and submodules, whose `.git` is a pointer file?**

- **Recommendation:** Their remote is reported unavailable. Following the pointer would read a path the repository supplies.
- **Why:** Safe by default; it affects few projects.
- **Status:** Recommended
- **Feeds:** FR-004 Git origin and repository URL

## Decisions for you

- **Q2** — Which manifests and languages come first (DFR-006)?
- **Q3** — Is README quality assessed (DFR-002)?
- **Q5** — What counts as a documented purpose (DO-005)?
- **Q15** — When does an observation become stale (FR-006 S5)?
