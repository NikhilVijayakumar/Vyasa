# Grill Log: Project Markers

Run with the `grill-me` skill. Answer each question with a recommendation; nothing is approved until confirmed.

**Status key:** *Settled* — existing documents decide. *Recommended* — low-risk answer, accept unless you object.
*Decision needed* — a real trade-off to choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | Q1 | |
| Scope | Q2 | |
| Behaviour | Q3, Q4 | |
| Data | Q5, Q10 | |
| Integration | Q6 | |
| Architecture | Q7 | |
| Acceptance | Q8 | |
| Ambiguity | Q9, Q11, Q12 | |

## Intent

**Q1. What problem, for whom, and why now?**

- **Recommendation:** Agents want to know whether a project has a README, docs, agent instructions, OpenSpec, and tests without opening it; it is the next Phase 1 detector family and all of it is answerable from names.
- **Why:** Roadmap P1 lists README, documentation, OpenSpec, and test detection.
- **Status:** Settled
- **Feeds:** FR-024

## Scope

**Q2. Which detectors are in the first change?**

- **Recommendation:** Presence only: README, docs directory, agent instruction files, OpenSpec directory, config, specs, and changes entries, and test indicators. OKF, OpenSpec configuration validity, README parsing, and README quality are deferred. Owner chose this option.
- **Why:** The deferred ones need to open files, which the scan has not done yet and needs its own review.
- **Status:** Settled
- **Feeds:** FR-024

## Behaviour

**Q3. How aggressive is "tests detected"?**

- **Recommendation:** A directory named `tests`, `test`, `__tests__`, or `spec`, or a file matching `test_*.py`, `*_test.py`, `*_test.go`, `*.test.js|ts|jsx|tsx`, `*.spec.js|ts`, or `*Test.java`. The matching rule is recorded. Owner chose this option.
- **Why:** Covers the common conventions; configuration files belong to the framework detector.
- **Status:** Settled
- **Feeds:** FR-024

**Q4. What states can a marker have?**

- **Recommendation:** `detected`, `not_detected` (only after a complete assessment), and `unknown` (walk stopped early and the marker not found). `not_detected` means not detected by these rules, not that none exist.
- **Why:** Partial results never imply absence; §9.9 states the same for tests.
- **Status:** Recommended
- **Feeds:** FR-024

## Data

**Q5. How are evidence paths stored?**

- **Recommendation:** Repository-relative paths only, at most 20 per marker with the total count. Owner chose this option.
- **Why:** The inventory asks for evidence paths; the cap keeps monorepos from bloating the index; no absolute path leaks.
- **Status:** Settled
- **Feeds:** FR-024

**Q10. What do observations made before this change report?**

- **Recommendation:** `not_assessed`, never `not_detected`; each observation records the rules version it was assessed with, null for older ones. Owner chose this option.
- **Why:** Absence may only be inferred from a complete assessment.
- **Status:** Settled
- **Feeds:** FR-024

## Integration

**Q6. How do agents filter on markers?**

- **Recommendation:** `marker` (list of names, OR) and `marker_state` (`detected` default, or `not_detected`), with any-active-checkout matching and unknown matching neither state. Owner chose this option.
- **Why:** One parameter pair does not grow the tool with each detector.
- **Status:** Settled
- **Feeds:** FR-024

## Architecture

**Q7. Where does detection run and where do rules live?**

- **Recommendation:** On the same walk as counts and languages (the walk also reports directories and relative paths), as a pure function over the lists; rules are versioned data like `file_types.json`; results are stored in a table linked to the observation.
- **Why:** One walk per checkout is the standing decision; data keeps additions out of code.
- **Status:** Recommended
- **Feeds:** FR-024

## Acceptance

**Q8. How is it proven?**

- **Recommendation:** Golden fixtures with shuffled order, persistence tests on a real database file, and the MCP snapshot.
- **Why:** Determinism (NFR-001) and the shared-walk guarantee.
- **Status:** Recommended
- **Feeds:** fr-024 scenarios

## Ambiguity

**Q9. Where may each marker be found?**

- **Recommendation:** `readme` and `docs` and the OpenSpec markers at the checkout root only; `agent_instructions` and `tests` at any depth. Owner chose this option.
- **Why:** A README in a vendored subfolder makes "has a README" meaningless, but nested agent files and package tests are real.
- **Status:** Settled
- **Feeds:** FR-024, rules data

**Q11. How are nested agent instruction files represented?**

- **Recommendation:** Each file is evidence with its scope: `root` or the nested directory. The marker is detected when any exists.
- **Why:** §9.8 forbids treating nested files as one global file.
- **Status:** Recommended
- **Feeds:** FR-024

**Q12. Are the OpenSpec indicators one marker?**

- **Recommendation:** No. `openspec_directory`, `openspec_config`, `openspec_specs`, and `openspec_changes` are four markers; configuration validity is deferred.
- **Why:** §9.7 requires separate indicators; a directory without a config must not imply a configuration.
- **Status:** Recommended
- **Feeds:** FR-024

## Decisions for you

None open. Q2, Q3, Q5, Q6, Q9, and Q10 were decided by the owner on 2026-10-27; Q4, Q7, Q8, Q11, and Q12 are recommendations awaiting confirmation.
