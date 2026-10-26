# Phase Acceptance Criteria — Vyasa (व्यास)

**Status:** Draft

**Knowledge references**
- `knowledge/product/scope-and-roadmap.md` — what each phase includes, excludes, and delivers

A phase is complete only when every criterion below is verified by an executed check. Use the `phase-gate-verification` skill.

---

## Phase 1 — Local Workspace Intelligence

Phase 1 is complete when:

1. A user can configure multiple workspace roots and exclusions.
2. Supported projects are discovered reproducibly.
3. Metadata is extracted only through documented rules and recognized evidence.
4. Unknown fields are not fabricated.
5. Queries return matching project records with useful evidence references.
6. A project can be queried even when the user is working in a different repository.
7. Scan failures are reported without unnecessarily losing previously valid index data.
8. Repeated scans do not create duplicate projects merely because their paths or metadata ordering changed.
9. Index refresh does not overwrite human-maintained project information.
10. The MCP service works without external services.
11. Tests verify normal operation, error cases, identity behaviour, and supported detection rules.
12. Setup and operational instructions are sufficient for another developer to run the service.

---

## Phase 2 — Shared Project Registry

Phase 2 is complete when:

1. Project metadata can be synchronized with the agreed workbook.
2. A second device can retrieve shared records without cloning every repository.
3. Human-managed registry values are preserved according to the field ownership rules.
4. Local paths, credentials, and machine-specific configuration are never exported.
5. Failed synchronization does not invalidate the local index.
6. Conflicts and partial failures are observable and recoverable.
7. Records can be matched consistently across devices.
8. Tests demonstrate correct behaviour for new, existing, changed, and conflicting records.

---

## Phase 3 — Remote Repository Discovery

Phase 3 is complete when:

1. Configured repositories can be discovered through the supported APIs.
2. Remote metadata can be retrieved without cloning or checking out repositories.
3. Supported files can be inspected through provider APIs where access permits.
4. Pagination and common API failures are handled predictably.
5. Remote projects can be matched to existing project records using documented rules.
6. Ambiguous matches and duplicate candidates are flagged for review.
7. Credentials are never written to shared registry records.
8. Inaccessible repositories are distinguished from confirmed absence.
9. Tests cover public access, authenticated access, pagination, permissions, and rate limits.
