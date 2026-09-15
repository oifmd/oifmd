---
type: issue
resource: oif:oif/p5ybec
title: Decide whether sidecar comments become the default form
kind: task
priority: high
created: 2026-09-15T12:00:00+10:00
---

Section 7.1 now documents a measured hazard: two branches appending
inline comments whose bodies share any line lose one body, silently
under `merge=union` and deceptively under the default driver. Section
7.2 adds sidecar comments as the safe form. The open question is which
form 0.1 should present as the default.

The case for inline staying default: one file holds the whole issue, so
`cat` shows everything and the format's central claim stays intact. The
hazard needs two agents commenting on one issue in the same window,
which many boards never hit.

The case for sidecar becoming default: the format is agent-first and
concurrent agents are the expected case, not the exception. A default
that is only safe when nobody else is working is a poor default. The
same reasoning made issue ids random rather than sequential, and this is
that argument one level down.

## Acceptance Criteria

- [ ] Decision recorded here with its reasoning
- [ ] SPEC.md section 4.3 and 7 reflect the chosen default
- [ ] The agent skill leads with the chosen form
- [ ] Validator checks both forms regardless of which is default
- [ ] A merge test covering concurrent appends in the chosen form lives in the repository

## Comments

### 2026-09-15T12:00:00+10:00 claude-code/2 kind=evidence

Measured on git 2.x with two branches each appending a comment whose
body contained the lines `Root cause identified.`, a blank line,
`Steps:` and three list items.

With `merge=union` the result carried both `###` headings adjacent,
followed by a single copy of the shared body. No conflict was raised.
One comment's body was gone.

Without the union driver the merge conflicted, but the markers enclosed
only the two heading lines; the shared body sat below them as common
context. Resolving by keeping both headings reproduces the collapse, and
the conflict presents as trivial.

Hypothesis raised by a peer session reviewing the comment grammar; the
measurement went further than the hypothesis, which predicted
interleaving rather than loss.
