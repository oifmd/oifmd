---
type: issue
resource: oif:oif/6k9nhr
title: Document linking a board to a correspondence corpus
kind: task
priority: medium
requested_by: human:sean
created: 2026-09-16T09:00:00+10:00
about:
  - path: SPEC.md
---

A design study on holding email, chat and meeting records in a
repository concluded that correspondence belongs outside the board, as
an Open Knowledge Format corpus, with the board pointing at it through
`about`. It found that OIF needs no new keys for this: multi-target
`about`, `resource` on an `about` entry, standalone comments and
`anchor` already carry it.

Two documentation touches would make that usable without a reader
deriving it:

1. Section 3.4 should show a carried `resource` that is not an `oif:`
   URI. The worked case is `mid:<Message-ID>` (RFC 2392), which
   identifies an email independently of any mailbox, so a citation
   survives the file being renamed and means the same thing to everyone
   holding that message.
2. Section 4.4 should note that a standalone comment naming an issue in
   its `about` is not found by `cat comments/<issue-id>/*`. It is found
   by grep across `comments/*.md`. Readers will otherwise assume the
   per-issue directory holds everything about that issue.

The deferred `reply_to` should also be renamed `in_reply_to` before 0.2,
so board-native threading uses the name RFC 5322 already established
rather than inventing a near-miss.

Correspondence itself stays out of scope. The normative core of an issue
format is short, and a message model would roughly double it while
dragging in channels, attachments and evidence handling that belong with
the corpus rather than the board.

## Acceptance Criteria

- [ ] Section 3.4 shows a non-`oif:` carried resource, with `mid:` as the example
- [ ] Section 4.4 says how to find standalone comments about an issue
- [ ] The 0.2 candidate is named `in_reply_to`, not `reply_to`
