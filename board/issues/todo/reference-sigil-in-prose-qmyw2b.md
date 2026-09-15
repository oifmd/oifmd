---
type: issue
resource: oif:oif/qmyw2b
title: A bare id in prose is ambiguous with a short git hash
kind: bug
priority: medium
requested_by: human:sean
created: 2026-09-15T19:30:00+10:00
about:
  - path: SPEC.md
---

Section 5.1 says to use the bare id in prose, commit messages and chat.
A reader meeting `7k2x9m` in a commit message has no way to know it is
an issue rather than an abbreviated object name.

**The ambiguity is measurable.** Ids use 32 characters; the 16 hex
characters are all among them, so one id in 64 is indistinguishable from
a six-character short hash. Two of the 25 ids across the boards in this
repository are already in that set: `41469f` and `f46c8e`. Git resolves
abbreviations from four characters, so the collision is with a form
people really paste.

Beyond ambiguity there is no signal at all: nothing marks a bare id as a
reference, so it cannot be linked, highlighted or found by anything that
does not already know the convention.

## Candidates

- `oif:7k2x9m` — costs four characters and reuses the URI form the spec
  already defines for `resource`, so there would be one syntax rather
  than two. Same-board references would need the key to be optional.
- `oif://7k2x9m` — the authority slashes imply a host component that
  does not exist here.
- `#7k2x9m` — familiar, and the worst option. GitHub, GitLab and Gitea
  all autolink `#` to their own issues, so every reference in a commit
  message would render as a broken link to a different tracker.
- `!7k2x9m` — GitLab already uses `!` for merge requests.
- `@7k2x9m` — `@` means a person everywhere.
- Leave it bare and rely on context.

## Worth checking before deciding

GitHub supports custom autolink references, where a configured prefix
turns a token into a link. If a prefix ending in a colon is accepted,
`oif:7k2x9m` could resolve to a board publisher's HTTPS form
automatically in issues, pull requests and commit messages. That would
settle the question on its own. Confirm what prefixes and suffix
character sets are actually permitted.

## Acceptance Criteria

- [ ] Decision recorded with reasoning
- [ ] SPEC.md section 5.1 updated, and section 3.4 `about` kept consistent with it
- [ ] The agent skill uses the chosen form
- [ ] Whether GitHub autolinks can resolve the chosen form is established, not assumed
