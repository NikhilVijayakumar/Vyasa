# Security and Privacy Requirements — Vyasa (व्यास)

**Status:** Draft  
**Applies to:** Phase 1 — Local MCP; Phase 2 — Google Sheets registry; Phase 3 — Remote repository discovery

**Knowledge references**
- `knowledge/architecture/security-and-privacy.md` — threat model, trust boundaries, data classification, and the rationale behind these requirements
- `knowledge/concepts/evidence-and-provenance.md` — evidence content rules referenced by data minimization

Normative security and privacy requirements (`SEC-001`–`SEC-052`), their verification expectations, open decisions (`SP-001`–`SP-013`), and delivery sequence. Section headings follow the security model so each requirement can be read next to its rationale.

---

## 4. Data classification and minimization

### 4.2 Data minimization rules

**SEC-001.** Collect only metadata required by an approved detector or operation.

**SEC-002.** Do not copy source files, README contents, configuration contents, or other document bodies into SQLite merely to make them searchable.

**SEC-003.** Where file inspection is needed, process the relevant content in memory and persist only approved extracted values and evidence references.

**SEC-004.** Do not index file contents for general-purpose full-text search unless a separate requirement explicitly authorizes it.

**SEC-005.** Never persist raw credential values, authentication headers, OAuth tokens, private keys, or passwords in observations, evidence, scan results, or errors.

**SEC-006.** Avoid collecting Git commit messages, authors, email addresses, complete directory listings, and other incidental metadata unless a defined capability requires them.

**SEC-007.** Use repository-relative paths for evidence wherever possible. Absolute local paths remain machine-local and must not be exported.

**SEC-008.** Shared exports must use an explicit field allowlist. A field is not exportable merely because it exists in the database.

**SEC-009.** Unknown fields must not be exported automatically. A new field requires a classification and ownership decision before synchronization.

**SEC-010.** If a detector encounters a likely secret, it must not store the secret as evidence. It may report a generic finding such as `sensitive_value_detected`, provided the detection is reliable and useful.

---

## 5. Filesystem and repository security

### 5.1 Workspace boundaries

**SEC-011.** Canonicalize and validate filesystem paths before use.

**SEC-012.** Reject or safely skip paths that escape configured roots through traversal components, symlinks, junctions, or equivalent filesystem mechanisms.

**SEC-013.** Define and test symlink behaviour explicitly. The initial safe default is not to follow directory symlinks during recursive scanning.

**SEC-014.** Apply exclusions before expensive inspection. Exclude version-control internals, build output, dependency directories, caches, virtual environments, and configured sensitive locations unless a specific detector requires them.

**SEC-015.** Enforce configurable limits for file size, traversal depth, file count, and scan duration.

**SEC-016.** Do not follow arbitrary paths discovered inside repository content as permission to read outside the configured roots.

**SEC-017.** Revalidate paths at the point of access rather than relying exclusively on an earlier discovery result.

**SEC-018.** Handle filesystem errors without expanding the scan to broader locations.

---

## 6. Local database and machine security

### 6.1 Storage location and permissions

**SEC-019.** Restrict database, configuration, log, temporary-file, and backup permissions to the current user wherever the operating system supports it.

**SEC-020.** Do not store credentials in the SQLite database.

**SEC-021.** Do not expose the database through a network share or remote database service by default.

**SEC-022.** Apply the same privacy classification to database backups and exported diagnostics as to the underlying data.

**SEC-023.** Use parameterized SQL and validate all user-supplied filters and sort fields. Never construct SQL statements from untrusted identifiers or query text without validation.

**SEC-024.** Use transactions and integrity constraints to prevent partially applied index updates from appearing as complete results.

**SEC-025.** Ensure database migrations and recovery operations cannot silently drop project data.

---

## 7. MCP security

### 7.1 Local transport and client trust

**SEC-026.** Do not expose an HTTP listener or remote MCP endpoint by default.

**SEC-027.** Document the trusted-client configuration required to launch Vyasa.

**SEC-028.** Do not assume that every connected client is authorized to access every configured workspace. Workspace access must be limited by the configuration and permissions available to the Vyasa process.

