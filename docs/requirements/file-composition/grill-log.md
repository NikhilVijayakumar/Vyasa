# Grill Log: File Composition

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 2 | 0 |
| Behaviour | 2 | 0 |
| Data | 2 | 0 |
| Integration | 1 | 0 |
| Architecture | 1 | 0 |
| Acceptance | 1 | 0 |
| Ambiguity | 2 | 0 |

## Intent

**Q1. Who needs these counts, and what do they decide?**

- **Recommendation:** A maintainer filtering for documentation-only repositories (knowledge bundles, specification repositories) and an agent sizing a project before opening it. Nothing else depends on them.
- **Why:** If no decision uses a number, it is noise. These two uses are concrete and cheap to serve.
- **Status:** Recommended
- **Feeds:** FR-021

## Scope

**Q2. Do we count lines or measure size?**

- **Recommendation:** No. File counts only, from names. No content is read.
- **Why:** Lines and sizes need reads, which the scan limits and the no-content rule discourage, and nothing named in Q1 needs them.
- **Status:** Settled
- **Feeds:** FR-021 S11

**Q3. Per-directory breakdowns?**

- **Recommendation:** Deferred. One total per category per checkout.
- **Why:** A breakdown is a different observation with a different size and privacy shape; add it when a question needs it.
- **Status:** Recommended
- **Feeds:** FR-021

## Behaviour

**Q4. How many files may the count walk visit?**

- **Recommendation:** Its own cap of 50,000 entries, with the accepted depth and 60-second limits unchanged. Beyond it the count is partial.
- **Why:** The accepted 5,000-entry inventory cap exists to bound reading and parsing. A count reads nothing, and at 5,000 most real repositories would be partial, which would make the feature mostly `unknown`. The number is a starting point to validate against representative workspaces. Confirmed by the owner 2026-10-27.
- **Status:** Settled
- **Feeds:** FR-021 S6, FC-001

**Q9. What is a documentation file?**

- **Recommendation:** Extensions `.md`, `.mdx`, `.rst`, `.adoc`. Not `.txt`, and not extension-less names such as `README` or `LICENSE`. They are data, versioned with the classification data.
- **Why:** `.txt` is too often data, logs, or notes. Extension-less names would need a name list, which is inference. A short explicit list is testable.
- **Status:** Recommended
- **Feeds:** FR-021 S1

## Data

**Q5. How is the classification versioned?**

- **Recommendation:** Extension lists live in versioned data, like the technology registry. A new data version marks existing observations stale.
- **Why:** The same tree must give the same counts for the same data version, and a changed list must not silently change old results.
- **Status:** Recommended
- **Feeds:** NFR-001, FR-021

**Q8. Are the counts synchronized to the shared registry?**

- **Recommendation:** No, not in phase 1. They are checkout-specific and change often; they stay machine-local and out of the export allowlist.
- **Why:** The registry should hold stable portfolio facts. Counts differ per device and would create sync noise. Revisit when a team need appears. Confirmed by the owner 2026-10-27.
- **Status:** Settled
- **Feeds:** FR-021, FC-002

## Integration

**Q6. How does this relate to the language detector?**

- **Recommendation:** One walk feeds both. The language histogram is a refinement of the code count, so the two agree. Counts appear in project details; `documentation_only` is a search filter.
- **Why:** Two walks over the same tree would disagree at the edges and double the cost.
- **Status:** Recommended
- **Feeds:** FR-021, FR-009, FR-010

## Architecture

**Q10. Is this a detector or part of discovery?**

- **Recommendation:** A detector in the registry (§9.13) that consumes the shared walk. Discovery decides whether something is a project; it does not describe it.
- **Why:** A detector failure is isolated and versioned; discovery failures are not.
- **Status:** Recommended
- **Feeds:** FR-004, FR-021

## Acceptance

**Q11. How is it proven?**

- **Recommendation:** Golden-file fixtures (documentation-only, mixed, unknown types, over the cap, empty, unreadable directory) plus a symlink-escape fixture and a shuffled-order run.
- **Why:** The failure modes are boundaries, not logic, and fixtures show them directly.
- **Status:** Recommended
- **Feeds:** FR-021 S1–S8

## Ambiguity

**Q7. Are `.MD` and `.md` the same?**

- **Recommendation:** Yes. Extensions compare case-insensitively.
- **Why:** Case differs across platforms; counts must not.
- **Status:** Recommended
- **Feeds:** FR-021

**Q12. What is a file with no extension, or a dotfile?**

- **Recommendation:** Other. `.gitignore` has no extension in the sense used here, and a name list for them is out of scope.
- **Why:** The rule stays one lookup on the extension; exceptions need evidence nobody has asked for.
- **Status:** Recommended
- **Feeds:** FR-021 S2

### Second grill: persistence and query (be-file-composition-query)

**Q13. How do composition counts share the walk with languages?**

- **Recommendation:** One walk, both results: a single function walks the checkout once and feeds the language tally and the composition tally. Owner chose this option after seeing that a second walk contradicts a shared row.
- **Why:** The language histogram and the code count then come from one file list and agree by construction; scan cost stays at one walk per checkout.
- **Status:** Settled
- **Feeds:** be-file-composition-query

**Q14. Where are the counts stored?**

- **Recommendation:** As columns on the checkout walk observation that already holds languages (code, documentation, other). Nullable, because observations made before this change have no counts. Owner chose this option.
- **Why:** One observation is one walk: shared status, completeness, failure, and the current-plus-previous retention.
- **Status:** Settled
- **Feeds:** be-file-composition-query, migration

**Q15. How does `documentation_only` filter a project with several checkouts?**

- **Recommendation:** `documentation_only` true matches when any active checkout is true; false when any active checkout is false; a checkout with unknown (partial or never counted) matches neither. Details give counts and the indicator per checkout and never a project total. Owner chose this option.
- **Why:** Consistent with the language filter; an unknown checkout must not read as documentation-only or as code (FR-021).
- **Status:** Settled
- **Feeds:** FR-021 query

**Q16. What do counts show for an observation made before counts existed, or for a failed one?**

- **Recommendation:** `composition` reports status `not_counted` with no numbers and `documentation_only` null; never zeros.
- **Why:** Zero would read as an empty checkout.
- **Status:** Recommended
- **Feeds:** FR-021 query

**Q17. Is `documentation_only` stored?**

- **Recommendation:** No. It is derived when read from the stored counts and the observation's completeness, so it cannot disagree with them.
- **Why:** One source of truth for the indicator.
- **Status:** Recommended
- **Feeds:** FR-021 query

## Decisions for you

None open. Q4 (separate 50,000-entry counting cap) and Q8 (counts machine-local in phase 1) were confirmed by the owner on 2026-10-27. Q13–Q15 were decided by the owner on 2026-10-27; Q16 and Q17 are recommendations awaiting confirmation.
