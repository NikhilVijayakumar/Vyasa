# Architecture Decision Record: be-file-composition-counts

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-file-composition-counts`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** file types are versioned data shared with the language detector, and counting has its own entry cap.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/file-composition-data-and-limits.md`, so it reads correctly after this change is archived. The owner confirmed the separate entry cap on 2026-10-27. Scan limits and symlink defaults, and partial results never imply absence, apply unchanged.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

Most real repositories exceed the 5,000-entry inventory cap; counting reads no content; two extension lists would drift.

## 5. Considered Options

See the concept's Alternatives considered: reuse the 5,000 cap, no cap, separate lists.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