**SEC-029.** If a future network transport is added, define authentication, authorization, TLS, origin/binding restrictions where relevant, and deployment security before enabling it.

### 7.2 Tool permissions

**SEC-030.** Validate every MCP argument against a defined schema and impose length, pagination, and result-size limits.

**SEC-031.** Do not let a tool argument override workspace roots, disable security exclusions, select arbitrary filesystem paths, or choose an unrestricted network destination.

**SEC-032.** Return only the requested fields and evidence necessary for the task. Avoid returning full internal database rows or environment details.

**SEC-033.** Keep error responses actionable but do not disclose credentials, absolute paths unnecessarily, internal stack traces, or sensitive provider responses.

**SEC-034.** MCP tools must not implicitly trigger remote discovery, Google Sheets synchronization, or other external side effects during ordinary queries.

---

## 8. Secret and credential management

### 8.1 Storage

**SEC-035.** Use the operating system's supported credential store where practical, or an approved secure local credential-storage mechanism.

**SEC-036.** Never commit tokens, OAuth credentials, refresh tokens, private keys, or service-account secrets to the Vyasa repository or any scanned project.

**SEC-037.** Do not put secrets in Google Sheets, project profiles, scanner configuration committed to Git, MCP arguments, logs, or diagnostic bundles.

**SEC-038.** Environment variables may be used as a controlled deployment mechanism when needed, but must not be treated as secure persistent storage. Do not log their values or include them in diagnostics.

**SEC-039.** Avoid printing secrets in exception messages, HTTP request diagnostics, URLs, or debug output.

---

## 9. Google Sheets security — Phase 2

### 9.1 Access control

**SEC-040.** The registry must be shared only with intended users or service identities.

**SEC-041.** Prefer the narrowest practical authorization model for the chosen integration, such as access restricted to a designated spreadsheet.

**SEC-042.** Never make the registry public merely to simplify integration.

**SEC-043.** Document who can read and edit each shared registry and how access is revoked.

---

## 10. Remote repository security — Phase 3

### 10.1 Scope restriction

**SEC-044.** Require explicit configuration of GitHub users/organizations and Bitbucket workspaces to inspect.

**SEC-045.** Do not enumerate unrelated accounts or organizations using credentials merely because those credentials technically permit it.

**SEC-046.** Apply inclusion and exclusion rules before inspecting repository contents.

**SEC-047.** Do not follow arbitrary URLs found in repository metadata as trusted destinations.

---

## 12. Configuration and secure defaults

**SEC-048.** An absent or malformed security setting must not silently broaden access.

**SEC-049.** Configuration changes must be validated before becoming active.

**SEC-050.** Diagnostics must not print secret values or dump the complete configuration indiscriminately.

**SEC-051.** Phase 2 and Phase 3 integrations must be disabled until explicitly configured and authorized.

**SEC-052.** A provider integration failure must not silently trigger an alternative access mechanism with broader permissions.

---

## 13. Security testing and verification

Security requirements must be covered by automated tests where practical, supplemented by manual review.

### 13.1 Filesystem tests

- Paths attempting to escape configured roots.
- Symlink and junction traversal.
- Oversized files and excessive directory depth.
- Unreadable files and interrupted scans.
- Files changing during scanning.
- Malformed Git metadata and remote URLs.
- Repositories containing secret-like values in documentation or configuration files.
- Proof that ordinary scans do not modify repository contents.

### 13.2 MCP tests

- Invalid argument types and oversized requests.
- Path injection and attempts to override configured roots.
- Attempts to request unsupported tools or fields.
- Excessive result sets and pagination boundary cases.
- Verification that query tools do not trigger external synchronization.
- Error-response checks for secret and path leakage.
- Verification that repository content is returned as data, not executed.

### 13.3 Storage and privacy tests

- Database permissions and default storage location.
- Absence of credentials in the database and logs.
- Export allowlist enforcement.
- No raw document bodies stored by default.
- Correct deletion and retention behaviour.
- Migration and recovery integrity.
- Stale and inaccessible data clearly identified.

### 13.4 Integration tests

