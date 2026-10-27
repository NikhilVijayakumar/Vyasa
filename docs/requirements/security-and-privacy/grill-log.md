# Grill Log: Security and Privacy

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 2 | 2 |
| Behaviour | 2 | 0 |
| Data | 2 | 1 |
| Integration | 2 | 1 |
| Architecture | 2 | 1 |
| Acceptance | 1 | 0 |
| Ambiguity | 2 | 1 |

## Intent

**Q1. What are the top threats, in order?**

- **Recommendation:** (1) Repository content that executes code or injects instructions into agents through returned text. (2) Path escape through traversal or symlinks. (3) Secrets leaking into the index, logs, or the sheet. (4) Over-broad credentials. (5) Hidden network side effects.
- **Why:** Ordering drives where tests and reviews go first.
- **Status:** Recommended
- **Feeds:** SEC-011, SEC-016, SEC-034


## Scope

**Q2. Does phase 1 scan for secrets (SP-011)?**

- **Recommendation:** No. Vyasa never stores matched text, redacts known token shapes on output, and strips credentials from URLs. A secret scanner would be a separate product.
- **Why:** The goal is not to leak secrets, not to find them.
- **Status:** Decision needed
- **Feeds:** SEC-005, SEC-010

**Q3. Encrypt the database (SP-001)?**

- **Recommendation:** No application-level encryption in phase 1. Use OS file permissions and disk encryption. Credentials are never in the database. Revisit if the index ever holds more sensitive content.
- **Why:** Encryption adds key management for little gain when the data is non-secret metadata.
- **Status:** Decision needed
- **Feeds:** SEC-019, SEC-020


## Behaviour

**Q4. How is prompt injection through returned text limited?**

- **Recommendation:** Repository-derived strings are typed with length caps, control and bidirectional characters removed, never merged into tool descriptions, and never returned as raw document bodies. Documentation states they are untrusted.
- **Why:** Vyasa cannot make text safe, only keep it inert and bounded.
- **Status:** Recommended
- **Feeds:** NFR-020

**Q5. What does logging do?**

- **Recommendation:** JSON lines through the standard library to a rotating file (five files of 1 MiB) and to stderr, with a redaction filter for URL credentials, Authorization headers, and known token shapes (`ghp_`, `github_pat_`, `xox`, AKIA keys, private key blocks, Google refresh tokens). Repository-relative paths are preferred; absolute paths appear only in local logs.
- **Why:** Redaction at the logging boundary covers every call site.
- **Status:** Recommended
- **Feeds:** SEC-039, NFR-032


## Data

**Q6. Which remote URLs may be shared (SP-012)?**

- **Recommendation:** Normalized URLs on github.com and bitbucket.org by default; any other host stays local unless a project is explicitly approved.
- **Why:** Internal hosts reveal infrastructure.
- **Status:** Decision needed
- **Feeds:** SEC-007, SEC-008

**Q7. What is retained and for how long (SP-005)?**

- **Recommendation:** Logs: 14 days or five files. Scan history: 50 runs or 90 days. Observations: current plus previous value.
- **Why:** Bounded retention limits what a leak could expose.
- **Status:** Recommended
- **Feeds:** SEC-022


## Integration

**Q8. Where do credentials live (SP-002)?**

- **Recommendation:** The OS credential store through the optional `keyring` extra. Environment variables are allowed as a controlled fallback and never logged. A 0600 file outside any repository is allowed only by explicit choice. Never in config, the database, or a repository.
- **Why:** Uses what the platform already protects.
- **Status:** Decision needed
- **Feeds:** SEC-035..SEC-039

**Q9. What scopes do providers need (SP-008)?**

- **Recommendation:** GitHub: read-only Metadata and Contents on selected repositories. Bitbucket: repositories read. Sheets: access to one designated spreadsheet via a service account. Verify current provider models when building.
- **Why:** Least privilege per integration.
- **Status:** Recommended
- **Feeds:** SEC-041, SEC-044


## Architecture

**Q10. How is 'no network in phase 1' enforced?**

- **Recommendation:** A test fixture that makes socket connections fail runs the phase 1 suite; the production package imports network libraries only inside optional extras.
- **Why:** A claim about absence needs a test that would catch presence.
- **Status:** Recommended
- **Feeds:** SEC-034, SEC-051

**Q11. When is the threat model reviewed (SP-013)?**

- **Recommendation:** Before enabling each new trust boundary, phase 2 and phase 3, using `mcp-server-review` and `code-review-security`, and recorded as a Decision concept.
- **Why:** Each integration changes who can reach what.
- **Status:** Decision needed
- **Feeds:** SP-013


## Acceptance

**Q12. What is the release gate in executable form?**

- **Recommendation:** One command running: tree-hash read-only check, symlink and traversal fixtures, socket-block run, the export canary, log and error redaction tests, malicious MCP argument cases, `secrets-scan`, and `sca-audit`.
- **Why:** The gate list in the security requirements becomes a script that either passes or fails.
- **Status:** Recommended
- **Feeds:** security requirements §13.5


## Ambiguity

**Q13. What are the default scan limits (SP-003)?**

- **Recommendation:** Depth 8, 1 MiB per file (256 KiB for profiles), 5,000 inventory entries per project, 60 s per project, all configurable. A limit reached means skipped, never absent.
- **Why:** Conservative starting points to be benchmarked.
- **Status:** Decision needed
- **Feeds:** SEC-015

**Q14. Will a network transport ever be needed (SP-009)?**

- **Recommendation:** Not initially. Adding one needs authentication, TLS, origin checks, and a new review before merging.
- **Why:** Documented so it cannot appear casually.
- **Status:** Settled
- **Feeds:** SEC-029

## Decisions for you

- **Q2** — Does phase 1 scan for secrets (SP-011)?
- **Q3** — Encrypt the database (SP-001)?
- **Q6** — Which remote URLs may be shared (SP-012)?
- **Q8** — Where do credentials live (SP-002)?
- **Q11** — When is the threat model reviewed (SP-013)?
- **Q13** — What are the default scan limits (SP-003)?
