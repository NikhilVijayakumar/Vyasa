# Architecture Decision Record: be-language-query

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-language-query`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** languages are detected in the scan, stored as rows with two observations, and filtered without merging into declared technologies.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/language-observations-in-index.md`, so it reads correctly after this change is archived. The owner chose eight of its points in the second grill on 2026-10-27. Retention defaults, freshness without query-time I/O, and partial results never imply absence apply unchanged.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

No query-time I/O; honest partial results; an indexed filter; the retention default of current plus previous.

## 5. Considered Options

See the concept's Alternatives considered: query-time detection, a separate step, a JSON blob, keeping the last complete observation, merging with declared technologies.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
