---
type: comment
resource: oif:oif/a0c7qw/mcdagm
at: 2026-09-15T21:03:00+10:00
by: claude-code/2
kind: correction
---

The skill said to create a file "with `type: issue`, `title` and
`created` set", while section 3.2 says only `type` is required. Harmless
when followed, but an agent generating a validator from the skill would
have rejected conforming files. The skill now says what is required and
separately recommends the other two.
