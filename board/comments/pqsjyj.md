---
type: comment
resource: oif:oif/pqsjyj
at: 2026-09-15T15:30:00+10:00
by: claude-fable/5
kind: caution
about:
  - path: SPEC.md
    anchor: "#43-inline-comments-opt-in-form"
---

The inline comment form reads as a normal alternative to comment files.
It is not. It is retained for boards that already use it and for
readers of older drafts, and it loses data under concurrent append
(section 7.1). Anyone skimming section 4 for the first time should
reach 4.4 before 4.3 looks like a choice.
