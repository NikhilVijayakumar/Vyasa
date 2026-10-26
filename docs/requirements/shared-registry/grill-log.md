# Grill Log: Shared Registry and Cross-Device Visibility

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 1 | 1 |
| Behaviour | 6 | 2 |
| Data | 2 | 1 |
| Integration | 1 | 0 |
| Architecture | 1 | 0 |
| Acceptance | 1 | 0 |
| Ambiguity | 2 | 0 |

## Intent

**Q1. Why Google Sheets?**

- **Recommendation:** Product decision: a human-editable portfolio view needing no infrastructure. The cost is quotas, no transactions, and anyone with edit rights can change cells; the design plans for batch writes and optimistic checks.
- **Why:** Naming the limits now keeps them from becoming surprises.
- **Status:** Settled
- **Feeds:** FR-016


## Scope

**Q2. Which fields are exported (SP-006)?**

- **Recommendation:** Allowlist v1: project id, display name, approved purpose, public repository URL, normalized remote identity, languages, technologies, README/OpenSpec/OKF/tests presence, declared lifecycle, Last Verified At, details status. Portfolio fields: tracking level, priority, notes. Never: local paths, workspace roots, checkout names, evidence lines, credentials, internal URLs without approval.
- **Why:** Starts narrow; adding a field is a classified, reviewed change.
- **Status:** Decision needed
- **Feeds:** FR-016 S4


## Behaviour

**Q3. How are conflicts decided (NFD-010, DFR-009)?**

- **Recommendation:** By ownership. Portfolio fields: the sheet wins and is imported. Scanner-owned fields: the newest observation wins and is written only if the cell still holds the last synced value; a hand-edited cell is a conflict, kept untouched and reported until the user picks `--prefer local|sheet`.
- **Why:** Never silently overwrite a human, never let a stale device overwrite a fresher fact.
- **Status:** Decision needed
- **Feeds:** FR-016 S3, S6

**Q4. Which Google authentication (DFR-010, SP-007)?**

- **Recommendation:** A service account by default, with the sheet explicitly shared with its address, so access is limited to that sheet. OAuth installed-app flow is an option for individuals. Credentials live in the OS keyring or a 0600 file outside any repository.
- **Why:** Sharing one sheet with a service account is the closest thing to least privilege Sheets offers.
- **Status:** Decision needed
- **Feeds:** FR-016 S5

**Q5. When does sync run?**

- **Recommendation:** Only by an explicit command, with `--dry-run` showing the plan. No MCP tool exposes sync to agents, and queries never trigger it.
- **Why:** An agent should not be able to push data to a cloud service.
- **Status:** Settled
- **Feeds:** NFR-037

**Q6. How is the registry schema checked (S8)?**

- **Recommendation:** A meta tab records the schema version. Required tabs and columns are matched by header name, not position. A missing required column aborts before any write; extra columns are left alone.
- **Why:** Header matching survives people inserting columns.
- **Status:** Recommended
- **Feeds:** FR-016 S8

**Q7. How are rows matched?**

- **Recommendation:** By the Project ID column; failing that, by normalized remote alias. Two rows for one project are a conflict and nothing is written for them.
- **Why:** Identity rules decide matches, never the adapter.
- **Status:** Recommended
- **Feeds:** FR-017 S2

**Q8. What about partial failure and retries?**

- **Recommendation:** Idempotent upserts in batches, with per-row results recorded. Rerunning converges. Rows are never deleted; a project no longer seen is marked `not seen since`.
- **Why:** Safe retries are what make a flaky API acceptable.
- **Status:** Recommended
- **Feeds:** FR-016 S5; NFR-035


## Data

**Q9. What do shared timestamps mean (DO-009)?**

- **Recommendation:** `Last Verified At`: when any device last observed the project. `Last Synced At`: when this row was last written. Local scan status stays local.
- **Why:** Keeps scanning time and sync time from being confused.
- **Status:** Decision needed
- **Feeds:** FR-017 S5

**Q10. How is local data kept out?**

- **Recommendation:** A canary test sets a sentinel in every local-only field and proves it never appears in any payload.
- **Why:** A property that must never fail deserves a test that tries to make it fail.
- **Status:** Recommended
- **Feeds:** FR-016 S4; FR-017 S4


## Integration

**Q11. How are API limits handled?**

- **Recommendation:** Batch update calls in chunks of at most 500 rows; exponential backoff with jitter, a maximum of five attempts, and honouring Retry-After.
- **Why:** Bounded retries turn a quota hit into a partial, reported run.
- **Status:** Recommended
- **Feeds:** NFR-035


## Architecture

**Q12. How heavy is the Google client?**

- **Recommendation:** The official Google libraries, isolated in the adapter and installed as an optional extra (`vyasa[sheets]`) so phase 1 stays small and offline.
- **Why:** Optional extras keep dependencies out of installs that do not need them.
- **Status:** Recommended
- **Feeds:** NFR-027


## Acceptance

**Q13. How is it tested without Google?**

- **Recommendation:** A fake in-memory Sheets gateway behind a protocol for unit and integration tests; contract tests against a dedicated spreadsheet run only when an environment variable is set.
- **Why:** CI must not depend on Google.
- **Status:** Recommended
- **Feeds:** FR-016


## Ambiguity

**Q14. Are projects with only a provisional identity exported?**

- **Recommendation:** No. They are flagged and left out until they have a remote or a root-commit identity, since another device could not match them.
- **Why:** A row nobody can match is clutter.
- **Status:** Recommended
- **Feeds:** FR-017 S2

**Q15. How does a registry-only project look to a client?**

- **Recommendation:** Labelled `source: shared_registry`, with `availability.local_checkout: unavailable_on_this_device`, and no path.
- **Why:** Example E of the ownership requirements.
- **Status:** Settled
- **Feeds:** FR-017 S1, S3

## Decisions for you

- **Q2** — Which fields are exported (SP-006)?
- **Q3** — How are conflicts decided (NFD-010, DFR-009)?
- **Q4** — Which Google authentication (DFR-010, SP-007)?
- **Q9** — What do shared timestamps mean (DO-009)?
