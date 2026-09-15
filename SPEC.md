# Open Issue Format (OIF) — Specification

**Version:** 0.1 (draft)
**Status:** starting point, not a finished standard. Expect 0.x to move.
**License:** Apache-2.0

OIF is a file format for issues, tasks, tickets and work items that live
in a git repository. It is designed so that any agent or human with
`ls`, `cat` and `git mv` can run a board with no tool installed.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be
interpreted as described in RFC 2119.

## 1. Principle: the filesystem is the record

| Layer       | Carries                      | Mechanism            |
|-------------|------------------------------|----------------------|
| Directory   | workflow state (the column)  | `git mv`             |
| Filename    | identity (slug + id)         | fixed at creation    |
| Frontmatter | attributes                   | YAML                 |
| Body        | prose, criteria, comments    | CommonMark           |

Neither state nor identity appears in frontmatter. They therefore cannot
disagree with the filesystem, and a state change is a single atomic
rename rather than a read-modify-write.

## 2. Board layout

```
<board>/
├── board.md            the board: ordered columns, kinds, charter
├── index.md            OPTIONAL, OKF entry point, see section 9
└── issues/
    ├── backlog/
    │   └── column.md   the column: what belongs here, exit criteria
    ├── doing/
    │   └── column.md
    └── done/
        └── column.md
```

- `board.md` is REQUIRED. Its frontmatter declares the board; its body is
  free text (charter, working agreements, anything).
- `issues/` is REQUIRED. Each direct subdirectory is a column.
- Every declared column MUST have a directory, and every column directory
  MUST contain a `column.md` (section 2.2). Git does not track empty
  directories; the column file keeps an empty column present, and it is
  what an arriving agent reads first.
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
key: app              # OPTIONAL. Board key for cross-board references.
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
- `key`, when present, MUST match `^[a-z][a-z0-9]{1,15}$`.
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
  identifiers such as `app-2753` are valid *aliases* (see 3.2) and are
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
| `description`  | string              | One sentence. The body is the full description. |
| `kind`         | string              | Free. Common: `task`, `bug`, `feature`, `epic`. |
| `priority`     | string              | Free. Common: `critical`, `high`, `medium`, `low`. |
| `assignees`    | list of actor       | See 3.3. |
| `requested_by` | actor               | |
| `tags`         | list of string      | |
| `parent`       | issue ref           | See 5. |
| `depends_on`   | list of issue ref   | This issue cannot complete until these do. |
| `related`      | list of issue ref   | Undirected. |
| `created`      | ISO 8601 datetime   | RECOMMENDED. MUST carry `Z` or a numeric offset. Git history is not reliable after import. |
| `due`          | ISO 8601 date/time  | |
| `resolution`   | string              | Only meaningful in a `complete` column. Common: `fixed`, `duplicate`, `wontfix`. |
| `aliases`      | list of string      | Other names this issue answers to, e.g. legacy sequential keys. |
| `external_ids` | map string→string   | Keys are system names (`github`, `jira`, …). |

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

### 4.3 Comments

If present, `## Comments` MUST be the last level-2 section in the file.
Each comment is a level-3 heading matching this grammar, followed by
free text up to the next level-3 heading or end of file:

```
### <timestamp> <actor>[ <key>=<value>]*
```

- `<timestamp>` is ISO 8601 with a `Z` or numeric offset.
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

## 5. References

An issue reference is:

- the bare id, e.g. `7k2x9m`, when referring within the same board;
- `<key>-<id>`, e.g. `app-7k2x9m`, when referring across boards, where
  `<key>` is the target board's `key`.

References MUST NOT be file paths, because paths change on every move.
Consumers resolve a reference by globbing `issues/*/*-<id>.md`.

The URI form of a reference is `oif:<key>/<id>`, which is the value of
the issue's `resource` key. A board publisher MAY make it resolvable
over HTTPS, e.g. `https://oif.md/<key>/<id>` redirecting to the file's
current location.

In prose, commit messages and chat, use the same tokens.

## 6. Operations

| Operation | Mechanism |
|-----------|-----------|
| create    | write `issues/<column>/<slug>-<id>.md` with a fresh id |
| move      | `git mv` to another column directory |
| edit      | rewrite frontmatter or body, preserving unknown keys and existing comments |
| comment   | append a comment block under `## Comments` |
| close     | move to a `complete` column; optionally set `resolution` |
| delete    | not an operation. Move to a hidden complete column instead |

## 7. Concurrency and merging

- Two branches creating issues never conflict: ids are random and
  filenames therefore differ.
- Two branches moving the same issue to different columns produce a git
  rename conflict. This is correct; it is a real disagreement.
- Two branches appending comments to the same issue are **not safe** in
  the inline form. See 7.1.

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

Boards that expect concurrent commenting SHOULD use the sidecar form
(7.2). Boards that do not MAY use the inline form, understanding that a
concurrent append needs manual resolution and that the resolver has to
check bodies, not just headings.

### 7.2 Sidecar comments

In the sidecar form, comments are files keyed by the issue's id:

```
<board>/
├── comments/
│   └── 7k2x9m/
│       ├── k3n2wp.md
│       └── q8v4jd.md
└── issues/doing/fix-login-7k2x9m.md
```

- The directory under `comments/` is the issue's id, which never
  changes, so moving an issue between columns remains a single rename
  and the comments do not move with it.
- Each comment file is named `<id>.md` with a fresh id generated the
  same way as an issue id (section 3.1).
- Frontmatter carries `type: comment`, `at` (ISO 8601 datetime with an
  offset) and `by` (an actor, section 3.3). Any further keys are the
  `key=value` pairs of the inline grammar.
- The body is the comment text.
- Order is by `at`, not by filename.

Two branches adding comments never conflict, because the filenames
differ. This is the same property that makes concurrent issue creation
safe, applied one level down.

A board MAY carry both forms; consumers reading a full comment history
MUST merge the inline section and the sidecar directory, ordered by
timestamp.

## 8. Conformance

A conforming board:

1. has `board.md` with `type: board`, `oif` and `columns`;
2. has a directory with a `column.md` carrying `type: column` for every
   declared column, and no directory under `issues/` that is not a
   declared column;
3. has every issue file matching `^[a-z0-9]+(?:-[a-z0-9]+)*-[0-9a-hjkmnp-tv-z]{6}\.md$`;
4. has no duplicate ids;
5. has frontmatter that parses as a YAML mapping, has `type: issue`, and
   contains none of `id`, `status`, `state`, `column`;
6. has every `parent`, `depends_on` and `related` reference resolvable
   within the board (cross-board references are not checked);
7. has `## Comments`, when present, as the last level-2 section, with
   every level-3 heading under it matching the comment grammar;
8. when `board.md` declares `kinds`, has every issue `kind` declared and
   every child's kind listed in its parent's `contains`.

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
2. optionally, a root `index.md` carries `okf_version: "0.2"` to declare
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

### 9.3 The one deliberate divergence

OKF defines a concept's identity as its path. In OIF the path carries
state, so an issue's OKF concept id changes on every move. OKF does not
specify identity stability and requires consumers to tolerate broken
links, so this does not break conformance, but a path link from another
concept to an issue dangles after a move.

The stable identity is the id in the filename, published as the
`resource` URI. Consumers that read OIF boards as OKF bundles SHOULD key
on `resource` before path. OIF proposes the same rule to OKF for any
concept that moves or is renamed.

## 10. Versioning

`board.md` declares the spec version in `oif`. Minor versions only add
optional keys and conventions. A key that becomes reserved is announced
one minor version before it is enforced.
