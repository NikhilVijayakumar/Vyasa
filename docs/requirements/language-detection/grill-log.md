# Grill Log: Language Detection

Run with the `grill-me` skill. Answer each question with a recommendation; nothing is approved until confirmed.

**Status key:** *Settled* â€” existing documents decide. *Recommended* â€” low-risk answer, accept unless you object.
*Decision needed* â€” a real trade-off to choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | Q1 | |
| Scope | Q2 | |
| Behaviour | Q3 | |
| Data | Q4 | |
| Integration | Q5 | |
| Architecture | Q6 | |
| Acceptance | Q7 | |
| Ambiguity | Q8 | |

## Intent

**Q1. What problem, for whom, and why now?**

- **Recommendation:** Agents need a project's languages before opening it; it is the next unbuilt P1 detector and file composition already reserves its histogram.
- **Why:** Roadmap P1 lists language detection; FR-021 requires the histogram to agree with the code count.
- **Status:** Settled
- **Feeds:** FR-023

## Scope

**Q2. Are manifests parsed?**

- **Recommendation:** No. A manifest file's presence declares its language; parsing versions and dependencies belongs to the framework detector (§9.4).
- **Why:** Keeps one slice and avoids a parser per format over untrusted input.
- **Status:** Recommended
- **Feeds:** FR-023 `declared`

## Behaviour

**Q3. What does a detected language mean?**

- **Recommendation:** Two statuses, `files_detected` and `declared`, kept as separate evidence rows. Owner chose this option.
- **Why:** §9.3 requires the meanings to stay distinguishable.
- **Status:** Settled
- **Feeds:** FR-023

## Data

**Q4. How are shared extensions mapped?**

- **Recommendation:** A fixed versioned table, one label per extension (`.h` is a C/C++ header label, markup grouped as HTML/CSS); no content reads, no guessing. Owner chose this option.
- **Why:** Keeps the histogram summing to the code count and honours the no-content rule.
- **Status:** Settled
- **Feeds:** FR-023, table

## Integration

**Q5. Are languages synchronized to the shared registry?**

- **Recommendation:** No, machine-local in phase 1, like file composition counts.
- **Why:** Registry sync is phase 2 and counts are checkout-specific.
- **Status:** Recommended
- **Feeds:** Deferred scope

## Architecture

**Q6. Where does it run?**

- **Recommendation:** On the FR-021 walk, so both agree; the table extends the existing `file_types.json` data with labels.
- **Why:** Decision `file-composition-data-and-limits` already shares data and the walk.
- **Status:** Settled
- **Feeds:** FR-023

## Acceptance

**Q7. How is it proven?**

- **Recommendation:** Golden fixtures with shuffled order; the sum equals the FR-021 code count.
- **Why:** Determinism (NFR-001) and the shared-walk guarantee.
- **Status:** Recommended
- **Feeds:** fr-023 scenarios

## Ambiguity

**Q8. What if a language is in neither table or the walk is partial?**

- **Recommendation:** Unknown extensions are ignored; a partial walk marks results partial and absence unknown, never absent.
- **Why:** Matches partial-results-never-imply-absence.
- **Status:** Settled
- **Feeds:** FR-023

## Decisions for you

None open; Q2, Q5 and Q7 are recommendations awaiting your confirmation.
