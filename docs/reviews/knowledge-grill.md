# Knowledge Grill

A review of the `knowledge/` bundle, run with the `grill-me` skill. The dimensions differ from the requirement
grills because the question is not "is this requirement sharp?" but "can this knowledge be found, trusted, and kept
true?".

**How it was run.** Structure and size were measured; every non-blank line of the nine large concepts was compared
before and after splitting; links, frontmatter, indexes, and independence were checked by `verify_knowledge.py`; all 42
diagrams were parsed with the Mermaid library; and open-decision tables and status vocabularies were compared across
documents. **What it was not.** I did not re-verify every sentence of the original 9,500 lines against the real world,
and technology notes come from general knowledge, not from fetching provider documentation today.

**Status key.** *Fixed*: the bundle or its neighbour was changed. *Added*: new knowledge written. *Verified*: checked
and fine. *Recommended*: my answer, low risk. *Decision needed*: a real choice for you. *Open*: not done, with a reason.

| Dimension | Fixed | Added | Verified | Recommended | Decision needed | Open |
|---|---|---|---|---|---|---|
| Purpose | 1 | 0 | 0 | 1 | 1 | 0 |
| Completeness | 0 | 3 | 0 | 0 | 0 | 2 |
| Consistency | 4 | 1 | 1 | 1 | 0 | 0 |
| Accuracy | 0 | 0 | 2 | 0 | 0 | 2 |
| Independence | 0 | 0 | 3 | 0 | 0 | 0 |
| Structure | 1 | 0 | 1 | 2 | 0 | 0 |
| Lifecycle | 0 | 1 | 0 | 0 | 1 | 1 |
| Retrieval | 0 | 0 | 2 | 1 | 0 | 0 |

## Purpose

**Q1. Who reads this bundle, and can they?**

- **Finding:** Agents and people read it through indexes, then single concepts. Seven architecture concepts ran 1,000 to
  1,270 lines and two more 500 to 535. An agent reading one pays for all of it; most of it is irrelevant to the question.
- **Action:** Nine concepts became overviews with 5 to 9 parts each (69 parts, none over 272 lines). The overview keeps
  the original path, so every link and `§` reference still resolves, and its table maps original section numbers to
  parts. The profile now caps a concept at 400 lines and the validator enforces it.
- **Status:** Fixed

**Q2. What is the difference between knowledge here and a requirement?**

- **Finding:** Seven architecture concepts end with an "Acceptance Criteria" section. They read like requirements but
  describe when the architecture is sound, not what the product must do.
- **Recommendation:** Keep them, as architectural fitness checks. The product-level criteria live with the requirements.
- **Status:** Recommended

**Q3. Is `product/` knowledge, or is it a requirement?**

- **Finding:** Vision and roadmap explain why and in what order; they do not state testable behaviour. The phase
  acceptance criteria were already moved out. The roadmap still lists "Deliverables" per phase.
- **Recommendation:** Keep vision and roadmap as knowledge. Treat deliverables as the roadmap's description of scope, not
  as acceptance. Decide whether you agree.
- **Status:** Decision needed

## Completeness

**Q4. What knowledge did a new engineer or agent need that did not exist?**

- **Finding:** No glossary; no statement of the principles the architecture repeats (determinism, local-first,
  explicit operations, untrusted content, freshness); no notes on the technologies Vyasa depends on and their traps; no
  practices beyond vertical slices; no runbooks except incident text buried in the security concept.
- **Action:** Added a glossary and five principle concepts; six technology notes (SQLite, MCP, Google Sheets API, GitHub
  and Bitbucket, Git metadata, Python stack); five practices; four runbooks.
- **Status:** Added

**Q5. Which diagrams were missing?**

- **Finding:** Fifteen diagrams (twelve in the original documents and three C4 views) covered context, flows, and a conceptual entity diagram. Missing: deployment, scanner
  components, table-level relationships, state machines, failure sequences, trust zones, and a threat-to-control map.
- **Action:** Added eight view concepts with 27 diagrams (deployment, scan pipeline, data model, MCP, storage,
  synchronization, remote discovery, security), using C4 context, container, component, and deployment notation plus
  sequence, state, and decision diagrams.
- **Status:** Added

**Q6. Eighty-two decision IDs are open across the architecture parts. Which have no proposed answer?**

