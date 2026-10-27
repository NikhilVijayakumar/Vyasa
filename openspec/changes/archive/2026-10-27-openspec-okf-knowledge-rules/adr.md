# Architecture Decision Record: openspec-okf-knowledge-rules

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `openspec-okf-knowledge-rules`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** the knowledge profile gains enforced content-shape rules.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is recorded as a standalone concept, `knowledge/decisions/knowledge-profile-section-rules.md`, so it reads correctly after this change is archived. This file only points to it.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

Cheap to run, data-driven, no history needed, current bundle already conforms.

## 5. Considered Options

See the concept's Alternatives considered: a full kind catalogue with layered links (rejected), warnings only (rejected), verifier-enforced immutability (rejected).

## 6. Decision

Three optional profile keys plus a deprecated-decision pointer rule, enforced as errors. See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
