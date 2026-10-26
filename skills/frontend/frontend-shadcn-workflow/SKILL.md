---
name: frontend-shadcn-workflow
description: Use for frontend component creation, migration, or shadcn source updates.
metadata:
  scope: frontend
---

# frontend-shadcn-workflow

Read the official [shadcn workflow](https://ui.shadcn.com/docs/skills), project design contract and component inventory. Inspect project info, aliases and component family; read current registry/component documentation before adding source. Use genuine registry components in the selected family, not handcrafted lookalikes labelled shadcn.

Record item, version/revision or hash, license, local source and adaptation rationale. Configuration alone is not provenance. Native semantic elements inside upstream sources are valid; features consume the public design-system API. Compose missing patterns from existing primitives and document the gap before custom implementation.

Bridge upstream semantic styles to canonical project tokens. Check source additions do not introduce a second theme authority or conflicting primitive family. Migrate existing exports/consumers deliberately. Define defaults, supported variants/sizes and states before coding; complete individual docs and relevant behavior/visual evidence before claiming completion.

Canonical content lives in skills/. Apply the existing OpenSpec lifecycle; project values stay in durable frontend guidance.

## Evidence and maintenance follow-up

For updates record source item/version/hash, license, upstream changes, each local patch, public API impact and affected consumers. Review a single family before broader updates. Do not overwrite adapted sources in bulk or refresh hashes without reviewing the actual diff.
