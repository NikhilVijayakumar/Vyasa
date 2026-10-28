# Grill Log: Project Report

Run with the `grill-me` skill. Answer each question with a recommendation; nothing is approved until confirmed.

**Status key:** *Settled* — existing documents or the owner decide. *Recommended* — low-risk answer, accept unless you object.
*Decision needed* — a real trade-off to choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | Q1 | |
| Scope | Q7 | |
| Behaviour | Q3, Q5 | |
| Data | Q2, Q4 | |
| Integration | Q8 | |
| Architecture | Q9 | |
| Acceptance | Q10 | |
| Ambiguity | Q6 | |

## Intent

**Q1. What does the report add beyond the profile?**

- **Recommendation:** A long-form markdown report in the repository, written by a coding agent from Vyasa's facts plus its own inspection; the profile stays the short structured summary.
- **Why:** Owner chose this on 2026-10-28. Raising the profile limits would weaken the bounded-profile decision; a prompt alone leaves nothing durable.
- **Status:** Settled
- **Feeds:** FR-028

## Scope

**Q7. Does the first change cover monorepo components or search?**

- **Recommendation:** No. One report per checkout and retrieval by project and section only; component reports and full-text search are later changes.
- **Why:** Both need decisions about identity and indexing that the profile has not made either.
- **Status:** Settled
- **Feeds:** FR-028

## Data

**Q2. Where is the report stored for queries?**

- **Recommendation:** The scan stores a bounded copy in the index; the MCP serves it from there.
- **Why:** Owner chose this on 2026-10-28. A project must be answerable from another repository, with no repository access at query time.
- **Status:** Settled
- **Feeds:** FR-028

**Q4. What are the size limits?**

- **Recommendation:** Configurable in `config.toml` under `report` (`max_file_kib`, `max_section_kib`); defaults 256 KiB file and 16 KiB per section; fixed bounds keep the index and any agent's context bounded.
- **Why:** Owner asked on 2026-10-28 for configurable limits with these defaults. Configuration has no settings but workspace roots so far, so the bounds are explicit.
- **Status:** Settled
- **Feeds:** FR-028

## Behaviour

**Q3. How is the report structured?**

- **Recommendation:** Markdown with fixed second-level headings from the template. Unknown headings are dropped and reported.
- **Why:** Fixed names let tools fetch one section and let the scan stay deterministic without parsing prose.
- **Status:** Settled
- **Feeds:** FR-028

**Q5. Which tools serve it?**

- **Recommendation:** `get_report_template` (no index), `get_project_report(project_id, section?)`, and a report status object in `get_project`. The `get_profile_context` workflow mentions the report.
- **Why:** The template and the content have different lifecycles; status in `get_project` avoids loading text by default.
- **Status:** Settled
- **Feeds:** FR-028

## Integration

**Q8. How does the agent learn about the report?**

- **Recommendation:** The `get_profile_context` workflow adds a step naming `get_report_template` and the report path; no other existing tool changes except the status object in `get_project`.
- **Why:** The agent already calls the context tool, so the report is discovered where the profile is.
- **Status:** Settled
- **Feeds:** FR-028

## Architecture

**Q9. Where does the section definition live?**

- **Recommendation:** One domain module holds the section names, purposes, and limits; the template, the section reader, and the tool validation read it.
- **Why:** It is the same approach that keeps the profile guide, validator, and JSON Schema from drifting.
- **Status:** Settled
- **Feeds:** FR-028

## Acceptance

**Q10. How is hostile or untrusted report text tested?**

- **Recommendation:** Fixtures for oversize, a link in place of the file, control characters, a credential-bearing URL, unknown and duplicate headings, and a before/after repository hash.
- **Why:** The report is the largest untrusted text Vyasa stores.
- **Status:** Settled
- **Feeds:** FR-028

## Ambiguity

**Q6. How does a reader know the report is out of date?**

- **Recommendation:** Store the declared commit and date from the report header and the scan time; compare with the repository head in a later change.
- **Why:** Owner confirmed on 2026-10-28; deferred. The comparison needs head-commit reading that the scan does not do yet.
- **Status:** Settled
- **Feeds:** FR-028
