---
type: issue
resource: oif:oif/tapcy7
title: Align comment frontmatter to OKF's generated key
kind: task
priority: high
created: 2026-09-15T14:30:00+10:00
---

Comment files currently carry flat `at` and `by`. OKF v0.2 already has
a vocabulary for exactly this: `generated: {by, at}`. Our keys are valid
OKF, since OKF requires only `type` and preserves unknown keys, but an
OKF consumer cannot attribute our comments without understanding them.

Adopting `generated` costs one nesting level and buys semantic interop
with every OKF reader. It is also a precondition for proposing a comment
concept upstream: proposing a design whose own reference implementation
uses parallel keys invites the obvious objection.

Decide, then either migrate or record why not. If migrating, keep `at`
and `by` readable by consumers for one minor version.

## Acceptance Criteria

- [ ] Decision recorded with reasoning
- [ ] SPEC.md section 4.4 updated
- [ ] Validator and schema accept the chosen form
- [ ] Example and roadmap boards migrated
