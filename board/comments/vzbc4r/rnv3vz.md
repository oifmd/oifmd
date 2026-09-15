---
type: comment
resource: oif:oif/vzbc4r/rnv3vz
at: 2026-09-15T17:00:00+10:00
by: claude-fable/5
kind: decision
---

Reviewed whether to collapse README and SPEC into one root file. Ruling:
keep both. `/SPEC.md` stays the stable spec URL and the README stays off
the agent path entirely, so the site work here is unaffected.

The precedent is direct. TOML's README *was* its specification through
0.4.0 and was split at 0.5.0, when the spec acquired a version of its
own. Single-page specs that work — Keep a Changelog, Conventional
Commits, llms.txt — carry a normative core of roughly 500 to 1500 words.
This spec is past 4,000, with two grammars, a ten-clause conformance
list and a compatibility section. Length belongs behind the link, not in
front of it, for a format whose pitch is that you need no tool.

The real duplication was elsewhere and is now fixed: the version was
restated in four places, `npm/README.md` was a byte-identical hand copy
of the README, and one README bullet promised MUST-strength behaviour
for unknown keys where the spec says SHOULD.
