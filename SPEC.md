# Open Issue Format (OIF) — Specification

> Issues and review comments as files, in any git repository, about
> anything in it.

**Version:** 0.1 (draft)
**Status:** starting point, not a finished standard. Expect 0.x to move.
**License:** Apache-2.0

OIF is a file format for issues, tasks, tickets and work items that live
in a git repository. It is designed so that any agent or human with
`ls`, `cat` and `git mv` can run a board with no tool installed.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be
interpreted as described in RFC 2119.

## 1. Principle: the filesystem is the record

| Layer       | Carries                     | Mechanism                        |
|-------------|-----------------------------|----------------------------------|
| Directory   | workflow state (the column) | `git mv`                         |
| Filename    | identity (slug + id)        | fixed at creation                |
| Frontmatter | attributes                  | YAML                             |
| Body        | prose and criteria          | CommonMark                       |
| One comment | one comment                 | create-only file under `comments/`|

Neither state nor identity appears in frontmatter. They therefore cannot
disagree with the filesystem. Changing state, minting identity and
adding a comment are all single create-or-rename operations: none is a
read-modify-write of a file another writer may hold. That property is
what lets two agents work the same board on two branches and merge.

### 1.1 Write boundary

A record may be *about* anything in the repository: a document, a
configuration file, a knowledge concept, a directory. Producers MUST
write only under the board root. They MUST NOT modify a target, and
MUST NOT place a file beside one.

This is what lets a board describe a repository nobody on the board
owns: a vendored dependency, a submodule, a generated tree that will be
regenerated, a binary, or a checkout taken purely to review it. A
target's own tooling sees no diff.

The cost is that a reader holding only the target cannot see that
records exist about it. Discovery runs from the board (section 5.2),
not from the target.

## 2. Board layout

### 2.0 Where a board lives

A board is any directory containing `board.md` and `issues/`. This
specification writes that directory as `<board>`.

- A repository MAY contain several boards. Nothing distinguishes one as
  primary.
- A board MAY sit at the repository root, or at any depth.
- A consumer finds boards by looking for `board.md`. Searching for
  `board.md` at the repository root, then one level down, then under a
  conventional directory such as `board/` or `.oif/`, resolves the
  common cases; no location is normative.
- A board does not require a git repository. Git supplies history and
  merge behaviour (section 7), and `about.commit` (section 3.4) has no
  meaning without it, but a board on a plain filesystem is conforming.
- Paths in `about` entries are relative to the **repository root** when
  the board is in a repository, and to the board's parent directory when
  it is not.

```
<board>/
├── board.md            the board: ordered columns, kinds, charter
├── index.md            OPTIONAL, OKF entry point, see section 9
├── comments/           one directory per issue id, see section 4.4
│   └── 7k2x9m/
│       ├── k3n2wp.md
│       └── q8v4jd.md
└── issues/
    ├── backlog/
    │   └── column.md   the column: what belongs here, exit criteria
    ├── doing/
    │   └── column.md
    └── done/
        └── fix-login-7k2x9m.md
```

- `board.md` is REQUIRED. Its frontmatter declares the board; its body is
  free text (charter, working agreements, anything).
- `issues/` is REQUIRED. Each direct subdirectory is a column.
- Every declared column MUST have a directory, and every column directory
  MUST contain a `column.md` (section 2.2). Git does not track empty
  directories; the column file keeps an empty column present, and it is
  what an arriving agent reads first.
- `comments/` is OPTIONAL and reserved. Each direct subdirectory is an
  issue id and holds that issue's comment files; each Markdown file
  directly inside `comments/` is a standalone comment (section 4.4). It sits
  outside `issues/` because it is keyed by identity, not by state, so an
  issue moving between columns leaves its comments untouched.
- `column.md`, `index.md` and `log.md` are reserved names and are never
  issues. `index.md` and `log.md` are OPTIONAL in any directory and, when
  present, follow the Open Knowledge Format shape (section 9).
- Files anywhere else under `<board>/` are not issues and are ignored by
  conforming consumers.

### 2.1 `board.md` frontmatter

