# Grill Log: Project Profile Lifecycle

Run with the `grill-me` skill. Each question was answered with a recommendation instead of waiting for you; nothing here is approved until you confirm it.

**Status key:** *Settled* — already decided by existing documents. *Recommended* — my answer, low risk, accept unless you object. *Decision needed* — a real trade-off you should choose.

| Dimension | Questions | Decision needed |
|---|---|---|
| Intent | 1 | 0 |
| Scope | 2 | 2 |
| Behaviour | 4 | 1 |
| Data | 1 | 0 |
| Integration | 1 | 0 |
| Architecture | 1 | 0 |
| Acceptance | 1 | 0 |
| Ambiguity | 2 | 0 |

## Intent

**Q1. Why a profile at all?**

- **Recommendation:** To carry what cannot be detected: purpose, lifecycle, domain, relations, owners. Without it these stay unknown, which is honest but less useful.
- **Why:** Declared knowledge belongs to the maintainers; a profile gives it a home.
- **Status:** Settled
- **Feeds:** FR-014


## Scope

**Q2. What format and path (DFR-004, DO-001, DO-002)?**

- **Recommendation:** One TOML file, `.vyasa/project-profile.toml`, with `schema_version = 1`. No root-level `VYASA.md` in phase 1, to avoid two authorities for one field. The README remains the documentation.
- **Why:** One authority per field is the ownership rule.
- **Status:** Decision needed
- **Feeds:** FR-014 note; DFR-004

**Q3. Which fields in version 1?**

- **Recommendation:** `name`, `purpose` (500 characters), `lifecycle` (active, maintenance, experimental, deprecated, archived), `domain` and `tags` (lists), `technologies` (declared), `related_projects` (identity plus relation), `documentation.entry_point` (relative path), `owners` (strings). Absolute paths, URLs with credentials, and secrets are rejected by the validator.
- **Why:** Covers what cannot be detected without inviting private data.
- **Status:** Decision needed
- **Feeds:** FR-014


## Behaviour

**Q4. What if the profile is partly invalid?**

- **Recommendation:** Validate per field. Valid fields are used, invalid ones produce a `profile_invalid` observation with the field path and reason. An unsupported `schema_version` marks the whole profile `unsupported`.
- **Why:** Matches the rule that a malformed profile must not block other extraction, without trusting a half-parsed file silently.
- **Status:** Recommended
- **Feeds:** FR-014 S4..S6

**Q5. Declared and detected values disagree (S5)?**

- **Recommendation:** Declared fields (name, purpose, lifecycle, relations) win for those fields. Technologies are shown as two lists, declared and detected, with a visible note for a declared technology no manifest confirms. Both keep their provenance.
- **Why:** Neither side is hidden, and ownership decides who wins.
- **Status:** Recommended
- **Feeds:** FR-014 S5

**Q6. How does draft generation work (DO-003)?**

- **Recommendation:** An explicit command `vyasa profile draft <project>`. It prints the exact path, writes only `.vyasa/project-profile.draft.toml`, adds a rule to `.git/info/exclude` instead of editing the tracked `.gitignore`, refuses to overwrite without `--force`, and lists missing fields as comments.
- **Why:** `.git/info/exclude` is local and untracked, so nothing tracked changes. Writing is limited to one named file.
- **Status:** Decision needed
- **Feeds:** FR-014 S2, S3

**Q7. Who promotes a draft?**

- **Recommendation:** A person, by renaming or editing the file and committing it. Vyasa offers `vyasa profile check` to validate a file but never promotes.
- **Why:** Promotion is a human decision.
- **Status:** Settled
- **Feeds:** DOR-006


## Data

**Q8. Is the profile copied into the index?**

- **Recommendation:** Only its values, as `declared` observations with source path and field. The file is not copied.
- **Why:** The repository stays the authority.
- **Status:** Settled
- **Feeds:** FR-014 S4


## Integration

**Q9. Does the same profile work for remote repositories?**

- **Recommendation:** Yes in phase 3: fetched through the provider API at a pinned revision and validated by the same code.
- **Why:** One schema, two sources.
- **Status:** Settled
- **Feeds:** FR-019


## Architecture

**Q10. Where is the schema defined?**

- **Recommendation:** As a Pydantic model; a JSON Schema generated from it is committed as `schemas/project-profile.v1.json`, so maintainers can validate in their editor.
- **Why:** The model is the single source and the exported file is a build artifact.
- **Status:** Recommended
- **Feeds:** FR-014


## Acceptance

**Q11. How do we prove the scanner never writes?**

- **Recommendation:** A before and after hash of a fixture repository around a full scan, plus tests for valid, invalid, and unsupported profiles and for each draft rule.
- **Why:** The strongest proof of read-only is that nothing changed.
- **Status:** Recommended
- **Feeds:** FR-014 S4, S6


