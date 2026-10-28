# Architecture Decision Record: be-profile-context

## 1. Decision Status

- **Status:** Proposed
- **Date:** 2026-10-28
- **OpenSpec Change ID:** `be-profile-context`
- **Decision owners:** Nikhil Vijayakumar
- **Related artifacts:** `proposal.md`, `design.md`, `specs/`

## 2. Decision Checkpoint

- [x] **New decision required:** a read-only context bundle with differences, offered as an MCP tool and a live-scanning command, with no agent launched and no profile written.
- [ ] **Existing decision applies**
- [ ] **No new ADR required**

### Rationale

The durable decision is the standalone concept `knowledge/decisions/profile-context-for-agents.md`, so it reads correctly after this change is archived. The owner chose the tool plus the command, the live in-memory scan, and the differences list on 2026-10-28. Read-only access, query-time I/O, and partial-results decisions apply unchanged.

## 3. Context and Problem

See the concept's Context.

## 4. Decision Drivers

Agents need the evidence and the comparison; the repository may not be indexed; Vyasa is read-only and starts nothing; absence must not be claimed from partial data.

## 5. Considered Options

See the concept's Alternatives considered: launching an agent, an index-only command, a command that updates the real index, automatic correction, file-system comparisons at query time.

## 6. Decision

See the concept's Decision.

## 7. Consequences

See the concept's Consequences.
