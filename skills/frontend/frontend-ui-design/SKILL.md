---
name: frontend-ui-design
description: Use for frontend reference-led composition, visual states and browser review.
metadata:
  scope: frontend
---

# frontend-ui-design

Read applicable specs, durable DESIGN.md and component inventory. Record concrete source screen/state and access limits before designing. Apply the project's reference hierarchy; a historical prototype or an open-ended aesthetic skill cannot silently replace it.

Describe hierarchy, density, default actions, supported states, meaningful color, depth and motion before coding. Distinguish observed reference behavior from proposed adaptations; do not invent exact source tokens. Use established interface review guidance selected in docs/frontend-ui-skill-adoption.md.

Inspect real browser output per slice, including hover/focus/open interactions and normal/reduced motion. Compare representative components and affected screens at matching widths/locales. Document gaps and request exact-revision maintainer visual review; screenshots and passing tests are not approval.

Canonical content lives in skills/. Apply the existing OpenSpec lifecycle; project values stay in durable frontend guidance.

## Adopted workflows
Before implementation, use [design preparation](references/design-preparation.md) in the existing OpenSpec design/tasks. For each representative rendered slice, use [structured critique](references/design-critique.md) and record findings with evidence.

For reference refinements, inspect press, focus, icon/avatar scale and sidebar states explicitly. Static images cannot establish animation or collapsed-state behavior; document unverified details and avoid invented motion.

For toolbar refinements, compare the rendered heights and alignment of adjacent labels, fields and actions; their shared component family does not guarantee matching geometry. Choose avatar density from identity readability in the actual record layout. Evaluate navigation-action placement beside the structure it controls, and verify focus transfer if the visible control changes between expanded/collapsed states. Keep project dimensions and brand pairings in DESIGN.md.


Trace branding from canonical primitives through semantic roles to rendered identity consumers; distinguish product monograms from official logos. Review the full identity region, not only its mark. For navigation motion, inspect normal/reduced behavior, intermediate reflow, focus transfer, inert hidden content and mobile resize. Do not infer reference animation from still images.

## Evidence and maintenance follow-up

Record the exact reference screen/state, access limits, observed behavior and project adaptations. Inspect every image submitted for review, linking findings to source/environment/hash. Historical approval never transfers to changed source automatically.
