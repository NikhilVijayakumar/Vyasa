# Architecture Decision Record: be-language-detector

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-language-detector`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** language evidence has two separate statuses and comes from a fixed versioned table.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/language-evidence-statuses.md`, so it reads correctly after this change is archived. The owner chose the two statuses and the fixed table on 2026-10-27. File composition data and limits, and partial results never imply absence, apply unchanged.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

The inventory (§9.3) requires distinguishable meanings; content is never read; the histogram must sum to the code count.

## 5. Considered Options

See the concept's Alternatives considered: merged status, content-based resolution, manifest parsing.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