- **Finding:** Most cluster into a few themes. Retention (DM-005, LS-005, LS-014) had no home; run status vocabulary had
  three versions; MCP defaults for refresh and paths were stated but not recorded as decisions.
- **Action:** Eighteen draft decision records, each with context, decision, alternatives, and consequences, and every
  decision part now links to the ones that propose its answers.
- **Status:** Added

**Q7. Which decisions are still unaddressed?**

- **Finding:** Not covered by any record: DM-007 lifecycle vocabulary, DM-009 and SE-008 README quality, SY-005 and
  RR-012 multi-repository representation, SY-006 portfolio enumerations, SY-013 scan-history semantics in the sheet,
  MCP-002 SDK pinning, MCP-008 cursor consistency. Several depend on product choices.
- **Recommendation:** Leave them open until the owning requirement is confirmed, then record each as a decision.
- **Status:** Open

**Q8. Are there runbooks for the ordinary operations, such as first-time setup and troubleshooting?**

- **Finding:** No. The command-line surface and installation path are not yet designed in the knowledge, so a runbook
  would invent them.
- **Recommendation:** Write them when those are designed.
- **Status:** Open

## Consistency

**Q9. Do the documents agree on status vocabularies?**

- **Finding:** Run status was `pending … interrupted` in the data model, `running … cancelled` in the storage tables, and
  `running … cancelled` again in the synchronization design; a requirement grill had a fourth variant.
- **Action:** One vocabulary for all runs (`pending, running, completed, partial, failed, cancelled, interrupted`) in the
  three documents, a decision record, and the diagrams. The requirement grill dropped `completed_with_warnings`.
- **Status:** Fixed

**Q10. Do the MCP defaults agree between knowledge and the requirements?**

- **Finding:** Knowledge says absolute paths are omitted by default (MCP-009). The requirement grill had recommended
  including them. Refresh availability (MCP-007) was ambiguous.
- **Action:** The requirement grill, its scenarios, and its decision list now follow the knowledge default. MCP-007 now
  reads "disabled unless enabled in configuration". Both are recorded as decisions.
- **Status:** Fixed

**Q11. Does the registry description agree?**

- **Finding:** The knowledge registry has three tabs and no meta tab. The requirement grill proposed a meta tab for the
  schema version, and "priority" and "notes" as portfolio fields that the registry baseline does not define.
- **Action:** The requirement grill now keeps three tabs, records the schema version in a named range, and treats the
  registry's human-managed fields (tracking level, domain, project type) as the baseline, with priority and notes as a
  schema change that still needs approval.
- **Status:** Fixed

**Q12. Do repository availability terms agree?**

- **Finding:** The data model uses `available`, `inaccessible`, `missing`, `unknown`. The requirement grill invented
  `not_found_remote`.
- **Action:** Replaced by `missing`, which the data model already defines, with remote access states kept separate.
- **Status:** Fixed

**Q13. Do numeric defaults conflict anywhere?**

- **Finding:** No. The architecture text contains no numeric limits at all; it says they are chosen during
  implementation. The only numbers are those the new decision records propose.
- **Status:** Verified

**Q14. Is the same material described in several places?**

- **Finding:** Yes. Phase 2 and 3 behaviour appears in the system architecture, the MCP interface, the scanning
  document, the storage design, and the data model. Each tells it from its own angle, and drift is the risk.
- **Recommendation:** Accept it for now. Where two descriptions overlap, one concept should own the rule and the other
  should link to it. The new views and decision records follow this: they point to the owning part instead of copying.
- **Status:** Recommended

**Q15. Do terms mean one thing?**

- **Finding:** "Workspace", "workspace root", "root", and "scope" were used loosely, as were "checkout" and "clone".
- **Action:** The glossary fixes the meaning of each. Existing prose was not rewritten.
- **Status:** Added

## Accuracy

**Q16. Do the diagrams parse?**

- **Finding:** All 42 Mermaid blocks parse with Mermaid 11.4.1. One real syntax error was found and fixed while
  writing (semicolons inside sequence messages), plus a glued frontmatter defect in the new views, caught by the validator.
- **Limit:** Parsing proves syntax, not that a renderer lays them out well or that they are accurate. I have not seen
  them rendered.
- **Status:** Verified

**Q17. Did splitting lose or alter anything?**

