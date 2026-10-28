# Architecture Decision Record: be-repeated-dependency-declaration

## 1. Decision Status

- **Status:** Not Required
- **Date:** 2026-10-29
- **OpenSpec Change ID:** `be-repeated-dependency-declaration`
- **Decision owners:** maintainer
- **Related artifacts:** `proposal.md`, `design.md`, `specs/framework-detection/spec.md`

## 2. Decision Checkpoint

- [ ] **New decision required:** This change introduces or alters a significant architectural decision.
- [x] **Existing decision applies:** An existing ADR governs this decision.
- [ ] **No new ADR required:** The change does not introduce a significant architectural decision.

### Rationale

The durable rules already exist and are unchanged by this work:

- `knowledge/decisions/framework-detection-from-manifests.md` fixes that dependencies are recorded with name, constraint, and scope, that scopes are never merged, and — clarified while making this fix — that the index keeps one dependency row per name and scope, so a package declared twice in one scope is stored once.
- `knowledge/decisions/local-first-sqlite-index.md` and `knowledge/decisions/index-lifecycle-and-single-writer.md` fix where dependencies live and that the scan is the only writer.

The implementation had drifted from the rule the table already encoded (migration 0009's primary key), so this work restores conformance rather than deciding anything new. No new `type: Decision` concept is warranted; the clarification was added to the existing concept instead of duplicating it in a second ADR.

---

No further sections apply: no new architectural decision is introduced.
