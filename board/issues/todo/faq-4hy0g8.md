---
type: issue
resource: oif:oif/4hy0g8
title: 'FAQ: OIF versus OKF, Backlog.md, beads, git-issues, GitHub Issues'
kind: task
priority: medium
requested_by: human:sean
created: 2026-09-13T05:00:00Z
---

One page in the shape of the OKF FAQ. Each entry says what the other
thing is for and why OIF stacks with it rather than competing.

## Where each kind of content lives

Decided. Two documents, not one, because "why not GitHub Issues" and
"how do I handle email" are different genres and a document serving both
serves neither.

- `FAQ.md` answers *why*: comparisons and objections, one paragraph
  each, no file trees. Served at `/FAQ.md` and listed in `llms.txt`.
- `patterns/<name>.md` answers *how*: worked shapes with a file tree and
  a real record. Copied to the site the same way `profiles/` is, but
  deliberately kept out of `llms-full.txt` so the agent bootstrap stays
  small.

The rule for sorting anything future: if a validator would change, it is
an RFC against the spec. If it fits one paragraph with no tree, it is
the FAQ. If it needs a tree, it is a pattern. If it argues a position
that still holds with OIF deleted, it is an essay and belongs off-site.

No appendices in the spec. Its shortness is the product.

