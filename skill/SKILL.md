---
name: oif
description: Create, move, comment on and close issues on an Open Issue Format (OIF) board using only file tools. No package required.
---

# OIF — run a board with `ls`, `cat` and `git mv`

An OIF board is a directory of Markdown files. The directory an issue
sits in is its status. The filename carries its identity. A record may
be *about* anything in the repository. Spec: https://oif.md/SPEC.md

**Before acting on a file, check what the board already says about it:**

```sh
grep -rl -- 'path/to/file.md' <board>/
```

Someone may have filed that it is wrong, stale, or already being fixed.

## Layout

```
<board>/
├── board.md            columns in order, optional kinds, optional key
└── issues/
    ├── backlog/column.md
    ├── doing/column.md
    └── done/column.md  columns marked complete: true in board.md
```

Read `board.md` first. Its `columns` list is authoritative. If it has a
`kinds` list, every issue's `kind` must be one of those names and a child
issue's kind must be in its parent's `contains`. Every column directory
contains a `column.md` that says what belongs there and the exit
criteria. Read it before moving an issue in. `column.md`, `index.md` and
`log.md` are never issues.

## Filenames

```
issues/<column>/<slug>-<id>.md
```

- `<id>` is six characters from `0123456789abcdefghjkmnpqrstvwxyz`
  (no i, l, o, u), random, never changed.
- `<slug>` is lowercase words joined by `-`, derived from the title.

Mint an id with any of:

```sh
tr -dc '0-9a-hjkmnp-tv-z' < /dev/urandom | head -c 6; echo
python3 -c "import secrets;print(''.join(secrets.choice('0123456789abcdefghjkmnpqrstvwxyz') for _ in range(6)))"
```

Never number issues sequentially. Never put `id`, `status`, `state` or
`column` in frontmatter.

## Issue file

```markdown
---
type: issue
resource: oif:<board key>/<id>
title: Short title
kind: task
priority: medium
assignees: [coder/1.4]
requested_by: human:sam
tags: []
depends_on: []
created: 2026-09-13T03:10:00Z
---

Description as free Markdown.

## Acceptance Criteria

- [ ] Checkable statement

## Comments

### 2026-09-13T03:40:00Z coder/1.4

Comment text.
```

Actors: `human:<id>`, `<agent>/<version>`, `process:<id>`.

## Operations

**Read.** `cat issues/*/*-<id>.md comments/<id>/*.md` gets the issue and
its full history in one command.

**Point at something.** Add `about` to an issue or comment to say what
it concerns. Each entry needs `path` or `resource`; add `commit` so the
reference survives the target being renamed, since `git log --follow`
resolves the new name from that revision.

```yaml
about:
  - path: docs/orders.md
    commit: 3f9c2e1
```

Never write to the target, and never put a file beside it. Everything
you write goes under the board root. That is what lets a board describe
a repository nobody on the board owns.

**Create.** Mint an id, write the file into the target column directory
with `type: issue`, `title` and `created` set. If `board.md` has a `key`,
set `resource: oif:<key>/<id>`. Keep every other key optional.

**Move.** `git mv issues/<from>/<file> issues/<to>/`. Nothing inside the
file changes.

**Remark.** When there is something worth recording but no work to do
and no state to move through — "I checked this and it holds", "careful,
this is more settled than it reads", "this is the good one" — write a
standalone comment at `comments/<new-id>.md` with an `about` key. Do not
file an issue that is born complete; the column would carry nothing.
Conventional `kind` values are `confirms`, `disputes`, `caution` and
`note`.

**Comment.** Write a new file at `comments/<issue-id>/<new-id>.md`,
minting the comment id the same way as an issue id. Frontmatter needs
`type: comment`, `at` (ISO 8601 with an offset) and `by` (an actor);
add any other keys you need. The body is the comment text. Never edit or
delete an existing comment file; a correction is a new comment.

Only if `board.md` says `comments: inline`: append to the end of the
issue file instead, under a final `## Comments` level-2 section, each
comment a `### <ISO-8601 timestamp> <actor>` heading optionally followed
by `key=value` pairs with no spaces in values.

Do not set `merge=union` on issue files. When two branches each append a
comment inline, git collapses lines the two bodies happen to share and
one comment's body is lost with no conflict shown.

**Edit.** Change frontmatter or body as needed. Preserve keys you do not
understand. Preserve existing comments verbatim.

**Close.** Move to a column marked `complete: true`. Optionally set
`resolution` (`fixed`, `duplicate`, `wontfix`, ...).

**Delete.** Not an operation. Move to a hidden complete column such as
`archived` if the board has one.

## References

Refer to another issue by its id (`7k2x9m`) inside the board, or
`<key>-<id>` (`app-7k2x9m`) across boards. Find it with
`ls issues/*/*-7k2x9m.md`. Never link by path; paths change on move.

## Sanity checks before you finish

- filename matches `<slug>-<id>.md` with a six-character id
- file is in a directory named in `board.md` `columns`
- `kind` is declared in `board.md` `kinds`, when that list exists
- no other file on the board has the same id
- frontmatter has `type: issue` and no `id`, `status`, `state` or `column`
- `resource`, if present, ends with the filename's id
- `## Comments`, if present, is the last level-2 section
- every `depends_on`, `parent` and `related` id exists on the board

If `oifmd` is installed, `oifmd validate <board>` runs all of these.