- **Finding:** Every non-blank line of the nine originals appears in exactly one part (0 missing). Section numbers,
  headings, and tables are unchanged. Only trailing horizontal rules at part ends were dropped.
- **Status:** Verified

**Q18. How reliable are the new technology notes?**

- **Finding:** They are written from general knowledge. Provider details move: Bitbucket's token model, Sheets quotas,
  GitHub's permission names. I did not fetch current documentation.
- **Action:** Each carries `stale_after: 2027-01-26` and says "confirm current" where it matters; the validator warns when
  that date passes.
- **Status:** Open (verify against provider documentation when each integration is built)

**Q19. Are the table-level diagrams faithful?**

- **Finding:** Columns come from the "Proposed fields" lists. The primary- and foreign-key marks and the relationships
  between tables are my inference from field names, not statements in the source.
- **Recommendation:** Treat the diagram as a draft; confirm it when the physical schema is designed.
- **Status:** Open

## Independence

**Q20. Does knowledge refer to requirements, changes, or code?**

- **Finding:** No. The validator found no link or source outside the bundle and none of the forbidden paths. A search
  found no requirement-style identifiers (FR, NFR, SEC, DOR) in any concept.
- **Status:** Verified

**Q21. Do the new decision records depend on a requirement?**

- **Finding:** They cite only concepts, parts, and technology notes. Several came from requirement grills, but each stands
  alone: context, decision, alternatives, consequences.
- **Status:** Verified

**Q22. Could the knowledge be reused if the requirements changed completely?**

- **Finding:** Mostly. The phase structure in `product/` and the phase labels in architecture parts tie the knowledge to
  today's roadmap. Principles, concepts, technology notes, practices, and runbooks do not.
- **Status:** Verified

## Structure

**Q23. Is the folder layout right?**

- **Finding:** `architecture/` now holds eight overview concepts, their eight part folders, the C4 views, and `views/`:
  eighteen entries besides the index. Each overview is the entry point, so a reader meets eight, not eighteen.
- **Recommendation:** Do not add sub-folders by theme yet.
- **Status:** Recommended

**Q24. Should the glossary be one concept per term?**

- **Finding:** OKF's unit is one concept per file, which would mean about 28 tiny files and a harder read.
- **Recommendation:** Keep one table. The unused `Term` type and `glossary/` folder in the profile can go.
- **Status:** Recommended

**Q25. Should concept size be a rule?**

- **Finding:** Without a rule the bundle drifts back to 1,000-line files.
- **Action:** `max_lines` in `profile.json`, enforced, with a test.
- **Status:** Fixed

**Q26. Are indexes complete?**

- **Finding:** Every concept and folder is listed in its index (the validator checks this), and every overview lists its
  parts with the original section numbers.
- **Status:** Verified

## Lifecycle

**Q27. Is anything verified by a person?**

- **Finding:** No. Every concept is `draft`, and no concept carries a human `verified` entry, so every one is in the
  unverified trust tier. That is accurate, and it means nothing here is reviewed.
- **Decision needed:** Who reviews, and in what order? Recommendation: the decision records and the principle concepts
  first, because requirements and code lean on them.
- **Status:** Decision needed

**Q28. How does knowledge go stale?**

- **Finding:** Only provider-dependent notes had a stale date.
- **Action:** `stale_after` on technology notes and a validator warning once it passes.
- **Status:** Added

**Q29. What triggers an update?**

- **Finding:** The `knowledge-first` skill covers closeout of a change. Nothing triggers a periodic check.
- **Recommendation:** Run the validator in the workflow check (already done) and review stale warnings at each phase gate.
- **Status:** Open

## Retrieval

**Q30. Can an agent find the right concept without reading everything?**

- **Finding:** The path is root index, section index, overview, part. Each step has a description. The overview's parts
  table says what each part answers.
- **Status:** Verified

**Q31. Are part descriptions good enough?**

- **Finding:** I wrote them by hand per part. They state the question the part answers, not just its topic.
- **Status:** Verified

**Q32. Would a knowledge graph help?**

- **Finding:** Tags and links already form one. The `graphify` skill could build a queryable graph over `knowledge/`.
- **Recommendation:** Try it once the bundle is reviewed, not before; a graph of unreviewed drafts spreads their errors.
- **Status:** Recommended

## Decisions for you

- **Q3** Whether the roadmap's deliverables stay in knowledge.
- **Q27** Who reviews the knowledge and in what order.
