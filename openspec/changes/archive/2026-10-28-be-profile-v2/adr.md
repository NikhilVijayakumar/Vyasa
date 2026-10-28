# Architecture Decision Record: be-profile-v2

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-28
- **OpenSpec Change ID:** `be-profile-v2`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** a second, comprehensive profile schema as nested TOML tables, with declared ids as labels and version 1 kept.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/profile-schema-v2-full-template.md`, so it reads correctly after this change is archived. The owner chose to keep TOML, to adopt the full template, to keep declared ids as labels, and to keep both versions on 2026-10-28, advised that some template fields duplicate data other systems own. Canonical profile handling and stored identity apply unchanged.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

One predefined schema for agents to write against; declared stays separate from observed; no secrets in repository content shown to agents; no existing profile breaks.

## 5. Considered Options

See the concept's Alternatives considered: YAML, replacing version 1, growing version 1, declared ids driving identity, copying observed data.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