```yaml
---
type: board           # REQUIRED. Fixed value.
oif: "0.1"            # REQUIRED. Spec version this board conforms to.
key: app              # RECOMMENDED. Used to reference records; see 5.1.
columns:              # REQUIRED. Ordered. Names are directory names.
  - name: backlog
  - name: todo
  - name: doing
    wip: 3            # OPTIONAL advisory work-in-progress limit.
  - name: blocked
  - name: done
    complete: true    # Issues here are finished.
  - name: archived
    complete: true
    hidden: true      # OPTIONAL. Consumers SHOULD hide by default.
comments: sidecar     # OPTIONAL. `sidecar` (default) or `inline`.
kinds:                # OPTIONAL. When absent, `kind` is free text.
  - name: epic
    contains: [story]
  - name: story
    contains: [task, bug]
  - name: task
  - name: bug
---
```

- `columns[].name` MUST match `^[a-z0-9]+(?:[_-][a-z0-9]+)*$`.
- A directory under `issues/` whose name is not a declared column is a
  validation error.
- `key`, when present, MUST match `^[a-z][a-z0-9]{1,15}$`. It is
  RECOMMENDED: a board without one cannot be referenced by token and
  its records have no `resource` (section 5.1).
- `comments` selects where comments are written: `sidecar` (section 4.4)
  or `inline` (section 4.3). When absent the value is `sidecar`.
  Producers MUST honour it when writing. Consumers MUST read both forms
  regardless of its value, because a board may carry history in the form
  it used previously.
- `kinds`, when present, is the board's vocabulary for the issue `kind`
  key. Every issue's `kind` MUST then be a declared name, and an issue
  with a `parent` MUST have a kind listed in the parent's `contains`.
  Top-level issues of any declared kind are always allowed. The
  specification names no hierarchy of its own: epic, story and task are
  one team's vocabulary, not the format's. See `profiles/` for ready
  `board.md` files for common methods.

### 2.2 `column.md`

```yaml
---
type: column          # REQUIRED. Fixed value.
title: Doing          # RECOMMENDED.
description: Work someone has picked up and is actively on.  # RECOMMENDED, one sentence.
---

Exit: acceptance criteria all checked and the change merged.
```

The body is prose for whoever arrives in the column: what belongs here,
what has to be true to leave. Order, `wip`, `complete` and `hidden` live
only in `board.md`; `column.md` MUST NOT repeat them.

## 3. Issue files

### 3.1 Path and identity

```
issues/<column>/<slug>-<id>.md
```

- `<id>` is exactly six characters from the lowercase Crockford base32
  alphabet `0123456789abcdefghjkmnpqrstvwxyz` (no `i`, `l`, `o`, `u`).
  It is generated randomly at creation and never changes.
- `<slug>` MUST match `^[a-z0-9]+(?:-[a-z0-9]+)*$` and SHOULD be derived
  from the title. It is display only. It MAY be changed by renaming the
  file; identity is unaffected.
- The id is the sole identity of an issue. Two files in one board with
  the same id are a validation error, regardless of slug or column.
- Producers MUST NOT generate sequential ids for new issues. Sequential
  identifiers such as `APP-2753` are valid *aliases* (see 3.2) and are
  how issues imported from other trackers keep their numbers.

Rationale: random ids need no counter, no scan and no coordination, so
two branches can create issues concurrently and merge without conflict.
Sequential ids are only safe with a single serialising allocator, which
an open format cannot assume.

### 3.2 Frontmatter

Frontmatter is REQUIRED and MUST be a YAML mapping delimited by `---`
lines at the top of the file. `type` is REQUIRED; every other key is
OPTIONAL.

```yaml
---
type: issue
resource: oif:app/7k2x9m
title: Login form rejects passwords containing "!"
description: Correct passwords with "!" are rejected at login.
kind: bug
priority: high
assignees: [coder/1.4]
requested_by: human:sam
tags: [auth]
parent: 9m27dj
depends_on: [d370av]
related: []
about:
  - path: docs/auth/login.md
    commit: 3f9c2e1
created: 2026-09-13T03:10:00Z
due: null
resolution: null
aliases: [APP-2753]
external_ids:
  github: acme/app#412
---
```

