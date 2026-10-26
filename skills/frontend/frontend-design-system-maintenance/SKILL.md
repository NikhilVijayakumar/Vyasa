---
name: frontend-design-system-maintenance
description: Use for frontend shared components, variants and reusable patterns.
metadata:
  scope: frontend
---

# frontend-design-system-maintenance

Read DESIGN.md, COMPONENTS.md and affected consumers/stories. Classify primitive, component or pattern impact. Use frontend-shadcn-workflow for source changes and frontend-storybook-documentation for public examples.

Define default behavior, typed supported variants/sizes, applicable states, controlled contracts and accessibility duties before implementation. Document intentionally omitted upstream options. Reuse existing components before adding alternatives. Preserve public exports or record migration of every affected consumer.

Require source provenance, individual docs and applicable behavior/state verification. A basic rendering or one grouped story is incomplete. Review default-without-props alongside supported variants; inspect affected feature and Storybook consumers. Shared designs require maintainer review, not agent approval.

Canonical content lives in skills/. Apply the existing OpenSpec lifecycle; project values stay in durable frontend guidance.

## Adopted workflow
For shared component changes, follow [component audit and extension](references/system-audit.md). Record evidence and gaps before proposing replacements.

For form families, define shared density, surface and focus contracts rather than styling each control independently. Separate person and organization identity roles; inspect defaults in their actual feature context.


For composed control rows, enforce density through a reusable composition contract, not feature selectors. Verify inherited and explicitly overridden sizes outside the original consumer. Audit supported variants for actual visual/behavior differences and ensure default stories omit appearance props. Keep small informational chips distinct from interactive target sizing.

## Evidence and maintenance follow-up

Require actual consumer and requirement links, per-state story IDs and verification references. Explicit gaps remain incomplete; structural catalog success is not component acceptance. Reuse before adding, and record token/component/pattern/feature impact and omitted upstream options.
