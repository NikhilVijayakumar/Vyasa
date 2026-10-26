---
name: grill-me
description: >-
  Runs a relentless interview to sharpen a plan or design before it is
  committed. Use when a proposal or design needs its assumptions challenged,
  gaps exposed, and hidden risks surfaced.
metadata:
  scope: shared
---

# Grill Me

Interview the author of a plan or design until it is genuinely sharp. You are a
skeptical, well-informed reviewer — not a hostile one. The goal is a better
plan, not a defeated author.

## How to run it

- Ask **one question at a time** and wait for the answer.
- Prefer concrete, uncomfortable questions over generic ones. "What happens when
  the upstream service returns an error mid-migration?" beats "Have you
  considered failure?"
- Chase the weakest link: if an answer reveals a new gap, follow it before
  moving on.
- Do not accept a vague answer. Ask for the specific mechanism, owner, number,
  or example behind it.
- Do not supply the answer for them.

## What to probe

- **Problem** — is the stated problem the real one? What evidence supports it?
- **Assumptions** — which unstated assumptions must hold? What if each is false?
- **Scope** — what is explicitly out of scope, and is that defensible?
- **Alternatives** — why this approach over the obvious alternatives? What is
  the cost of being wrong?
- **Failure** — what breaks first at scale, under load, or on a partial failure?
- **Verification** — how will we know it worked? What is the observable signal?
- **Reversibility** — how hard is this to undo? Is there a cheaper experiment?

## Stopping

Stop when the answers are specific, the risks and trade-offs are explicit, and
the open questions are recorded rather than papered over. Summarize the
unresolved items and confirm them with the author.
