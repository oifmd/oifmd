# Open Issue Format (OIF)

![](brand/oif-header-1500x500.png)

**Issues and review comments as files, in any git repository, about
anything in it.**

An issue is a Markdown file whose directory is its state. A comment is a
create-only file recording who said what, when, about which issue or
which path at which commit. Concurrent comments never conflict. Nothing
installed, and nothing written into the files being discussed.

- **Spec:** [SPEC.md](https://github.com/oifmd/oifmd/blob/main/SPEC.md)
- **Site:** https://oif.md
- **Package:** `oifmd` (validator)

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
about:
  - path: src/LoginForm.svelte
    commit: 3f9c2e1
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

Find what the board says about a file before you touch it:

```sh
grep -rl -- 'src/LoginForm.svelte' .     # or: oifmd about src/LoginForm.svelte
```

Not everything has a lifecycle. A standalone comment records a judgement
with no work attached, at `comments/<id>.md`:

```markdown
---
type: comment
at: 2026-09-15T04:10:00Z
by: human:sam
kind: confirms
about:
  - path: docs/orders.md
    commit: 3f9c2e1
---

Checked against the billing code at this commit. Holds.
```

## Install

The format needs no tool. The validator is there when you want the
conformance list in section 8 of the spec checked for you.

```sh
pip install oifmd

oifmd validate <board>      # check a board against the spec
oifmd about <path>          # what the board says about a file
oifmd new <board> todo "…"  # create an issue with a fresh id
```

## Why

Every git-native tracker (Backlog.md, git-issues, beaver-backlog, beads)
converged on Markdown plus frontmatter, one file per issue. None published
it as a versioned specification with a validator, so the format is only
as portable as the tool that wrote it. OIF is the format,
written down, with a validator, so issues outlive whichever tool wrote
them and any agent can read them cold.

Design rules that fall out of being agent-first and git-native:

- **State is the directory.** A move is one atomic rename, not a
  read-modify-write that two agents can trample.
- **Identity is a random six-character id in the filename.** Two
  branches can create issues at once and merge with no counter, no
  scan, no renumbering. Sequential keys like `APP-2753` survive as
  aliases.
- **Records point at things; things never point back.** Everything is
  written under the board root, so a board can describe a vendored
  dependency, a submodule, a generated tree or a repo you only cloned to
  review. The target's own tooling sees no diff.
- **One comment is one file**, keyed by the issue's id. Two agents
  commenting at once write two different paths, so nothing conflicts and
  nothing is lost. Appending to a shared file does not survive concurrent
  writers; see SPEC.md section 7.1.
- **Unknown keys pass through.** A conforming consumer never rejects
  them and keeps them when it rewrites a file.
- **Every column has a `column.md`.** It keeps empty columns in git and
  tells an arriving agent what belongs there and how to leave.
- **The board declares its own vocabulary.** `board.md` lists the columns
  and, optionally, the `kinds` an issue may have and which kinds may
  contain which. Epic, story and task are one team's words, not the
  format's. Ready `board.md` files for Kanban, Scrum and Shape Up are in
  [`profiles/`](https://github.com/oifmd/oifmd/blob/main/profiles).

An OIF board is a conforming [Open Knowledge Format](https://okf.md)
bundle: same substrate, same actor convention, `type: issue` on every
file. The one deliberate divergence, identity by id rather than by path,
is spelled out in SPEC.md section 9. A tracker is a service you log into; OIF is a
directory you already have.

## This repository

The roadmap for OIF itself lives in [`board/`](https://github.com/oifmd/oifmd/blob/main/board), in OIF.
GitHub Issues stays open for conversation; accepted work lands in
`board/issues/` with the GitHub number kept in `external_ids`.


## License

Apache-2.0.

Open Issue Format is an independent specification, not affiliated with
or endorsed by Google. Open Knowledge Format, OKF and Google are marks
of their respective owners. See SPEC.md section 10.
