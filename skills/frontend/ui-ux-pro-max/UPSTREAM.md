# UPSTREAM — provenance

- **Source:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (built skill payload .claude/skills/ui-ux-pro-max/)
- **License:** MIT (Copyright (c) 2024 Next Level Builder)
- **Upstream commit:** 56ea9cf174ed
- **Intake date:** 2026-10-20
- **Intake change:** OpenSpec openspec-fe

## Taken / stripped

Taken: SKILL.md, data/, eferences/, scripts/ (the consumable skill payload). Stripped: repository, cli/, docs/, galleries, screenshots, and the other built skills (anner-design, rand, design, design-system, slides, ui-styling). Installed by copy, NOT by upstream's uipro CLI, which would write real directories into .claude/skills/ and collide with this repository's link contract.

## Local patches

Patch 2 (design D-2): all 11 invocation paths `/.claude/skills/ui-ux-pro-max/scripts/search.py` replaced with the skill-directory-relative <skill-dir>/scripts/search.py, because the Claude-plugin variable does not resolve through this repository's per-agent directory links. Skill body otherwise unmodified.
