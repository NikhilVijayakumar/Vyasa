# Architecture Decision Record: be-identity-ambiguity

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-27
- **OpenSpec Change ID:** `be-identity-ambiguity`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [ ] **New decision required**
- [x] **Existing decision applies:** `knowledge/decisions/stored-identity-with-aliases.md`
- [ ] **No new ADR required**

### Rationale

The existing decision already fixes aliases, the lookup order, and identity events, and says ambiguity is preserved and flagged. This change implements the flagging and extends the decision with: flags are generated, per project and kind, derived in the transaction that changed the evidence, and never resolved automatically.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

Renames must not duplicate; evidence must not be guessed; every mapping change must be auditable.

## 5. Considered Options

See the concept's Alternatives considered.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
