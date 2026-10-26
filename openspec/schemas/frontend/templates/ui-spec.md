# UI/UX Specification: {{change-name}}

- **OpenSpec Change ID:** `{{change-id}}`
- **Proposing team:** fe (frontend team)
- **Related proposal:** `proposal.md`
- **Related specifications:** `specs/`
- **Related design:** `design.md`

## 1. Purpose

Describe the user-facing contract this change must satisfy: the screens and
components it touches, the states each of them can be in, and the behaviour
of every state.

## 2. Scope

Identify the screens, components, and user journeys covered by this contract,
and any explicitly excluded from it.

## 3. Screen and Component Inventory

| Screen or component | Entry points | Primary user goal | Requirements covered |
|---|---|---|---|
| Name | How the user reaches it | What the user achieves | Requirement IDs |

List every affected surface. A surface that is not listed here will be
discovered during implementation.

## 4. State and Interaction Model

For each screen or component, describe every state it can be in and what the
user sees and can do in that state.

| Screen or component | State | What the user sees | What the user can do | Trigger |
|---|---|---|---|---|
| Name | loading / empty / error / partial / disabled / permitted | Observable description | Available actions | What causes it |

Cover the states that frontend changes routinely miss: loading, empty, error,
partial, disabled, and permission-dependent variants. If a state cannot occur
in this change, say so explicitly instead of leaving it unmentioned.

## 5. Design Tokens and Components Used

State the design-system elements this change relies on: tokens, primitives,
and existing components. Name new elements explicitly and justify them.

Consult the `ui-ux-pro-max` skill when this change makes a design-system
decision, and `frontend-design` when reviewing implemented screens for
hierarchy, states, spacing, and copy.

## 6. Responsive Behaviour

Describe how the layout and behaviour change across supported viewport sizes,
what reflows, what collapses, and what stays fixed. State any breakpoint
decisions and their source.

## 7. Accessibility Contract

- **Keyboard:** reachable elements, focus order, visible focus, and keyboard
  alternatives for pointer-only interactions.
- **Semantics:** roles, accessible names, and the reading order of the
  content.
- **Dynamic content:** how loading, error, and status changes are announced.
- **Visual:** contrast, target size, and any motion behavior.
- **Automated checks:** the checks that will run and what they assert.

Consult the `accessibility-testing` and `localization-accessibility-review`
skills when the change has accessibility or localization impact.

## 8. Localization Expectations

State the translatable copy, the pluralization rules, the date, time, and
number formats, and the layouts that must tolerate longer translated
strings.

## 9. Data and Permissions

State the data each surface reads and writes, and how role or scope changes
what is visible and actionable. Distinguish what the server enforces from
what the client hides.

## 10. Traceability

| Requirement | Screen or component | State | Acceptance scenario |
|---|---|---|---|
| Requirement ID | Name | State name | Scenario name |

## 11. UI Specification Review

- [ ] Every affected screen and component is listed.
- [ ] Every reachable state is described, including loading, empty, and error.
- [ ] Keyboard, focus, and semantics expectations are stated.
- [ ] Responsive behaviour is stated.
- [ ] Localization expectations are stated where copy is affected.
- [ ] Every requirement in scope is traced to a screen and state.
- [ ] Open visual questions are recorded as explicit open questions.

**Status:** Draft / Ready for design
