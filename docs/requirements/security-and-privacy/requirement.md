# Requirement: Security and Privacy

- **Package:** `docs/requirements/security-and-privacy/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P1–P3
- **Owns:** NFR-016, NFR-017, NFR-019, NFR-020, SEC-001–SEC-052
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [data-and-credentials.feature](features/data-and-credentials.feature), [filesystem-boundaries.feature](features/filesystem-boundaries.feature), [mcp-boundary.feature](features/mcp-boundary.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/architecture/security-and-privacy.md` — threat model, trust boundaries, classification, incident response
- `knowledge/architecture/system-architecture.md` — security architecture (§15)
- `knowledge/concepts/field-ownership.md` — machine-local data never leaves the device
- `knowledge/architecture/c4-system-views.md` — containers across the trust boundaries

## Intent

Vyasa reads proprietary repositories and later talks to the cloud, so security is a property of the design, not a feature. It reads only what it is told to, stores only what it needs, treats all repository and provider content as untrusted, keeps secrets out of every store, and never changes a repository during an ordinary scan.

## Scope

- **Included:**
  - Filesystem and repository boundaries, read-only operation, and draft-write control.
  - Local storage, MCP, credential, Sheets, and provider security.
  - Data classification and minimization, logging, and safe defaults.
  - Security testing and the release gate.
- **Excluded:**
  - Application-level database encryption (revisit later).
  - A network MCP transport.
  - Secret scanning as a product feature.
- **Deferred:**
  - A formal threat-model review before phase 2 and again before phase 3.
  - Network transport security if one is ever added.

## Requirements

The full normative text stays in `docs/requirements/security-and-privacy-requirements.md`
(`SEC-001` to `SEC-052`, verification expectations, open decisions, and sequence). This package owns the
non-functional security requirements and turns the testable ones into scenarios.

| Requirement | Statement |
|---|---|
| NFR-016 | Repositories are accessed read-only. |
| NFR-017 | Credentials are protected throughout their lifecycle. |
| NFR-019 | Filesystem access stays within configured boundaries. |
| NFR-020 | Repository content is untrusted input and is never executed. |

| SEC range | Area |
|---|---|
| SEC-001 to 010 | Data minimization |
| SEC-011 to 018 | Filesystem |
| SEC-019 to 025 | Local storage |
| SEC-026 to 034 | MCP |
| SEC-035 to 039 | Credentials |
| SEC-040 to 043 | Google Sheets |
| SEC-044 to 047 | Remote repositories |
| SEC-048 to 052 | Configuration |

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- Boundaries hold under hostile paths and content (`filesystem-boundaries.feature`).
- The MCP surface is validated, bounded, and free of side effects (`mcp-boundary.feature`).
- Data and credentials stay where they are allowed (`data-and-credentials.feature`).

## Constraints

- Security-sensitive settings are explicit and validated; absence never broadens access (SEC-048).
- Phase 2 and 3 integrations are off until configured (SEC-051).
- A failing integration never silently falls back to broader access (SEC-052).

## Acceptance Expectations

- Phase 1 to 3 gates in `phase-acceptance-criteria.md`, and the release gate in the security requirements §13.5.
- Each gate item is an automated check: tree hash, symlink escape, socket block, canary, redaction.
- `secrets-scan` and `sca-audit` run on every change.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| SP-001 | No application-level encryption in phase 1; rely on OS permissions and disk encryption. | Q3 |
| SP-002 | OS credential store through an optional keyring extra; environment variables as a controlled fallback. | Q8 |
| SP-003 | Defaults: depth 8 (owner, 2026-10-27), 1 MiB per file, 5,000 inventory entries, 60 s per project. | Q13 |
| SP-011 | No secret scanning feature; redact on output only. | Q2 |
| SP-012 | Only public-host remote URLs are shareable by default. | Q6 |
| SP-013 | Threat-model review before phases 2 and 3. | Q11 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-boundary-tests`: symlink, traversal, and tree-hash tests as the first suite.
- `be-redaction`: logging and error redaction with the token patterns.
- `be-no-network-guard`: socket-blocking test fixture for phase 1.
- `be-security-gate`: the release gate as a single command.
