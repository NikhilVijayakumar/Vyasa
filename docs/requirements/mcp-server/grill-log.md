# Grill Log: MCP Server and Tool Contracts

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 2 | 1 |
| Behaviour | 3 | 1 |
| Data | 2 | 1 |
| Integration | 1 | 0 |
| Architecture | 2 | 0 |
| Acceptance | 1 | 0 |
| Ambiguity | 2 | 0 |

## Intent

**Q1. Who connects?**

- **Recommendation:** Agents running as the user on the same machine (Claude Code, Codex, Gemini CLI, OpenCode, IDE agents) over stdio.
- **Why:** The product is local-first; stdio inherits the user's trust and needs no authentication.
- **Status:** Settled
- **Feeds:** FR-013 S1


## Scope

**Q2. Is refresh an MCP tool?**

- **Recommendation:** No by default. Refresh is a CLI command. An `[mcp] allow_refresh = true` setting registers an optional `refresh_index` tool for people who want it, since it writes generated state and can be expensive.
- **Why:** An agent should not start filesystem scans or write state without the user choosing that.
- **Status:** Decision needed
- **Feeds:** FR-013 S7

**Q3. Is a network transport needed?**

- **Recommendation:** No (NFD-007, SP-009). If added later it needs authentication, TLS, origin checks, and a new threat model review.
- **Why:** A listener changes the trust boundary entirely.
- **Status:** Settled
- **Feeds:** NFR-021


## Behaviour

**Q4. How are failures reported?**

- **Recommendation:** As a tool result with `isError` and a structured `error {code, message, details}` using the documented codes. JSON-RPC protocol errors are only for malformed requests.
- **Why:** Agents read tool results; a structured code lets them react without parsing text.
- **Status:** Decision needed
- **Feeds:** FR-013 S3, S5

**Q5. How strict is input validation?**

- **Recommendation:** Pydantic models with unknown fields forbidden, bounded integers (limit 1..100), string length caps, enumerated values, and no path-like arguments anywhere.
- **Why:** Rejecting what is not needed removes whole attack classes.
- **Status:** Settled
- **Feeds:** FR-013 S3; SEC-026..

**Q6. Is there a response size cap?**

- **Recommendation:** About 64 KiB per response with `truncated: true` and a total count; lists are paginated.
- **Why:** Keeps agent context and server memory bounded.
- **Status:** Recommended
- **Feeds:** FR-013 S2


## Data

**Q7. May responses include local filesystem paths?**

- **Recommendation:** Yes by default for the local client, because the point is finding where a project is; setting `expose_local_paths = false` removes them. Paths from other devices are never shown, and paths never reach a shared export.
- **Why:** The client is the user's own agent on the same machine; the setting covers stricter setups.
- **Status:** Decision needed
- **Feeds:** NFR-018, NFR-021

**Q8. How are contracts versioned?**

- **Recommendation:** Every response has `schema_version`. Fields are added, never changed. A breaking change introduces a new tool name suffix. `get_index_status` also reports server and schema versions.
- **Why:** Stable contracts are an explicit principle of the interface.
- **Status:** Recommended
- **Feeds:** NFR-038


## Integration

**Q9. Can a query tool call Google Sheets or a Git provider?**

- **Recommendation:** No. Query tools read the index only. Synchronization and remote discovery are separate explicit operations in later phases and are not exposed to agents by default.
- **Why:** Hidden network work breaks latency, offline use, and the trust model at once.
- **Status:** Settled
- **Feeds:** FR-013 S6; mcp-interface §2.5


## Architecture

**Q10. Which SDK and logging rule?**

- **Recommendation:** The official Python MCP SDK (FastMCP style). Tool functions stay thin. Logging goes to stderr and a log file only, since stdout is the protocol channel.
- **Why:** Stray prints on stdout corrupt the protocol, a common failure.
- **Status:** Recommended
- **Feeds:** NFR-038

**Q11. How do we guarantee tools cannot write?**

- **Recommendation:** All tools open the database through a read-only connection (`mode=ro`). A bug then fails loudly instead of writing.
- **Why:** Defence in depth for the read-only promise.
- **Status:** Recommended
- **Feeds:** FR-013 S6


## Acceptance

**Q12. How are contracts tested?**

- **Recommendation:** Contract tests call each tool through the SDK client; a committed JSON snapshot of the tool list and schemas is compared in CI; a stdio subprocess smoke test starts the real server.
- **Why:** A snapshot makes accidental contract changes visible in review.
- **Status:** Recommended
- **Feeds:** FR-013 S1, S2


## Ambiguity

**Q13. Can repository text attack the agent through results?**

- **Recommendation:** Repository-derived strings are typed fields with length caps, control and bidirectional characters removed, and are never merged into tool descriptions. Documentation states that these fields are data, not instructions.
- **Why:** Prompt injection through returned text is the main agent-facing risk.
- **Status:** Recommended
- **Feeds:** NFR-020

**Q14. Is there authentication?**

- **Recommendation:** None on stdio; the process inherits the user's authority. This is stated in the documentation.
- **Why:** Stating it prevents someone assuming protection that does not exist.
- **Status:** Settled
- **Feeds:** NFR-021

## Decisions for you

- **Q2** — Is refresh an MCP tool?
- **Q4** — How are failures reported?
- **Q7** — May responses include local filesystem paths?
