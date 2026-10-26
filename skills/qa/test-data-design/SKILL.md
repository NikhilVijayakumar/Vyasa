---
name: test-data-design
description: "Designs synthetic, consistent test data and import-validation scenarios for people, staffing, and opportunity data."
---

# Skill: Test Data Design and Import Validation
## Goal
Provide safe, representative data for reliable testing of staffing, people, project, and opportunity workflows.

## Procedure
1. Read approved schemas/data dictionaries for each source file.
2. Identify required fields, data types, keys, relationships, permitted values, date rules, and duplicate handling only when specified.
3. Create synthetic data covering normal, missing, invalid, boundary, duplicate, unmatched-reference, encoding, and large-file cases as appropriate.
4. Maintain referential consistency across People, Rapports, Opportunity Register, Towers/Delivery Managers, and Client-Tower Mapping.
5. Include scenarios with no data, partial data, and conflicting data only where useful.
6. Label synthetic data clearly and keep a repeatable seed/fixture where the framework supports it.
7. Verify that reports and screenshots do not expose real personal/client data.
8. Do not decide how the application should handle bad rows unless the specification defines it; log a clarification.

## Output
Data matrix, synthetic fixtures, import test cases, data cleanup/reset steps, and unresolved schema questions.

## Guardrails
Do not use real employee, client, or opportunity data in unapproved tools. Do not assume import behaviour such as all-or-nothing versus partial acceptance.
