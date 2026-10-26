---
name: frontend-test-verification
description: Use for frontend test selection, rendered evidence and completion reporting.
metadata:
  scope: frontend
---

# frontend-test-verification

Map evidence to changed requirements and component contracts. Check source provenance, public export/docs coverage and applicable default/variant/state behavior. Test interactions meaningfully; a static build or grouped showcase alone does not establish component completeness.

Use deterministic fixtures/locales/fonts/clocks for screenshots. Inspect rendered component and feature slices, normal/reduced-motion behavior and affected shared consumers. Verify keyboard, accessibility, en/es and responsive states proportionately.

Record commands, environment, source revision and actual results. Preserve rejected candidate evidence as history. Do not approve your own visual changes or regenerate baselines to clear failures. Historical passing tests do not verify a revised design; keep unimplemented and unavailable checks explicit.

Canonical content lives in skills/. Apply the existing OpenSpec lifecycle; project values stay in durable frontend guidance.

## Evidence and maintenance follow-up

Separate historical/current runs, local/hosted results and candidate/baseline approval. Validate baseline browser and rendering environment plus image hashes. Baseline source provenance is historical; comparison candidates may differ. Never mark a coverage reference as executed without a matching run.
