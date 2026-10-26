---
name: frontend-react-architecture-review
description: Use for frontend React module boundaries, state ownership and dependency review.
metadata:
  scope: frontend
---

# frontend-react-architecture-review

Read frontend architecture, public interfaces and the change design. Keep generic UI independent of feature/API/router internals; features compose public exports. Separate owned upstream primitives, reusable project patterns and domain composition. Preserve or explicitly migrate controlled props and consumer contracts.

Keep navigable state in the URL and transient interaction state local unless a demonstrated cross-cutting need justifies more. Review applicable React performance/composition guidance in docs/frontend-ui-skill-adoption.md; do not import framework-specific server patterns into a Vite application.

For shared changes identify every affected consumer, story and boundary check. Configuration and naming do not prove source provenance or completed contracts.

Canonical content lives in skills/. Apply the existing OpenSpec lifecycle; project values stay in durable frontend guidance.

## Adopted workflow
When reusable APIs or state ownership change, follow [composition review](references/composition-review.md); retain compatible upstream contracts and avoid unnecessary abstractions.

## Evidence and maintenance follow-up

Require demonstrated consumers before extracting a generic API. Test stable identity and state ownership across rerender, reorder and data shrink. URL state stays with features; transient state stays local. Public UI does not assume router or API behavior.