- Google authentication and spreadsheet permission failures.
- Attempts to share or write outside the authorized registry.
- Conflicting human-managed values.
- Partial synchronization and retry behaviour.
- Provider pagination and rate limiting.
- Remote repository access denied by scope.
- Credential expiry and revocation.
- Malicious or malformed API responses.
- Failure without unintended cloning, writes, or data export.

### 13.5 Release gate

A release must not be considered security-ready if any of the following remain unresolved:

- Secrets can enter logs, shared exports, or persistent observations.
- Configured filesystem boundaries can be bypassed.
- Ordinary scan or query operations modify repositories.
- Failed synchronization can silently overwrite human-managed data.
- External integrations are enabled without explicit configuration.
- Security-sensitive operations have no clear outcome or failure report.

---

## 15. Security requirements summary

| ID range | Area | Required outcome |
|---|---|---|
| SEC-001–010 | Data minimization | Collect and share only approved, necessary metadata |
| SEC-011–018 | Filesystem | Respect configured boundaries and avoid unsafe traversal |
| SEC-019–025 | Local storage | Protect the index, credentials, queries, and data integrity |
| SEC-026–034 | MCP | Limit client exposure, validate requests, and prevent implicit side effects |
| SEC-035–039 | Credentials | Store and manage credentials securely |
| SEC-040–043 | Google Sheets | Restrict access and synchronize safely |
| SEC-044–047 | Remote repositories | Restrict discovery scope and handle remote evidence honestly |
| SEC-048–052 | Configuration | Fail safely and require explicit integration enablement |

These requirements are proposed acceptance criteria. They should be mapped to implementation tests and reviewed alongside the functional and non-functional requirements before the first release.

---

## 16. Open decisions

| ID | Decision | Proposed direction |
|---|---|---|
| SP-001 | Should local SQLite use application-level encryption? | Start with OS permissions and disk encryption; reassess threat model |
| SP-002 | Which OS credential stores must be supported? | Prefer native secure credential storage where available |
| SP-003 | What are the default scan limits? | Establish conservative configurable limits and benchmark |
| SP-004 | Which symlink behaviours are supported? | Do not follow directory symlinks by default |
| SP-005 | What is the retention period for scan history and logs? | Define explicit configurable defaults |
| SP-006 | Which fields are approved for Sheets export? | Maintain a versioned explicit allowlist |
| SP-007 | Which Google authentication mechanism is selected? | Choose the least-privilege approach supported by the deployment |
| SP-008 | Which GitHub and Bitbucket scopes are required? | Read-only and limited to configured repository scopes |
| SP-009 | Is a future network-based MCP transport required? | No for the initial release |
| SP-010 | Is draft profile generation enabled by default? | No; opt-in only |
| SP-011 | Should likely secret detection be included in Phase 1? | Consider lightweight detection that never persists matched values |
| SP-012 | How are sensitive internal repository URLs classified? | Local by default; explicit approval for shared export |
| SP-013 | Is a formal threat-model review required before Phase 2 and Phase 3? | Yes, before enabling each new external trust boundary |

---

## 17. Implementation sequence

### Phase 1 — Local security foundation

- Implement filesystem boundary checks and exclusions.
- Keep scanning deterministic and read-only.
- Define metadata and evidence sensitivity rules.
- Secure the local database, configuration, logs, and backups.
- Validate MCP schemas and constrain tool capabilities.
- Add security regression tests.
- Verify that no external service is contacted during ordinary local queries.

### Phase 2 — Shared registry security

- Finalize export classifications and field ownership.
- Choose the authentication model and minimum required permissions.
- Implement explicit sync, dry-run, conflict handling, and failure reporting.
- Validate all spreadsheet data as untrusted input.
- Test permissions, partial failure, credential expiry, and data leakage.

### Phase 3 — Remote API security

- Define repository scopes and provider permissions.
- Implement secure credential handling and bounded API clients.
- Enforce pagination, size, timeout, and rate limits.
- Preserve provenance and distinguish inaccessible repositories from deleted ones.
- Test malformed responses, access denial, incomplete discovery, and credential revocation.