| Key            | Type                | Notes |
|----------------|---------------------|-------|
| `type`         | string              | REQUIRED. MUST be `issue`. Lets a file identify itself when read alone, and satisfies OKF. |
| `resource`     | URI                 | RECOMMENDED. `oif:<key>/<id>`. The stable identity for consumers that key on path. See 5 and 9. |
| `title`        | string              | RECOMMENDED. Consumers fall back to the slug. |
| `description`  | string              | A one-sentence summary, for listings and for OKF consumers. Distinct from the body's opening prose (section 4.1), which is the full description. Neither is derived from the other. |
| `kind`         | string              | Free. Common: `task`, `bug`, `feature`, `epic`. |
| `priority`     | string              | Free. Common: `critical`, `high`, `medium`, `low`. |
| `assignees`    | list of actor       | See 3.3. |
| `requested_by` | actor               | |
| `tags`         | list of string      | |
| `parent`       | issue ref           | See 5. |
| `depends_on`   | list of issue ref   | This issue cannot complete until these do. |
| `related`      | list of issue ref   | Undirected. |
| `about`        | list of targets     | What this issue concerns, outside the board. See 3.4. |
| `created`      | ISO 8601 datetime   | RECOMMENDED. MUST carry `Z` or a numeric offset. Git history is not reliable after import. |
| `due`          | ISO 8601 date or datetime | A bare `YYYY-MM-DD` means end of that day in the board's own reckoning; a datetime MUST carry an offset. |
| `resolution`   | string              | A short token, not a report: `fixed`, `duplicate`, `wontfix`, and so on. Prose explaining the outcome belongs in a comment or the body. Only meaningful in a `complete` column; elsewhere it says nothing and SHOULD be absent. |
| `aliases`      | list of string      | Other names this issue answers to, e.g. legacy sequential keys. |
| `external_ids` | map string→string   | Keys are system names (`github`, `jira`, …). |

A note for implementers: a YAML parser yields a native date or datetime
object for an unquoted timestamp, not a string. Consumers MUST accept
both that and a quoted string, and SHOULD serialise back to an ISO 8601
string with an explicit offset when writing JSON. The published schemas
describe the JSON projection, so they specify strings.

Reserved keys that MUST NOT appear in issue frontmatter, because the
filesystem carries them: `id`, `status`, `state`, `column`.

Producers MAY include any other key. Consumers MUST NOT reject unknown
keys and SHOULD preserve them when rewriting a file.

### 3.3 Actors

An actor is a string naming a human, an agent or a process. The
convention follows the Open Knowledge Format:

- `human:<id>` — a person, e.g. `human:sam`
- `<agent>/<version>` — an agent, e.g. `coder/1.4`, `claude-code/2.1`
- `process:<id>` — automation, e.g. `process:ci`

A bare string is permitted and means "kind unspecified".

Formally an actor matches:

```
actor    = human / agent / process / bare
human    = "human:" 1*idchar
process  = "process:" 1*idchar
agent    = 1*idchar "/" 1*VCHAR-without-space
bare     = 1*idchar
idchar   = ALPHA / DIGIT / "-" / "_" / "." / "@"
```

Consumers MUST NOT reject an actor they cannot classify; an unrecognised
prefix is a bare actor.

### 3.4 Targets

An issue or a comment MAY carry `about`: a list of things in the
repository it concerns. Each entry is a mapping with at least one of
`path` or `resource`.

```yaml
about:
  - path: docs/orders.md        # repo-relative path to the target
    commit: 3f9c2e1             # RECOMMENDED. Revision that was reviewed.
    anchor: "#cancellation"     # OPTIONAL, advisory. Not tracked across edits.
  - resource: okf:acme/orders   # a stable id, when the target has one
  - repo: https://github.com/acme/api   # OPTIONAL. Default is the board's repo.
    path: openapi.yaml
    commit: b81d0aa
```

- `path` is relative to the repository root, not to the board.
- `commit` pins which revision was looked at. Without it a path is a
  guess about the present; with it the reference stays meaningful after
  the target is renamed, because `git log --follow` resolves the current
  name from that commit using git alone.
- `resource` is a stable identifier the target carries itself. When both
  are present `resource` wins.
- Resolution order is `resource`, then `path` at `commit`, then `path`
  at HEAD.
- One record MAY name several targets. A contradiction between two
  documents is one issue about both, not two issues.

Nothing is written to a target. See 1.1.

## 4. Body

The body is CommonMark. It begins after the closing `---` of the
frontmatter.

### 4.1 Description

Everything before the first level-2 heading is the description. It is
free text and MAY be empty.

### 4.2 Recommended sections

Level-2 headings with the following exact names have conventional
meaning. None is required and any other heading is allowed.

- `## Acceptance Criteria` — a GFM task list (`- [ ]` / `- [x]`).
  Consumers MAY compute completion from the checked ratio.
- `## Plan` — intended approach.
- `## Notes` — working notes.

