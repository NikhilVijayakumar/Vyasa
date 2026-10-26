---
name: frontend-accessibility-review
description: Use for frontend semantics, keyboard, focus, contrast, reflow and motion review.
metadata:
  scope: frontend
---

# frontend-accessibility-review

Review component contracts and current established interface guidance selected by the project. Verify accessible names, field/error associations, status meaning without color and full applicable keyboard behavior. Menus/dialogs need correct dismissal and focus return; modal focus containment belongs to the chosen primitive.

Check all supported variants and interactive states, chart/category contrast, long localized content, local table overflow, native zoom and reflow. Inspect both normal motion and reduced motion; nonessential movement must be suppressible without hiding state.

Run relevant automated checks and manual keyboard/assistive-technology checks. Record unavailable checks honestly; automated scans and screenshots do not establish WCAG conformance.

Canonical content lives in skills/. Apply the existing OpenSpec lifecycle; project values stay in durable frontend guidance.

## Evidence and maintenance follow-up

Record automated results separately from keyboard, screen-reader, native zoom, forced-colors and increased-contrast evidence. Appearance decisions cannot waive conformance. Report missing host/assistive-technology access explicitly and retain concrete manual procedures.
