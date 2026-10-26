# Grill Log: Remote Repository Discovery and Inspection

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 2 | 1 |
| Behaviour | 5 | 2 |
| Data | 2 | 1 |
| Integration | 1 | 0 |
| Architecture | 2 | 0 |
| Acceptance | 1 | 0 |
| Ambiguity | 2 | 0 |

## Intent

**Q1. Which question does remote discovery answer?**

- **Recommendation:** What exists in my accounts that is not on this machine, so work is not rebuilt because a repository was never cloned.
- **Why:** It extends the same 'help agents see what exists' goal beyond the local disk.
- **Status:** Settled
- **Feeds:** FR-018


## Scope

**Q2. What defines a scope (DFR-011, RR-003)?**

- **Recommendation:** An explicit list: GitHub users and organizations, Bitbucket workspaces, with optional name filters. Nothing is discovered outside the list. Archived repositories are recorded and not inspected by default.
- **Why:** Explicit scopes bound both exposure and API cost.
- **Status:** Decision needed
- **Feeds:** FR-018 S1..S3

**Q3. Which files are read remotely (RR-006)?**

- **Recommendation:** Metadata only by default. When inspection is enabled: README, the canonical profile, root manifests from the detector inventory, and the OpenSpec config, at most 12 files and 256 KiB each, pinned to the default branch commit.
- **Why:** The smallest set that feeds the existing detectors.
- **Status:** Recommended
- **Feeds:** FR-019 S2, S3


## Behaviour

**Q4. Which credentials (RR-001, RR-002)?**

- **Recommendation:** GitHub: a fine-grained token with read-only Metadata and Contents on selected repositories. Bitbucket Cloud: a repository or workspace access token with read scope. Atlassian is retiring app passwords, so confirm the current model when building. Credentials come from the OS keyring or environment, never the config file.
- **Why:** Least privilege per provider; the Bitbucket detail is the part most likely to change.
- **Status:** Decision needed
- **Feeds:** FR-018 S2, S3

**Q5. How are limits handled (NFD-012, RR-015)?**

- **Recommendation:** Honour provider rate-limit headers and Retry-After. At most three retries with capped backoff. Beyond that the run is `partial` and coverage is marked incomplete.
- **Why:** Persistence beyond the provider's guidance risks blocks.
- **Status:** Recommended
- **Feeds:** FR-018 S5

**Q6. What does a failed page mean?**

- **Recommendation:** Results from earlier pages are kept, the scope is marked incomplete, and nothing is inferred about repositories on later pages.
- **Why:** Incomplete listings must never read as complete.
- **Status:** Recommended
- **Feeds:** FR-018 S4

**Q7. What does an authentication failure return?**

- **Recommendation:** An access failure with a category, never an empty successful result. Previously discovered records stay and are marked with the failure.
- **Why:** FR-018 S6 and the rule that absence is not deletion.
- **Status:** Settled
- **Feeds:** FR-018 S6

**Q8. When is a repository considered gone (DFR-012)?**

- **Recommendation:** Only after two consecutive complete, successful listings omit it. It becomes `not_found_remote` and is never deleted. Authentication or partial failures never count.
- **Why:** A single missed listing is common; a deletion claim must be hard to make.
- **Status:** Decision needed
- **Feeds:** FR-019 S4


## Data

**Q9. What is stored?**

- **Recommendation:** Provider repository fields, and extracted observations with evidence (repository, path, blob SHA, revision). No file bodies.
- **Why:** Same minimization rule as local scanning.
- **Status:** Settled
- **Feeds:** FR-019 S5

**Q10. Do private repositories reach the shared registry?**

- **Recommendation:** Not by default. A scope must set `share_to_registry = true` for its records to be exported, and then only allowlisted fields.
- **Why:** A private repository's name can be sensitive; sharing should be a deliberate act.
- **Status:** Decision needed
- **Feeds:** NFR-018


## Integration

**Q11. GitHub Enterprise or self-hosted Bitbucket?**

- **Recommendation:** Out of scope for phase 3. A configurable GitHub base URL can follow later.
- **Why:** Documented scope is cloud APIs only.
- **Status:** Recommended
- **Feeds:** FR-018


## Architecture

**Q12. Which HTTP client and contract?**

- **Recommendation:** A provider adapter protocol (`list_repositories`, `get_file`) that maps errors to domain errors: AuthFailure, NotFound, RateLimited, Transient. HTTP through `httpx` in an optional extra, with timeouts and a streaming size cap.
- **Why:** A protocol lets a fake provider drive the tests.
- **Status:** Recommended
- **Feeds:** NFR-036

**Q13. How is the no-clone rule enforced?**

- **Recommendation:** Adapters contain no Git calls, and a test fails if a subprocess is started during discovery.
- **Why:** The rule is architectural, so it needs a structural test.
- **Status:** Recommended
- **Feeds:** FR-018 S7


## Acceptance

**Q14. How are adapters tested?**

- **Recommendation:** Recorded response fixtures and a small local fake server cover pagination, rate limits, auth failure, malformed bodies, and oversized responses. Live tests run only when an environment variable provides scoped credentials.
- **Why:** Deterministic and offline, with live checks opt-in.
- **Status:** Recommended
- **Feeds:** Phase 3 criterion 9


## Ambiguity

**Q15. Can remote discovery run before a local scan?**

- **Recommendation:** Yes. Remote-only projects get their identity from the provider id and normalized remote.
- **Why:** The two sources are independent and reconcile through identity.
- **Status:** Settled
- **Feeds:** FR-019 S6

**Q16. Is remote content trusted?**

- **Recommendation:** No. Descriptions, READMEs, and file bodies are untrusted data, size-capped and sanitized like local content.
- **Why:** Remote repositories are where hostile text is most likely.
- **Status:** Settled
- **Feeds:** NFR-020

## Decisions for you

- **Q2** — What defines a scope (DFR-011, RR-003)?
- **Q4** — Which credentials (RR-001, RR-002)?
- **Q8** — When is a repository considered gone (DFR-012)?
- **Q10** — Do private repositories reach the shared registry?