### 4.3 Inline comments (opt-in form)

Producers MUST NOT write inline comments unless `board.md` declares
`comments: inline`. The default form is 4.4. Consumers MUST read this
section when present whatever the board declares, because a board may
hold history written under an earlier setting.

If present, `## Comments` MUST be the last level-2 section in the file.
Each comment is a level-3 heading matching this grammar, followed by
free text up to the next level-3 heading or end of file:

```
### <timestamp> <actor>[ <key>=<value>]*
```

- `<timestamp>` is an ISO 8601 datetime in **extended** form, carrying a
  `Z` or a numeric offset, matching:

  ```
  \d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})
  ```

  Basic form (`20260913T031000Z`) is valid ISO 8601 but is NOT accepted
  here, because the heading grammar splits on spaces and a single
  published form keeps parsers interchangeable.
- `<actor>` is as in 3.3.
- `<key>` matches `^[a-z][a-z0-9_]*$`; `<value>` matches
  `^[A-Za-z0-9_.:/@-]+$`. No spaces, no quoting in 0.1.

Example:

```markdown
## Comments

### 2026-09-13T03:40:00Z coder/1.4

Root cause: the form strips `!` before hashing.

### 2026-09-13T04:12:00Z human:sam kind=verdict result=changes_requested

Keep the strip for whitespace only. Add a test for the full punctuation set.
```

Comments are append-only. Producers MUST NOT edit or reorder existing
comments; a correction is a new comment. Order in the file is the
canonical order.

Two branches each appending here do not merge safely. See 7.1.

### 4.4 Comment files

The default form. One comment is one file, in one of two places:

```
comments/<issue-id>/<comment-id>.md    a comment on an issue
comments/<comment-id>.md               a standalone comment
```

A comment under an issue-id directory is about that issue. A comment
directly under `comments/` is standalone and MUST carry `about`
(section 3.4), naming what it concerns.

Standalone comments exist because not everything worth recording has a
lifecycle. "I checked this against the billing code and it holds",
"careful, this reads as more settled than it is" and "this is the good
one, use it" are all durable, attributable judgements with no state to
move through. Filing them as issues would mean creating an issue that
is born complete, which makes the column carry nothing.

- `<issue-id>`, when present, MUST be the id of an issue on the board.
  The directory is created on first use and never moves, because the
  issue's id does not change when the issue changes column.
- `<comment-id>` is a fresh id generated exactly as an issue id is
  (section 3.1): six characters of lowercase Crockford base32, random.

```markdown
---
type: comment
at: 2026-09-13T04:12:00Z
by: human:sam
kind: verdict
result: changes_requested
---

Keep the strip for whitespace only. Add a test for the full punctuation set.
```

- `type` is REQUIRED and MUST be `comment`.
- `at` is REQUIRED: an ISO 8601 datetime carrying `Z` or a numeric
  offset.
- `by` is REQUIRED: an actor as in 3.3.
- `kind` is OPTIONAL and free. These values have conventional meaning:
  `confirms` (checked, holds), `disputes` (this is wrong),
  `caution` (correct but misleading), `note` (neither).
- `about` is REQUIRED on a standalone comment and OPTIONAL otherwise.
- Any further keys carry what the inline grammar puts in `key=value`
  pairs. Unlike that grammar, values here are YAML and so may contain
  spaces.
- The body is the comment text, free CommonMark.

Comment files are create-only. Producers MUST NOT edit or delete one; a
correction is a new comment. Canonical order is by `at`, not by filename
and not by directory listing order.

A standalone comment:

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

To read an issue and its history with no tool:

```sh
cat issues/*/*-7k2x9m.md comments/7k2x9m/*.md
```

Two branches each adding a comment never conflict, because the filenames
differ. This is the property that makes concurrent issue creation safe
(section 3.1), applied one level down.

## 5. References

### 5.1 Referring to a record

A reference token is `<key>-<id>` or `<key>-<slug>-<id>`, where `<key>`
is the target board's `key` (section 2.1), `<id>` is the record's id
(section 3.1) and `<slug>`, when present, is the slug of the record's
filename at the time of writing: `app-7k2x9m`,
`app-encryption-disabled-unexpectedly-7k2x9m`. The key is always first
and the id always last.

Use a token in prose, commit messages, chat, and anywhere a reader may
not know which board is meant, including on the board being referenced.
Writers SHOULD use the slug-bearing form where a human will read the
text without the title beside it. The short form is sufficient where the
title is already stated or only tools will read it. Readers MUST accept
both.

