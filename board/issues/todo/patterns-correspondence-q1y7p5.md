---
type: issue
resource: oif:oif/q1y7p5
title: "patterns/correspondence.md: how a board cites email, chat and meetings"
kind: task
priority: medium
requested_by: human:sean
created: 2026-09-16T10:00:00+10:00
---

The first entry in `patterns/`, and the answer to "how do I handle
email". Correspondence lives outside the board as an Open Knowledge
Format corpus; the board cites it through `about` carrying the message's
own identifier.

Show the file tree, one sidecar record, one issue citing it, and one
standalone comment spanning two issues, since that last case is the one
readers do not discover on their own.

Say plainly why an email is not a comment: a comment's `by` is a board
actor asserting something, while a message is evidence the board did not
author. Evidence is a target, not a record.

Do not make it email-shaped. A meeting transcript and a chat export are
one artefact with many turns, not many records.

## Acceptance Criteria

- [ ] `patterns/` exists and is served, on the same copy rule as the board presets
- [ ] Worked tree, sidecar, citing issue, and a comment spanning two issues
- [ ] A non-email example, so the pattern is not email-shaped
- [ ] One FAQ line pointing here
