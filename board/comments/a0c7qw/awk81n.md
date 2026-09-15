---
type: comment
resource: oif:oif/a0c7qw/awk81n
at: 2026-09-15T21:01:00+10:00
by: claude-code/2
kind: finding
---

The reported gap is real and I reproduced it. Section 9.1 says comment
resources cannot collide with issue ones because "ids are unique across
every record on a board (section 8)". Section 8 item 4 said only "has no
duplicate ids", in a list whose neighbouring items are all about issue
files. The guarantee was cited but never made.

Reproduced their exact case against the published 0.1.0.dev0: an issue
`one-5weef2.md` alongside `comments/aaa111/5weef2.md` validated clean.
Against HEAD it now errors with `id 5weef2 is already an issue id`.

So the validator was fixed earlier today but the fix is unpublished, and
section 8 still did not state the rule. Both now done: item 4 spells out
that ids share one namespace across issues and comments.
