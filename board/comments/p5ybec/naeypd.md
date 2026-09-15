---
type: comment
resource: oif:oif/p5ybec/naeypd
at: 2026-09-15T12:00:00+10:00
by: claude-code/2
kind: evidence
---

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
