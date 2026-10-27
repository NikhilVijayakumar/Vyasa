# Requirement: Language Detection

- **Package:** `docs/requirements/language-detection/`
- **Status:** Grilled — recommendations pending owner confirmation
- **Roadmap phase:** P1
- **Owns:** FR-023
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-023-language-detection.feature](features/fr-023-language-detection.feature), [fr-023-language-query.feature](features/fr-023-language-query.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing. The status vocabulary was captured in `knowledge/` first.

- `knowledge/architecture/scanning-and-evidence/detector-inventory.md` — §9.3 language detector, §9.13 file composition
- `knowledge/decisions/file-composition-data-and-limits.md` — versioned file-type data shared with this detector, one walk
- `knowledge/decisions/language-evidence-statuses.md` — two distinct statuses and a fixed extension table
- `knowledge/decisions/partial-results-never-imply-absence.md` — a bound means not assessed, never absent
- `knowledge/concepts/evidence-and-provenance.md` — evidence record and observation statuses

## Intent

An agent choosing between projects needs to know what each is written in before opening it. A filename alone proves only that files exist, while a manifest proves what the project declares; reporting both as "uses X" would overstate the evidence. This requirement reports each separately.

## Scope

- **Included:**
  - Per-checkout language histogram from file extensions (`files_detected`).
  - Languages declared by recognized manifest files (`declared`), by file presence.
  - Languages in project details; filtering project search by language.
- **Excluded:**
  - Reading file or manifest content; versions, dependencies, frameworks (see the framework detector).
  - Any claim that a language runs in production.
- **Deferred:**
  - Content-based disambiguation of shared extensions.
  - Synchronizing languages to the shared registry.

## Requirements

### FR-023 — Programming Language Detection (P1)

Vyasa MUST report, for each scanned checkout, the languages found, each with a status that says how it was found.

- `files_detected` MUST come from file extensions through a versioned table; its counts MUST sum to the code count of FR-021.
- `declared` MUST come from the presence of a recognized manifest file; manifest content MUST NOT be read.
- The two statuses MUST stay separate: a language found by both has two evidence rows, never one merged claim.
- An extension or manifest not in the tables MUST be ignored, never guessed.
- A shared extension (such as `.h`) MUST map to exactly one documented label.
- A count that reached a traversal bound MUST be marked partial; absence of a language is then unknown.
- Each result MUST carry evidence: the table version and the completeness marker.
- Languages MUST be detected during the scan, per checkout, and stored with the current and previous observation; a query MUST NOT touch the filesystem.
- A partial rescan MUST become the current observation, flagged partial; a language not found in it MUST NOT be reported as gone.
- `search_projects` MUST accept `language` (list, OR, case-insensitive exact label) and `language_status` (`files_detected`, `declared`, or either when omitted); an unknown label MUST be rejected with `INVALID_INPUT` listing the allowed labels.
- A project MUST match when any present checkout matches; details MUST give languages per checkout and MUST NOT sum them; a never-observed checkout MUST be reported `not_observed`, not as an empty list.
- Detected languages MUST stay separate from the profile's declared `technologies`; neither overrides the other.
- A detection failure MUST be isolated to its checkout, which records a `failed` observation while the scan continues.

## Expected Behaviour

- Extension counts and manifests yield separate statuses; the histogram agrees with the code count (`fr-023`).
- Stored languages are filterable, per checkout, with partial and never-observed states kept honest (`fr-023-query`).
- Unknown types are ignored and a bound makes absence unknown (`fr-023`).

## Constraints

- Deterministic: same tree and table version give the same result (NFR-001).
- File content is never read; paths are never returned (security §4.3).
- Bounded by the FR-021 walk; a detector failure is isolated.

## Acceptance Expectations

- Golden fixtures: a mixed tree, a manifest-only tree, a tree with `.h` and unknown types, and a tree over the entry cap, including shuffled directory order.
- The histogram sum equals the FR-021 code count on every fixture.

## Open Decisions

| Decision | Recommended direction | Grill |
|---|---|---|
| LD-001 | Two statuses, `files_detected` and `declared`, never merged. | Q3 |
| LD-002 | Fixed extension table; shared extensions map to one label; no content reads. | Q4 |
| LD-003 | Manifests count by presence only; parsing waits for the framework detector. | Q2 |
| LD-004 | Detect in the scan per checkout; rows per language; newest observation wins when partial. | Q9–Q11 |
| LD-005 | Filter by `language` and `language_status`; any present checkout matches; unknown label is an error. | Q12, Q13, Q16 |
| LD-006 | Detected languages never merge with profile `technologies`. | Q15 |

## Delivery

- `be-language-detector`: tables, detector on the shared walk, evidence, details output.
- `be-language-query`: persistence in the scan, languages in project details, and the language filter in project search.
