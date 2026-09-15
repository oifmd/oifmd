# Open Issue Format (OIF)

**Issues as files.** A directory of Markdown files that any agent or
human can run as a board with `ls`, `cat` and `git mv`. No tool required.

- **Spec:** [SPEC.md](SPEC.md) · version 0.1 (draft)
- **Site:** https://oif.md
- **Package:** `oifmd` (validator and converters)

## Sixty-second tour

```
board.md
issues/
├── backlog/
│   ├── column.md
│   └── add-jira-importer-nkhnsk.md
├── doing/
│   ├── column.md
│   └── fix-login-redirect-loop-7k2x9m.md
└── done/
    ├── column.md
    └── write-spec-outline-h87456.md
```

The directory is the status. The filename is the identity. Moving an
issue is `git mv issues/doing/fix-login-redirect-loop-7k2x9m.md issues/done/`.

`issues/doing/fix-login-redirect-loop-7k2x9m.md`:

```markdown
---
type: issue
resource: oif:app/7k2x9m
title: Login form rejects passwords containing "!"
kind: bug
priority: high
assignees: [coder/1.4]
requested_by: human:sam
tags: [auth]
created: 2026-09-13T03:10:00Z
---

Submitting a correct password with `!` clears the form and shows
"invalid credentials". Expected: login succeeds.

## Acceptance Criteria

- [x] Reproduce with a failing test
- [ ] Fix without changing the hashing path

```

Comments are separate files, one per comment, keyed by the issue's id:

`comments/7k2x9m/k3n2wp.md`

```markdown
---
type: comment
at: 2026-09-13T04:12:00Z
by: human:sam
kind: verdict
result: changes_requested
---

Keep the strip for whitespace only.
```

Read an issue and its whole history with one command:

```sh
cat issues/*/*-7k2x9m.md comments/7k2x9m/*.md
```

## Why

Every git-native tracker (Backlog.md, git-issues, beaver-backlog, beads)
converged on Markdown plus frontmatter, one file per issue. None
published the format separately from the tool. OIF is the format,
written down, with a validator, so issues outlive whichever tool wrote
them and any agent can read them cold.

Design rules that fall out of being agent-first and git-native:

- **State is the directory.** A move is one atomic rename, not a
  read-modify-write that two agents can trample.
- **Identity is a random six-character id in the filename.** Two
  branches can create issues at once and merge with no counter, no
  scan, no renumbering. Sequential keys like `APP-2753` survive as
  aliases.
- **One comment is one file**, keyed by the issue's id. Two agents
  commenting at once write two different paths, so nothing conflicts and
  nothing is lost. Appending to a shared file does not survive concurrent
  writers; see the changelog.
- **Unknown keys are preserved.** Your tracker's extra fields round-trip.
- **Every column has a `column.md`.** It keeps empty columns in git and
  tells an arriving agent what belongs there and how to leave.
- **The board declares its own vocabulary.** `board.md` lists the columns
  and, optionally, the `kinds` an issue may have and which kinds may
  contain which. Epic, story and task are one team's words, not the
  format's. Ready `board.md` files for Kanban, Scrum and Shape Up are in
  [`profiles/`](profiles/).

An OIF board is a conforming [Open Knowledge Format](https://okf.md)
bundle: same substrate, same actor convention, `type: issue` on every
file. The one deliberate divergence, identity by id rather than by path,
is spelled out in SPEC.md section 9. Trackers are platforms, OIF is the
file.

## This repository

The roadmap for OIF itself lives in [`board/`](board/), in OIF.
GitHub Issues stays open for conversation; accepted work lands in
`board/issues/` with the GitHub number kept in `external_ids`.

## Status

0.1 is a draft. Expect 0.x to move.

## License

Apache-2.0.
