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

- [x] Decision recorded here with its reasoning
- [x] SPEC.md sections 1, 2, 4.3, 4.4, 6, 7, 8 and 9 reflect the chosen default
- [x] The agent skill leads with the chosen form
- [x] Validator checks both forms regardless of which is default
- [ ] A merge test covering concurrent appends in the chosen form lives in the repository
