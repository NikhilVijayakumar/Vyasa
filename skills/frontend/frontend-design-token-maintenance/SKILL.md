---
name: frontend-design-token-maintenance
description: Use for frontend canonical tokens, semantic mappings and migrations.
metadata:
  scope: frontend
---

# frontend-design-token-maintenance

Read the canonical token graph and design contract. Separate identity primitives from accessible UI semantic pairings, categorical/chart colors and interaction roles. Define default/hover/pressed/focus/selected/disabled/invalid roles and elevation/motion where applicable; do not infer exact third-party values from screenshots.

Keep one DTCG authority; generated CSS, Tailwind and upstream-component theme mappings derive from it. Validate types/references/cycles/names/required roles and output freshness. Never hand-edit generated artifacts.

Before renaming/removing tokens, document replacements and affected consumers. Verify changes in both component stories and representative screens, contrast and reduced-motion behavior. Record proposed project adaptations and obtain shared-design review.

Canonical content lives in skills/. Apply the existing OpenSpec lifecycle; project values stay in durable frontend guidance.

When quieter borders conflict with an existing contrast target, measure and disclose the trade-off. Keep proposed appearances explicit and retain the existing default while a required maintainer decision is pending; do not relabel low-contrast boundaries as verified accessible. Preserve distinct focus/error and increased-contrast behavior.

## Evidence and maintenance follow-up

For deprecation/rename/removal record old role, replacement, rationale, consumers, compatibility window and migration evidence in the approved change. Keep values in canonical tokens and durable guidance; verify source hash/text normalization without rewriting historical approval records.
