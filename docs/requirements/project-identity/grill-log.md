# Grill Log: Project Identity and Review Candidates

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 2 | 1 |
| Behaviour | 5 | 2 |
| Data | 2 | 0 |
| Integration | 1 | 0 |
| Architecture | 3 | 1 |
| Acceptance | 2 | 1 |
| Ambiguity | 1 | 0 |

## Intent

**Q1. What breaks if identity is wrong?**

- **Recommendation:** Everything downstream: duplicate projects on rescan, lost human-managed values on sync, wrong matches between devices and remotes. It is the dependency of phases 2 and 3.
- **Why:** Raising its priority now is cheaper than migrating IDs after data exists.
- **Status:** Settled
- **Feeds:** NFR-004


## Scope

**Q2. How are remote URLs normalized (DFR-005)?**

- **Recommendation:** Drop scheme, userinfo, default port, a trailing `.git` and slash; convert `git@host:org/repo` and `https://host/org/repo` to `host/org/repo`. Lowercase the whole identity for github.com and bitbucket.org; keep path case for unknown hosts. Use the remote named `origin`; if absent and exactly one remote exists use it; otherwise the identity is provisional.
- **Why:** These providers are case-insensitive; unknown hosts may not be. A fixed remote choice keeps results reproducible.
- **Status:** Decision needed
- **Feeds:** FR-003 S1; DFR-005

**Q3. Are forks and mirrors the same project?**

- **Recommendation:** No. A different remote is a different repository. An `upstream` remote that differs from `origin` is recorded as a related identity, not merged. A `fork_of` relationship needs provider evidence in phase 3.
- **Why:** Merging forks would destroy the very distinction people search for.
- **Status:** Recommended
- **Feeds:** FR-003 S6


## Behaviour

**Q4. How is the project ID built (DO-004, DM-001)?**

- **Recommendation:** `prj_` plus 16 hex characters of SHA-256 over `v1|` and the first strongest evidence at creation. The ID is stored and never recomputed. Later evidence (renamed remote, provider id) is added as aliases that resolve to the same ID. Repositories use `rep_` the same way. Collisions fail loudly with `INDEX_INCONSISTENT`.
- **Why:** A stored ID survives a remote rename, which a pure function of the remote could not.
- **Status:** Decision needed
- **Feeds:** FR-003 S1, S3

**Q5. What identity does a repository without a remote get?**

- **Recommendation:** A repository with no usable remote (none, several with no `origin`, a local-path remote, or an unreadable or pointer-file Git entry) is a local project: a provisional identity matched by its checkout path. No Git program is run. A move creates a new project and leaves the old one missing; nothing is linked by name. Confirmed by the owner 2026-10-27; root-commit identity is dropped permanently.
- **Why:** Running Git inside an untrusted repository is an execution risk, and the only gain is matching remote-less repositories across devices, which phase 1 does not do. Moving a remote-less repository is rare; two records are honest and recoverable.
- **Status:** Settled
- **Feeds:** FR-003 S2

**Q6. In what order is an existing project looked up on rediscovery?**

- **Recommendation:** Normalized remote alias, then known checkout path, then nothing further (a repository without a remote is matched by path alone). A remote that changed at a known path is a remote-changed event on the same project, not a new one.
- **Why:** Prevents duplicates on rename or transfer while still detecting real change.
- **Status:** Recommended
- **Feeds:** FR-003 S3

**Q7. Two directories share one remote. What happens (S4)?**

- **Recommendation:** One repository, two checkouts. A primary checkout is chosen deterministically by configured root order then path. The duplicate checkout is flagged as a review candidate.
- **Why:** Matches the data model, which separates repository from checkout.
- **Status:** Recommended
- **Feeds:** FR-003 S4; FR-020 S1

**Q8. Evidence disagrees: path says one project, remote another.**

- **Recommendation:** Create nothing silently. Record the candidate as `identity_unresolved`, keep both pieces of evidence, and surface it for review.
- **Why:** A wrong merge is worse than a visible open question.
- **Status:** Recommended
- **Feeds:** FR-003 S5


## Data

**Q9. How are identity changes recorded?**

- **Recommendation:** An `identity_events` log: created, alias_added, remote_changed, flagged, resolved. Each row holds evidence and run id.
- **Why:** The data model requires an audit trail for identity changes.
- **Status:** Settled
- **Feeds:** NFR-004

**Q10. What if the remote URL contains a token?**

- **Recommendation:** Strip userinfo before normalizing, never persist the raw URL, and redact it in logs.
- **Why:** Security requirements forbid credentials in observations, evidence, and errors.
- **Status:** Settled
- **Feeds:** SEC-005


## Integration

**Q11. How do provider repository IDs fit in later?**

- **Recommendation:** As aliases of kind `provider:github:<id>` or `provider:bitbucket:<uuid>`; they resolve renames and transfers.
- **Why:** Gives phase 3 a stable join key without changing the ID rule.
- **Status:** Recommended
- **Feeds:** remote-discovery


## Architecture

**Q12. Where does normalization live?**

- **Recommendation:** A pure domain function `normalize_remote(url) -> RemoteIdentity | None`, no I/O. File URLs and local paths return `None` and count as no remote.
- **Why:** A pure function is exhaustively testable and cannot be bypassed by an adapter.
- **Status:** Recommended
- **Feeds:** NFR-004

**Q13. What are the duplicate-candidate rules (FR-020)?**

- **Recommendation:** (a) two checkouts of one repository; (b) two projects with the same normalized remote, treated as an integrity alert; (c) dropped together with root-commit identity. Names alone never qualify. Each flag carries a rule id, evidence, and a confidence tier.
- **Why:** Deterministic rules are explainable, which FR-020 S5 requires.
- **Status:** Recommended
- **Feeds:** FR-020 S1, S5

**Q14. What makes a project an obsolescence candidate?**

- **Recommendation:** Only declared state: lifecycle `deprecated` or `archived` in the canonical profile, or a provider archived flag. Time-based indicators (for example no commits for N days) are opt-in and off by default. An unscanned or inaccessible project is never flagged for that reason.
- **Why:** Inactivity is not obsolescence, and an unverifiable state must not read as a verdict.
- **Status:** Decision needed
- **Feeds:** FR-020 S2, S3


## Acceptance

**Q15. Where is a reviewer's decision stored?**

- **Recommendation:** In Vyasa's own index as candidate status: open, dismissed, confirmed. This is generated state and never touches a repository. Syncing decisions is a phase 2 question.
- **Why:** FR-020 forbids automatic destructive action; a local status is the least invasive way to record a human choice.
- **Status:** Decision needed
- **Feeds:** FR-020 S4

**Q16. How is identity verified?**

- **Recommendation:** Real `git init` fixtures in `tmp_path`: rename, move, clone twice, no remote, ssh vs https vs `.git` forms, rewritten remote, embedded token. A parametrized table drives the normalization function.
- **Why:** Fixtures with real repositories catch what mocks of Git config would miss.
- **Status:** Recommended
- **Feeds:** Phase 1 criterion 8


## Ambiguity

**Q17. What if history is rewritten or the clone is shallow?**

- **Recommendation:** No root commit is read, so rewritten history and shallow clones do not affect identity. A changed remote at a known path is an alias update, not a new project.
- **Why:** These are the common ways a fallback identity breaks.
- **Status:** Recommended
- **Feeds:** FR-003 S2

## Decisions for you

None open. Q2, Q4, Q5, Q14 and Q15 were confirmed by the owner on 2026-10-27. Q15: a reviewer's decision is always local and is never synchronized or shown in Google Sheets.
