# Architecture Decision Record: be-file-composition-query

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-file-composition-query`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** one walk feeds counts and languages, stored on one observation, with the indicator derived when read.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/checkout-walk-observation.md`, so it reads correctly after this change is archived. The owner chose the single walk, the shared observation, and the filter semantics on 2026-10-27, after seeing that a second walk contradicts a shared row. Language observations in the index and partial results never imply absence apply unchanged.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

No extra scan cost; counts and languages must agree; one retention and status story; the indicator must not disagree with its counts.

## 5. Considered Options

See the concept's Alternatives considered: a second walk, separate tables, storing the indicator, all-checkouts agreement, a project rollup.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