A token resolves on `<key>` and `<id>` alone. The slug is advisory:
consumers MUST NOT use it to resolve, compare or reject a reference, and
a slug that no longer matches the filename does not invalidate the
reference. A tool MAY report the mismatch as a warning, and a validator
SHOULD, since a stale slug is a reader being misled rather than a
machine being broken.

A token matches:

```
^[a-z][a-z0-9]{1,15}(?:-[a-z0-9]+(?:-[a-z0-9]+)*)?-[0-9a-hjkmnp-tv-z]{6}$
```

and MUST be bounded on both sides by the start or end of the text or by
a character outside `[a-z0-9-]`. Because a key contains no hyphen and an
id is exactly six characters, the first segment is always the key and
the last always the id. So `login-7k2x9m` refers to a board keyed
`login`, never to a one-word slug on the current board. Tools MUST NOT
extract tokens from file paths.

Inside the frontmatter keys `parent`, `depends_on` and `related` the
value is the bare id, e.g. `7k2x9m`, for a record on the same board, or
`<key>-<id>` for any board. The slug form is not used there.

The bare id MUST NOT be used as a reference in prose. One id in 64 is
made only of hexadecimal characters and is indistinguishable from an
abbreviated commit hash, and a bare id gives a reader or a tool nothing
to recognise it by.

A board with no `key` cannot be referenced by token and has no
`resource`; `key` is therefore RECOMMENDED.

References MUST NOT be file paths, because paths change on every move.
Consumers resolve a reference by globbing `issues/*/*-<id>.md`.

The URI form is `oif:<key>/<id>`, the value of the issue's `resource`
key and of `about.resource` (section 3.4). The URI carries no slug.
Token and URI convert mechanically. A board publisher MAY make the URI
resolvable over HTTPS, e.g. `https://oif.md/<key>/<id>`, and SHOULD also
accept `https://oif.md/<key>/<slug>-<id>` by ignoring the slug.

A repository host with configurable autolinks can be given the prefix
`<key>-`, one prefix per referenced board, so that tokens render as
links. Where the host's suffix matcher accepts hyphens both forms link
as one unit and the target receives everything after the prefix, so the
target SHOULD resolve on the trailing id. Note that this is a paid
feature on some hosts, GitHub among them, so a specification MUST NOT
depend on it.

### 5.2 Finding records about a target

Records point at targets; targets do not point back (section 1.1). To
find what a board says about a file:

```sh
grep -rl -- 'docs/orders.md' <board>/
```

This is a scan of many small text files and costs milliseconds on
boards of a few thousand records. Existence is never stale, because
each record is the source of truth rather than a cache of one. If the
target was renamed, resolve the old name first with
`git log --follow -- <path>` and grep for both.

Consumers MUST NOT depend on any index of targets. A tool MAY
materialise one, on the same terms as an OKF `index.md` (section 9): it
is a convenience, never the source of truth, and it MUST NOT be written
outside the board root.

An agent will not run this unless its instructions say to. That is a
property of every tracker, not of this format. The recommended
instruction is to list the records about a file before acting on it.

## 6. Operations

| Operation | Mechanism |
|-----------|-----------|
| create    | write `issues/<column>/<slug>-<id>.md` with a fresh id |
| move      | `git mv` to another column directory |
| read      | `cat issues/*/*-<id>.md comments/<id>/*.md` |
| edit      | rewrite frontmatter or body, preserving unknown keys |
| comment   | write `comments/<issue-id>/<new-id>.md` (or, on an `inline` board, append under `## Comments`) |
| remark    | write `comments/<new-id>.md` with `about`, when there is no issue and no lifecycle |
| find      | `grep -rl -- '<path>' <board>/` |
| close     | move to a `complete` column; optionally set `resolution` |
| delete    | not an operation. Move to a hidden complete column instead |

## 7. Concurrency and merging

- Two branches creating issues never conflict: ids are random and
  filenames therefore differ.
- Two branches moving the same issue to different columns produce a git
  rename conflict. This is correct; it is a real disagreement.
- Two branches adding comments never conflict in the default form
  (4.4), because each comment is its own file. In the opt-in inline
  form they are **not safe**. See 7.1.

### 7.1 The concurrent-append hazard

