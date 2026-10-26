---
name: spec-analysis
description: "Analyzes project source documents and extracts traceable requirements, conflicts, scope, and gaps without inventing behaviour."
---

# Skill: Specification Analysis
## Goal
Turn project source material into a structured, traceable specification without inventing missing behaviour.

## Inputs
Kickoff emails, approved requirements, mockups, data files/data dictionaries, user stories, API contracts, meeting notes, and stakeholder answers.

## Procedure
1. Identify each source and its date/version/owner when available.
2. Extract atomic requirements and preserve original terminology.
3. Assign stable IDs, e.g. `REQ-STAFF-001`.
4. Label every item Confirmed, Proposed, Assumption, Open Question, or Out of Scope.
5. Separate functional, data, permission, localization, non-functional, and operational requirements.
6. Detect conflicts, duplicates, vague words, missing states, missing roles, and untestable statements.
7. Create a clarification log with one concise question per unresolved decision.
8. Map requirements to the five priority capability areas and Prototype/MVP/Later scope.
9. Provide source traceability for every extracted requirement.

## Project checks
- Authentication conflict: standard login vs SEIDOR SSO must be clarified.
- Confirm definitions and ownership of Rapports, People, Opportunity Register, Towers/Delivery Managers, and Client-Tower Mapping.
- Confirm whether the prototype uses mock data or real file imports.
- Confirm language scope and how English/Spanish selection works.

## Output
Requirement inventory, ambiguity/conflict list, scope classification, and prioritized clarification questions.

## Guardrails
Do not create missing formulas, permission rules, thresholds, approval flows, or validation behaviour. Quote the source or mark the item as unresolved.
