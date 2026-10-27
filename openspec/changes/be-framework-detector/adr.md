# Architecture Decision Record: be-framework-detector

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-28
- **OpenSpec Change ID:** `be-framework-detector`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** manifests are read under strict rules, kept with scopes, mapped through a registry, and reported per ecosystem with honest absence.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/framework-detection-from-manifests.md`, so it reads correctly after this change is archived. The owner chose the manifests, extraction, scopes, states, registry seed, filter, location, and safety rules on 2026-10-28. The technology registry decision supplies the registry shape; scan limits and partial-results decisions apply unchanged.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

This is the first detector that opens untrusted files; absence must not be inferred from a partial, skipped, or malformed state; scopes must not be flattened; no new dependency.

## 5. Considered Options

See the concept's Alternatives considered: any-depth parsing, lenient parsing, following links, runtime-only, merged scopes, free-text search, a YAML library.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
