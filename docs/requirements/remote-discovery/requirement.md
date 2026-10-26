# Requirement: Remote Repository Discovery and Inspection

- **Package:** `docs/requirements/remote-discovery/`
- **Status:** Grilled — recommended answers await your confirmation
- **Roadmap phase:** P3
- **Owns:** FR-018, FR-019, NFR-022, NFR-036, NFR-037
- **Grill log:** [grill-log.md](grill-log.md)
- **Diagrams:** [diagrams.md](diagrams.md)
- **Features:** [fr-018-remote-repository-discovery.feature](features/fr-018-remote-repository-discovery.feature), [fr-019-remote-metadata-inspection.feature](features/fr-019-remote-metadata-inspection.feature)

## Knowledge References

Checked with the `knowledge-first` skill before writing.

- `knowledge/architecture/remote-repositories.md` — scope, adapters, pagination, caching, failure handling, MCP operations
- `knowledge/architecture/data-model.md` — remote repository observations and access status (§15)
- `knowledge/concepts/project-identity.md` — provider identifiers as aliases; forks stay distinct
- `knowledge/concepts/evidence-and-provenance.md` — remote evidence names the repository, path, and revision
- `knowledge/architecture/c4-system-views.md` — provider adapters and external APIs

## Intent

Vyasa can see repositories that are not cloned on this machine, from GitHub and Bitbucket Cloud, inside scopes the user configured. It lists them and reads a few selected files through the provider API, never cloning, and reports honestly when it saw only part of the picture.

## Scope

- **Included:**
  - Configured scopes, pagination, and rate-limit behaviour.
  - Selected-file inspection pinned to a revision.
  - Reconciling remote and local observations.
  - Failure isolation from local operation.
- **Excluded:**
  - Cloning or checking out repositories.
  - Provider write operations.
  - Continuous polling.
  - Self-hosted Bitbucket.
- **Deferred:**
  - GitHub Enterprise Server base URLs.
  - Scheduled discovery.
  - Webhooks.

## Requirements

### FR-018 — Remote Repository Discovery (P3)

Vyasa MUST support discovering eligible repositories through configured GitHub and Bitbucket Cloud APIs.

### FR-019 — Remote Metadata Inspection (P3)

Vyasa MUST inspect supported remote repository metadata through provider APIs when access and provider capabilities permit.

## Expected Behaviour

Observable behaviour is specified as Gherkin scenarios in `features/`. Scenarios tagged `@proposed` come from grill recommendations and become normative when the recommendation is confirmed.

- Configured scopes are enumerated completely or the shortfall is reported (`fr-018`).
- Authentication failure is an access failure, never an empty success (`fr-018` S6).
- Selected files are read at a known revision and kept distinguishable from local observations (`fr-019`).

## Constraints

- Read-only credentials limited to configured scopes (NFR-022).
- Bounded retries, request size, and duration (NFR-036).
- Provider failure never affects local scanning or queries (NFR-037).
- Private repository data stays out of shared exports unless a scope opts in.

## Acceptance Expectations

- Phase 3 criteria 1 to 9 in `phase-acceptance-criteria.md`.
- Adapter tests run against recorded or fake provider responses; live tests are gated by an environment variable.
- A test proves no subprocess or Git clone is started during discovery.

## Open Decisions

Accepted as open until you confirm the recommended direction in the grill log.

| Decision | Recommended direction | Grill |
|---|---|---|
| DFR-011 / RR-003 | Scopes are explicit lists of users, organizations, and workspaces; archived repositories are listed, not inspected. | Q2 |
| RR-001/002 | Read-only fine-grained tokens; verify Bitbucket's current token model at build time. | Q4 |
| NFD-012 / RR-015 | Honour provider rate-limit headers; at most three retries; then partial. | Q5 |
| DFR-012 | Remote disappearance is only recorded after two complete listings; auth errors never imply deletion. | Q8 |
| sharing | Remote-derived records are not exported to the registry unless the scope sets share_to_registry. | Q10 |

## Delivery

Proposed OpenSpec changes, each a set of vertical slices (`knowledge/practices/vertical-slices.md`):

- `be-provider-contract`: adapter protocol, domain errors, fake provider.
- `be-github-list`: list repositories for a scope with pagination and completeness.
- `be-remote-inspect`: pinned selected-file inspection through the existing detectors.
- `be-bitbucket-list`: the same contract for Bitbucket Cloud.
- `be-remote-reconcile`: matching with local records and the missing-remote rule.
