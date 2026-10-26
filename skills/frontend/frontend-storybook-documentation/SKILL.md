---
name: frontend-storybook-documentation
description: Use when frontend public components or patterns need Storybook documentation.
metadata:
  scope: frontend
---

# frontend-storybook-documentation

Give each public component a discoverable component page with component metadata and autodocs; use MDX for curated pattern guidance where useful. A grouped gallery and a generated props table are insufficient. Follow current [Storybook docs](https://storybook.js.org/docs/writing-docs/autodocs) for the installed version.

Document purpose, default variant/behavior, supported sizes/variants, anatomy, props/defaults/events, controlled-state contracts, keyboard/accessibility responsibilities, do/don't examples, composition, reference/provenance and known limitations. Provide live default-without-props and applicable interaction/state stories, including loading, disabled, invalid and long/localized content.

Keep story IDs and public exports in the component inventory. Verify docs routes, examples and coverage, not only the static build. Shared changes review affected examples and feature consumers. Never present omitted states, undocumented props or unreviewed screenshots as completed coverage.

Canonical content lives in skills/. Apply the existing OpenSpec lifecycle; project values stay in durable frontend guidance.

## Evidence and maintenance follow-up

Provide component-specific state ownership and duties; remove generic copied paragraphs that do not apply. Interaction examples must produce visible local state changes. Map catalog states to real CSF story IDs and keep declared gaps explicit; a prose state list is not evidence.