When two branches each append a comment to the end of the same file,
git's diff finds common subsequences between the two additions. Comment
bodies written independently often share lines: a blank line, a list
item such as `- fix`, or a repeated sentence. The consequences,
both measured:

- With `merge=union`, the shared lines are emitted once and the two
  headings end up adjacent above a single body. **One comment's body is
  silently lost.** There is no conflict and no warning.
- With the default merge driver, the conflict markers surround only the
  differing heading lines while the shared body sits below as common
  context. The conflict *looks* trivial, so a resolver keeping both
  headings produces the same collapsed result.

Producers MUST NOT rely on `merge=union` for issue files. Earlier drafts
of this specification recommended it; that recommendation was wrong.

No arrangement of inline text avoids this. Git refines a conflict by
diffing the two sides against each other, so any line the two comments
happen to share is factored out as context, including blank lines and
lines inside a fenced block.

This hazard is why comment files (4.4) are the default form. A board
declaring `comments: inline` accepts that a concurrent append needs
manual resolution, and that the resolver has to compare bodies rather
than trusting a conflict that appears to involve only headings.

### 7.2 Why comment files solve it

Comment files (4.4) cannot collide: each carries a fresh random id, so
two branches write two different paths and git merges both with no
overlap to diff. Nothing is read, modified and written back, so there is
no window in which one writer's copy is stale.

The same reasoning produced random issue ids in 3.1. Anything appended
to a shared file by independent writers needs coordination; anything
created as its own file does not.

### 7.3 Migrating an existing board

Trackers being migrated from share a shape, and it maps onto this format
without loss:

| Source concept | OIF |
|---|---|
| Sequential key, e.g. `APP-38` | `aliases: [APP-38]`, and a fresh random id in the filename |
| Per-issue changelog or history list | One comment file per entry (section 4.4) |
| `status` or `column` field | The directory. Delete the field; it is reserved (section 3.2) |
| The tracker's own issue URL or number | `external_ids`, e.g. `{github: acme/app#412}` |
| A free-text closing report | A comment or a body section, not `resolution` |
| Assignee, labels, priority | `assignees`, `tags`, `priority` |

A history entry usually carries a timestamp, an actor and a description,
which is exactly what a comment file requires: `at`, `by`, and the body.
Anything else the source recorded, an event name for instance, rides
along as an additional frontmatter key, because consumers preserve keys
they do not recognise (section 3.2).

Derive each new id however you like, but derive it deterministically
from the source key if you intend to run the migration more than once;
otherwise a second run produces a second set of files.

## 8. Conformance

A conforming board:

1. has `board.md` with `type: board`, `oif` and `columns`;
2. has a directory with a `column.md` carrying `type: column` for every
   declared column, and no directory under `issues/` that is not a
   declared column;
3. has every issue file matching `^[a-z0-9]+(?:-[a-z0-9]+)*-[0-9a-hjkmnp-tv-z]{6}\.md$`;
4. has no duplicate ids. **Ids share one namespace across every record
   on a board**: no two issues, no two comments, and no issue and
   comment may carry the same id. This is what lets a comment's
   `resource` never collide with an issue's (section 9.1);
5. has frontmatter that parses as a YAML mapping, has `type: issue`, and
   contains none of `id`, `status`, `state`, `column`;
6. has every `parent`, `depends_on` and `related` reference resolvable
   within the board (cross-board references are not checked);
7. has `## Comments`, when present, as the last level-2 section, with
   every level-3 heading under it matching the comment grammar;
8. when `board.md` declares `kinds`, has every issue `kind` declared and
   every child's kind listed in its parent's `contains`;
9. has every file under `comments/` at either
   `comments/<issue-id>/<id>.md`, where `<issue-id>` is an id present on
   the board, or `comments/<id>.md`, in both cases carrying
   `type: comment` with `at` and `by`. A comment directory naming no
   existing issue is an error. A comment directly under `comments/`
   without `about` is an error;
10. has every `about` entry carrying `path` or `resource`, with
    `commit` matching `^[0-9a-f]{7,40}$` when present.

Validators SHOULD warn when an `about.path` names nothing at HEAD and
carries no `commit` to resolve it from. They MUST NOT fail on it: the
target may live in a repository the board does not contain.

Producers MUST NOT write outside the board root (section 1.1).

Producers MUST NOT write an inline comment to a board that does not
declare `comments: inline` (section 4.3). A board may nonetheless carry
inline comments written under an earlier setting, so that is a property
of the writer, not of the board: validators SHOULD warn when an inline
section appears on a board declaring `comments: sidecar`, and MUST NOT
fail on it.

