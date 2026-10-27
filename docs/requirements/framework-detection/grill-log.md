# Grill Log: Framework and Technology Detection

Run with the `grill-me` skill. Answer each question with a recommendation; nothing is approved until confirmed.

**Status key:** *Settled* — existing documents decide. *Recommended* — low-risk answer, accept unless you object.
*Decision needed* — a real trade-off to choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | Q1 | |
| Scope | Q2, Q9 | |
| Behaviour | Q3, Q4, Q5 | |
| Data | Q6, Q7 | |
| Integration | Q8 | |
| Architecture | Q10, Q11 | |
| Acceptance | Q12 | |
| Ambiguity | Q13, Q14, Q15 | |

## Intent

**Q1. What problem, for whom, and why now?**

- **Recommendation:** Agents want to know what a project is built with before opening it; the manifests state it, the roadmap lists framework detection, and it is the last large Phase 1 detector.
- **Why:** Roadmap P1 and DFR-006; the earlier detectors read names only, so this one needs a review of reading untrusted files.
- **Status:** Settled
- **Feeds:** FR-025

## Scope

**Q2. Which manifests come first?**

- **Recommendation:** `pyproject.toml` and `requirements*.txt` (Python), `package.json` (JavaScript and TypeScript), `Cargo.toml` (Rust), `go.mod` (Go). Docker, compose, `setup.cfg`, `tsconfig.json`, Maven, Gradle, and Unreal are deferred. Owner chose this option.
- **Why:** TOML and JSON are in the standard library; compose needs YAML, which is not, and each added format is its own detector.
- **Status:** Settled
- **Feeds:** FR-025

**Q9. Where are manifests looked for?**

- **Recommendation:** Root manifests only. Nested manifests of a supported name are counted per ecosystem and not parsed; a workspace declaration is a flag and members are not expanded. Owner chose this option.
- **Why:** A monorepo reads as incompletely assessed rather than as having no frameworks, without multiplying reads and storage.
- **Status:** Settled
- **Feeds:** FR-025

## Behaviour

**Q3. What is extracted and stored from a manifest?**

- **Recommendation:** Technologies mapped through the registry plus the direct dependencies (name, declared constraint, scope), at most 200 per manifest with the total. Unknown dependencies stay dependencies and create no technology. Owner chose this option.
- **Why:** §9.4 keeps declared versions and forbids flattening scopes; the cap bounds the index.
- **Status:** Settled
- **Feeds:** FR-025

**Q4. Do development and optional dependencies create technologies?**

- **Recommendation:** Yes, with the set of scopes they were declared in. Owner chose this option.
- **Why:** Test and lint frameworks matter to agents, and scopes must not be silently dropped or merged.
- **Status:** Settled
- **Feeds:** FR-025

**Q5. What does an ecosystem report when its manifest is missing or the walk was partial?**

- **Recommendation:** `detected`, `not_detected` (complete walk, no root manifest), `unknown` (walk stopped early), or `not_assessed` (older observation). A technology is never reported absent except after a complete assessment of a parsed manifest. Owner chose this option.
- **Why:** Partial results never imply absence.
- **Status:** Settled
- **Feeds:** FR-025

## Data

**Q6. What seeds the registry?**

- **Recommendation:** Registry version 1 ships about forty mainstream frameworks and libraries across the four ecosystems plus a ubiquitous list; unknown dependencies create nothing. Owner chose this option.
- **Why:** A small reviewed vocabulary is testable; growth is a data change.
- **Status:** Settled
- **Feeds:** FR-025, registry data

**Q7. How are dependencies capped and named?**

- **Recommendation:** At most 200 per manifest with the total. Python names are normalized (lower case, runs of `-`, `_`, `.` become `-`); other ecosystems keep the declared name lower-cased only for registry matching.
- **Why:** A bound on index growth; PEP 503 normalization is the Python standard.
- **Status:** Recommended
- **Feeds:** FR-025

## Integration

**Q8. How can agents search by technology?**

- **Recommendation:** A `technology` parameter (list of registry keys, OR, case-insensitive, validated against the registry), matching the current observation of any active checkout. No raw dependency-name filter. Owner chose this option.
- **Why:** A closed vocabulary needs no free-text surface and keeps the index small.
- **Status:** Settled
- **Feeds:** FR-025

## Architecture

**Q10. What are the rules for opening manifests from untrusted repositories?**

- **Recommendation:** Regular files at the root only; never a link; at most 1 MiB; strict UTF-8; parser errors, including recursion and value errors, become `malformed` with a fixed reason; nothing is executed and `setup.py` is never read; each manifest has its own status. Owner chose this option.
- **Why:** Repository content is untrusted (NFR-020); one bad file must not hide the others.
- **Status:** Settled
- **Feeds:** FR-025

**Q11. Where does reading happen?**

- **Recommendation:** In `scan_checkout`, after the walk, for the supported root names found in the walk's file list; results are stored on the same observation with the registry version; the parsers are pure functions over text.
- **Why:** One walk per checkout is the standing decision; pure parsers are testable without a filesystem.
- **Status:** Recommended
- **Feeds:** FR-025

## Acceptance

**Q12. How is it proven?**

- **Recommendation:** Golden fixtures per ecosystem, hostile fixtures (oversized, symlinked, binary, non-UTF-8, deeply nested JSON, truncated TOML, very long lists), persistence tests on a real database file, and the MCP snapshot.
- **Why:** The failure modes are boundaries; this is the first detector that reads untrusted content.
- **Status:** Recommended
- **Feeds:** fr-025 scenarios

## Ambiguity

**Q13. What happens to dependency kinds a parser does not support?**

- **Recommendation:** Platform-specific dependency tables (Cargo `target`) and Go indirect requirements are not recorded; the manifest carries a count of skipped entries.
- **Why:** §9.4 forbids flattening platform-specific declarations, and skipping silently would hide the gap.
- **Status:** Recommended
- **Feeds:** FR-025

**Q14. What scope does a `requirements*.txt` file have?**

- **Recommendation:** `runtime` for `requirements.txt`; `dev` when the file name contains `dev` or `test`; otherwise `runtime`. Lines that are options, includes, editable installs, or URLs are skipped and counted.
- **Why:** The name is the only evidence of intent; the rule is documented and tested.
- **Status:** Recommended
- **Feeds:** FR-025

**Q15. How is the same technology from several manifests combined?**

- **Recommendation:** One technology per key per checkout with the union of its scopes and the manifests that declared it.
- **Why:** The question is what the checkout is built with, with the evidence preserved.
- **Status:** Recommended
- **Feeds:** FR-025

## Decisions for you

None open. Q2 through Q6, Q8, Q9, and Q10 were decided by the owner on 2026-10-28; Q7 and Q11 through Q15 are recommendations awaiting confirmation.
