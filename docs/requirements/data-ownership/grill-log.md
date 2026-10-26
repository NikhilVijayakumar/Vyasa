# Grill Log: Data Ownership and Source of Truth

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 3 | 2 |
| Behaviour | 3 | 0 |
| Data | 2 | 0 |
| Integration | 1 | 0 |
| Architecture | 1 | 0 |
| Acceptance | 1 | 0 |
| Ambiguity | 2 | 1 |

## Intent

**Q1. What goes wrong without explicit ownership?**

- **Recommendation:** A sync overwrites a human's note, a scanner replaces a declared purpose with a guess, or a local path lands in a shared sheet. Each is silent and each destroys trust.
- **Why:** The examples in the requirements describe these failures concretely.
- **Status:** Settled
- **Feeds:** DOR-003


## Scope

**Q2. Where does the ownership registry live (DOR-001)?**

- **Recommendation:** A declarative table in the domain layer: field, owner category, precedence list, scope (local, shared, portfolio), exportable, sync direction. A completeness test fails when a persisted or observed field has no entry.
- **Why:** Code is the one place every adapter must pass through, and a test keeps documents from drifting.
- **Status:** Recommended
- **Feeds:** DOR-001, DOR-012

**Q3. Which fields are portfolio-owned (DO-006)?**

- **Recommendation:** Start from the registry baseline: tracking level (a small fixed set such as tracked, watch, ignored), domain, and project type. Priority (P0 to P3) and notes (free text up to 2,000 characters) are candidates that need a reviewed schema change first. Anything else needs a classification before use.
- **Why:** Small and explicit; people can ask for more.
- **Status:** Decision needed
- **Feeds:** FR-016 S3

**Q4. Who owns lifecycle status (DO-007)?**

- **Recommendation:** Two fields. `lifecycle_declared` is project-owned, from the profile. `portfolio_status` is portfolio-owned: active, review, archive-candidate, archived. A declared obsolete lifecycle can raise a review candidate but never changes the portfolio status.
- **Why:** Splitting removes the clash between what a project says and what a portfolio decides.
- **Status:** Decision needed
- **Feeds:** FR-020 S2


## Behaviour

**Q5. What is the precedence for name and purpose (DO-005)?**

- **Recommendation:** Name: canonical profile, then manifest name, then directory name marked provisional. Purpose: canonical profile, then manifest description, and nothing else. README prose and provider descriptions are never a purpose source.
- **Why:** Matches the metadata package; inference is excluded.
- **Status:** Recommended
- **Feeds:** DOR-EX-B

**Q6. How is a conflict represented?**

- **Recommendation:** Status `conflicting` on the field plus a `conflicts` record with both values, their sources, first seen run, and any resolution. Counts appear in index status and in project details.
- **Why:** Visible conflicts are the requirement; a record makes them queryable.
- **Status:** Recommended
- **Feeds:** DOR-007

**Q7. Who resolves conflicts?**

- **Recommendation:** In phases 1 and 2 conflicts are reported, and resolution means fixing the owning source. The only explicit command is the registry `--prefer local|sheet` choice.
- **Why:** Interactive resolution is real design work with little payoff yet.
- **Status:** Recommended
- **Feeds:** DOR-003


## Data

**Q8. How is local-data isolation proven (DOR-004)?**

- **Recommendation:** A canary test sets a sentinel in every machine-local field and scans every export, log, and MCP shared payload for it.
- **Why:** A guarantee about absence is only credible if a test tries to find a leak.
- **Status:** Recommended
- **Feeds:** DOR-004

**Q9. What minimum provenance does a value need (DOR-002)?**

- **Recommendation:** Source type, source reference, actor (detector id and version, or human or process id), observation time, and revision when known.
- **Why:** Settled by the evidence and OKF actor conventions.
- **Status:** Settled
- **Feeds:** DOR-002


## Integration

**Q10. Provider descriptions versus repository purpose?**

- **Recommendation:** Provider text is kept as `provider_description`, a provider-owned observation. It is never promoted to purpose.
- **Why:** Different owners, different fields.
- **Status:** Recommended
- **Feeds:** DOR-EX-D


## Architecture

**Q11. Where is ownership enforced?**

- **Recommendation:** A single policy object offers `resolve(field, observations)` and `authorize_write(field, actor)`. Adapters write only through it.
- **Why:** One chokepoint is auditable; scattered checks are not.
- **Status:** Settled
- **Feeds:** DOR-003


## Acceptance

**Q12. How do the five examples become tests?**

- **Recommendation:** Each is an end-to-end scenario against fixtures and the fake Sheets gateway, tagged with its example id, plus the adapter conformance suite.
- **Why:** Worked examples already read as acceptance tests.
- **Status:** Recommended
- **Feeds:** DOR-012


## Ambiguity

**Q13. Who counts as a portfolio maintainer?**

- **Recommendation:** Vyasa cannot tell. Any value present in a portfolio column is treated as authoritative, so protecting the sheet is a sharing and access matter. The documentation says so.
- **Why:** Pretending Vyasa enforces who edits a sheet would be false assurance.
- **Status:** Decision needed
- **Feeds:** SEC-040

**Q14. What do shared timestamps mean (DO-009)?**

- **Recommendation:** Two columns with fixed meanings: Last Verified At and Last Synced At, defined in the shared-registry package.
- **Why:** Keeps one definition in one place.
- **Status:** Settled
- **Feeds:** shared-registry

## Decisions for you

- **Q3** — Which fields are portfolio-owned (DO-006)?
- **Q4** — Who owns lifecycle status (DO-007)?
- **Q13** — Who counts as a portfolio maintainer?
