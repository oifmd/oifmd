# Changelog

## 0.1 (draft)

First public draft. A starting point rather than a finished standard;
expect 0.x to move.

- **The format.** Directory as workflow state, filename as identity
  (slug plus a random six-character id), YAML frontmatter for
  attributes, CommonMark body, references by id rather than path.
- **Records are about things.** An optional `about` list on an issue or
  comment names what it concerns: a repo-relative `path`, a `commit`
  pinning the revision reviewed, or a `resource` when the target carries
  a stable id. One record may name several targets.
- **Standalone comments.** Not everything worth recording has a
  lifecycle. A comment at `comments/<id>.md` with `about` records a
  judgement with no work attached, rather than an issue born complete.
  Conventional `kind` values: `confirms`, `disputes`, `caution`, `note`.
- **Write boundary.** Producers write only under the board root, never
  modifying a target and never placing a file beside one. A board can
  therefore describe a repository nobody on the board owns. Discovery
  runs from the board, by grep or `oifmd about`, not from the target.
- **Comments are files**, one per comment, at
  `comments/<issue-id>/<comment-id>.md`. Keyed by identity rather than
  path, so an issue changing column leaves its comments untouched. A
  board may opt into the older inline form with `comments: inline` in
  `board.md`; consumers read both.
- **Board vocabulary.** `board.md` declares ordered columns and,
  optionally, the `kinds` an issue may have and which kinds may contain
  which. The specification names no hierarchy of its own. Ready boards
  for Kanban, Scrum and Shape Up ship in `profiles/`.
- **References in prose are `<key>-<id>`**, e.g. `app-7k2x9m`, on the
  same board as well as across boards. A bare id is reserved for the
  frontmatter reference keys, where the key name says what the value is.
  One id in 64 is all hexadecimal and reads as an abbreviated commit
  hash, and the token form also autolinks on hosts that support a
  configurable prefix.
- **Open Knowledge Format compatibility.** A board is a conforming OKF
  v0.2 bundle: `type` on every file, OKF's actor convention, OKF's
  unknown-key rule. `resource: oif:<key>/<id>` carries the stable
  identity. The one deliberate divergence is documented in section 9.
- **Tooling.** A validator with no dependency beyond a YAML parser, JSON
  schemas for each file type, and a portable agent skill that works in
  any harness reading the Agent Skills convention.

### Why comments are files, and a note for anyone who saw a draft

An earlier draft recommended `.gitattributes` with `merge=union` on
issue files. **Do not use it.** When two branches each append a comment
and the bodies share any line, including a blank line or a list item,
git emits the shared lines once and one comment's body is lost with no
conflict raised. The default merge driver is no safer: it marks only the
heading lines as conflicting while the shared body sits below as common
context, so the obvious resolution collapses two comments into one.

Section 7.1 documents the hazard. Section 7.2 defines sidecar comments,
files keyed by issue id, which cannot conflict.
