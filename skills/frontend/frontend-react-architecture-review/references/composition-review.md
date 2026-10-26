# React composition review

Project adaptation informed by [Vercel composition-patterns](https://github.com/vercel-labs/agent-skills/blob/main/skills/composition-patterns/SKILL.md), reviewed 2026-10-22. Not a vendored upstream package.

For reusable components:

- Prefer explicit supported variants over interacting boolean modes.
- Use compound parts when consumers need structural flexibility; keep simple controls simple.
- Give state one owner and expose clear values/actions; lift it only when consumers need coordination.
- Keep presentation independent from domain services and router internals.
- Preserve required upstream composition APIs and accessibility behavior.
- Check installed React and dependency compatibility before API migrations.

Record the public contract, state owner and migration consequences in the existing design. Review representative callers and stories. Do not replace valid upstream APIs to satisfy a stylistic rule or introduce Next.js/server architecture into this Vite project.
