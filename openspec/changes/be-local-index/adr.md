# Architecture Decision Record: be-local-index

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-local-index`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** what a vanished project becomes, how the single writer is enforced and a dead one detected, and the freshness thresholds.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/index-lifecycle-and-single-writer.md`. It extends `local-first-sqlite-index.md` (one file, one writer, per-project transactions), which already applies, and records the owner's confirmation of 2026-10-27 of Q4 (never auto-delete missing projects), Q7 (refuse overlapping refreshes) and Q15 (24-hour freshness).

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

A failed or partial scan must not erase evidence; overlapping writers must be visible and refused; freshness must be computed without scanning.

## 5. Considered Options

See the concept's Alternatives considered.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