A conforming consumer preserves unknown frontmatter keys, never edits
existing comments, and never reads state or identity from frontmatter.

## 9. Open Knowledge Format compatibility

OIF is built on the same substrate as Google's Open Knowledge Format
(OKF): a directory of Markdown files with YAML frontmatter, a required
`type`, the same actor convention, and the same rule that unknown keys
are preserved. `board.md`, every `column.md` and every issue file are
valid OKF concept documents by construction (`type: board`,
`type: column`, `type: issue`).

### 9.1 When an OIF board is an OKF bundle

An OIF board is a conforming OKF v0.2 bundle when:

1. the board root is the bundle root, and every non-reserved `.md` file
   under it carries frontmatter with a non-empty `type` (true for
   `board.md` and issues; any other Markdown placed under the board root
   must add a `type`);
2. comment files (4.4) carry `type: comment`, so they are OKF concepts
   too. A comment on an issue SHOULD carry
   `resource: oif:<key>/<issue-id>/<comment-id>`; a standalone comment
   SHOULD carry `resource: oif:<key>/<comment-id>`. The two-segment form
   cannot collide with an issue's `resource` (section 5.1), because ids
   are unique across every record on a board (section 8);
3. optionally, a root `index.md` carries `okf_version: "0.2"` to declare
   it. OKF index files carry no other frontmatter and their body is
   sections of bullet links to concepts, so board configuration MUST NOT
   be placed in an index file. A root index in that shape links
   `board.md` and each `column.md`; those paths never change, so it never
   goes stale. `oifmd index` generates one. Per-column indexes listing
   issues MAY be generated for OKF consumers but go stale on every move
   and are never relied on by OIF.

### 9.2 Field mapping

| OKF            | OIF            | Note |
|----------------|----------------|------|
| `type`         | `type: issue`  | fixed value, so OKF consumers can route all issues together |
| `title`        | `title`        | same |
| `description`  | `description`  | same, one sentence |
| `tags`         | `tags`         | same |
| `resource`     | `resource`     | `oif:<key>/<id>`, the stable identity |
| `status`       | absent         | OIF forbids it; OKF reads absence as `stable` |
| `generated`, `verified`, `sources` | passed through | optional provenance; `verified` reads naturally as review evidence |

### 9.3 Records about OKF concepts

An OIF record MAY be about an OKF concept. Put the concept's `resource`
in an `about` entry (section 3.4); it is the stable identifier, so it
survives the concept being moved, which a path does not.

OKF's `verified[]` records that an actor confirmed a concept, never what
they said. A standalone comment with `kind: confirms` or
`kind: disputes` carries the reasoning that `verified[]` has no room
for. The two compose: the comment is evidence, and a human or producer
may promote it into the concept's own frontmatter.

An OIF producer MUST NOT write `verified[]`, or any other key, into an
OKF concept. That follows from the write boundary (section 1.1), and it
keeps OKF's trust tiers derivable from the concept alone, as OKF
requires.

### 9.4 The one deliberate divergence

OKF defines a concept's identity as its path. In OIF the path carries
state, so an issue's OKF concept id changes on every move. OKF does not
specify identity stability and requires consumers to tolerate broken
links, so this does not break conformance, but a path link from another
concept to an issue dangles after a move.

The stable identity is the id in the filename, published as the
`resource` URI. Consumers that read OIF boards as OKF bundles SHOULD key
on `resource` before path. OIF proposes the same rule to OKF for any
concept that moves or is renamed.

## 10. Trademarks and independence

The Open Issue Format is an independent specification. It is not
affiliated with, endorsed by, or sponsored by Google or any other
organisation.

Section 9 describes compatibility with the Open Knowledge Format, which
Google Cloud publishes. References to that specification here are
descriptive: they say what this format is compatible with, in the sense
that "compatible with" ordinarily carries. Open Knowledge Format, OKF
and Google are the marks of their respective owners, and this
specification claims no rights in them.

Likewise the acronym OIF is used by others, including the Optical
Internetworking Forum, a networking consortium unrelated to this work.
Write "Open Issue Format (OIF)" on first mention.

## 11. Versioning

`board.md` declares the spec version in `oif`. Minor versions only add
optional keys and conventions. A key that becomes reserved is announced
one minor version before it is enforced.