## Ambiguity

**Q12. Is the profile trustworthy input?**

- **Recommendation:** No. It is repository content. Values have length caps, control characters are stripped, and they are returned as typed data, never as instructions.
- **Why:** A profile is a convenient place to plant text that targets an agent.
- **Status:** Recommended
- **Feeds:** NFR-020

**Q13. What about monorepos?**

- **Recommendation:** One profile per repository root in version 1. Component profiles are out of scope until needed.
- **Why:** Avoids designing for a case we have not seen.
- **Status:** Recommended
- **Feeds:** FR-002 S3

### Second grill: comprehensive profile and agent context

**Q14. Is the proposed YAML profile at the repository root adopted?**

- **Recommendation:** No. The TOML profile at `.vyasa/project-profile.toml` stays. Owner chose this option.
- **Why:** TOML is in the standard library, a second authority was rejected, and the writer guide is already built; consumers read the profile through Vyasa, not the raw file.
- **Status:** Settled
- **Feeds:** FR-026

**Q15. How deep is the next profile schema?**

- **Recommendation:** Schema version 2 adopts the full proposed template as nested TOML tables: project identity, business purpose, scope, capabilities, declared technology, architecture, interfaces, dependencies, engineering references, documentation map, collaboration, relationships, and profile maintenance. Every field is optional and validated alone. Owner chose the full template, advised that some fields duplicate data other systems own.
- **Why:** The owner wants one comprehensive, predefined schema that an agent fills from evidence.
- **Status:** Settled
- **Feeds:** FR-026

**Q16. How do declared ids fit the remote-derived identity decision?**

- **Recommendation:** `project.id` and the relationship ids are stored as declared labels only: shape-validated, no URLs or paths, shown in details and used only by the differences list. Vyasa's own project identity never reads them. Owner chose this option.
- **Why:** A wrong or copied declared id must not merge or split projects.
- **Status:** Settled
- **Feeds:** FR-026

**Q17. How do versions 1 and 2 coexist?**

- **Recommendation:** Both are read. Version 1 files keep working unchanged; version 2 uses the nested tables and its fields are stored under dotted names such as `project.summary`, while version 1 keeps its names; one accessor reads a value from either version; the guide and JSON Schema describe version 2 and say version 1 is still read. Owner chose this option.
- **Why:** No existing profile becomes unsupported.
- **Status:** Settled
- **Feeds:** FR-026

**Q18. How does the agent get the deterministic facts?**

- **Recommendation:** A read-only MCP tool and a CLI command return the same bundle: the checkout facts Vyasa observed, the profile as read, the differences list, and the writer workflow. Vyasa never launches an agent. Owner chose the tool and the command.
- **Why:** Launching an agent breaks read-only scanning, explicit operations, and no LLM in the pipeline.
- **Status:** Settled
- **Feeds:** FR-027

**Q19. Where does the CLI get its facts?**

- **Recommendation:** A live read-only scan of that one checkout, held in a temporary in-memory index that is discarded; it writes nothing to disk and does not touch the real index. The MCP tool serves the stored observation. Each bundle states its source and observed time. Owner chose this option.
- **Why:** An agent working in a repository may not have it indexed yet.
- **Status:** Settled
- **Feeds:** FR-027

**Q20. Does the differences list ship now?**

- **Recommendation:** Yes. A deterministic comparison of the declared profile with stored observations, labelled as findings for review and never correcting the profile. Owner chose this option.
- **Why:** A declared technology that was not detected, or the reverse, is a useful review finding.
- **Status:** Settled
- **Feeds:** FR-027

**Q21. Which comparisons are safe to make?**

- **Recommendation:** Only where the observation supports them: a declared language or framework is reported as not detected only after a complete assessment; unmatched declared names are reported as not comparable; detected items are reported as undeclared only when the profile declares that category; declared OpenSpec or agent instruction references are compared with the markers.
- **Why:** Partial results never imply absence.
- **Status:** Recommended
- **Feeds:** FR-027

**Q22. How are secrets and contacts kept out of the profile?**

- **Recommendation:** Every text field rejects a URL that carries credentials; the contact reference rejects email addresses and URLs; paths must be repository-relative; the unchanged size limit applies. A rejected field is dropped and reported, the others are kept.
- **Why:** The profile is repository content and is shown to agents and other projects.
- **Status:** Recommended
- **Feeds:** FR-026

## Decisions for you

- **Q2** — What format and path (DFR-004, DO-001, DO-002)?
- **Q3** — Which fields in version 1?
- **Q6** — How does draft generation work (DO-003)?
