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

### Second grill: persistence and query (be-language-query)

**Q9. When does language detection run?**

- **Recommendation:** In the scan, per checkout: `store_run` runs `detect_languages` for each checkout it upserts, under the same run and the single-writer lock. Owner chose this option.
- **Why:** The index stays consistent with one run; query-time I/O is forbidden by the freshness decision; a separate step leaves projects without data.
- **Status:** Settled
- **Feeds:** be-language-query

**Q10. How are languages stored?**

- **Recommendation:** Rows per language plus one observation row per checkout (run, time, completeness, data version); the current and previous observation are kept. Owner chose this option.
- **Why:** The filter becomes an indexed predicate and the retention default (current plus previous) holds.
- **Status:** Settled
- **Feeds:** be-language-query, migration

**Q11. Which observation do queries see after a partial rescan?**

- **Recommendation:** The newest, flagged partial with `stopped_by`; the prior complete one is kept as previous. The filter matches positives only and never reports a language as gone. Owner chose this option.
- **Why:** Matches partial-results-never-imply-absence and shows that the tree changed.
- **Status:** Settled
- **Feeds:** be-language-query

**Q12. How does `search_projects` filter by language?**

- **Recommendation:** `language` is a list (OR, case-insensitive exact label) and `language_status` is `files_detected`, `declared`, or omitted for either. Each result says which status matched. No share threshold. Owner chose this option.
- **Why:** An agent can ask for real files versus a bare declaration, which is the point of two statuses.
- **Status:** Settled
- **Feeds:** FR-023 query

**Q13. How do several checkouts aggregate?**

- **Recommendation:** A project matches when any present checkout matches; list items show the union of labels; details give languages per checkout, never summed. Missing or inaccessible checkouts are excluded from matches but keep their last observation in details, marked with the checkout state. Owner chose this option.
- **Why:** FR-021 forbids summing counts across checkouts.
- **Status:** Settled
- **Feeds:** FR-023 query

**Q14. Is file composition persisted in the same change?**

- **Recommendation:** No. Languages only; composition persistence and its filter stay in `be-file-composition-query`. Owner chose this option.
- **Why:** One logical change per OpenSpec change.
- **Status:** Settled
- **Feeds:** Scope

**Q15. How do detected languages relate to the profile's declared `technologies`?**

- **Recommendation:** Separate fields, never merged: detected languages are observed evidence under `languages`, `technologies` stays owner-declared under `profile`, no conflict is computed, and the filter reads detected data only. Owner chose this option.
- **Why:** Observed and declared values keep their owners (field-ownership).
- **Status:** Settled
- **Feeds:** FR-023 query

**Q16. What does a filter with an unknown label do?**

- **Recommendation:** `INVALID_INPUT` listing the allowed labels, validated case-insensitively against the shipped table. Owner chose this option.
- **Why:** A typo must not read as 'no project uses it'.
- **Status:** Settled
- **Feeds:** FR-023 query

**Q17. What does a never-observed checkout show?**

- **Recommendation:** Details report `languages` as `not_observed` (never an empty list), and the filter simply does not match it.
- **Why:** An empty list would read as 'no languages'.
- **Status:** Recommended
- **Feeds:** FR-023 query

**Q18. What if detection fails for one checkout?**

- **Recommendation:** The failure is isolated: that checkout stores a `failed` observation with a safe reason, the scan continues, and the run is partial.
- **Why:** A detector failure must not lose the other projects (NFR isolation).
- **Status:** Recommended
- **Feeds:** be-language-query

**Q19. Is the extra walk per scan acceptable?**

- **Recommendation:** Yes for now. Each scan re-walks every checkout within the FR-021 limits; incremental rescan is a later change. The walk time per checkout is recorded in the observation so the cost is visible.
- **Why:** Skipping unchanged trees needs a fingerprint, which needs its own design.
- **Status:** Recommended
- **Feeds:** Risk

## Decisions for you

None open. Q2, Q5 and Q7 were confirmed on 2026-10-27; Q17, Q18 and Q19 are recommendations awaiting your confirmation.
