# Changelog

## oifmd 0.1.0.dev1 (package)

The validator, not the specification. `0.1.0.dev0` accepted a board the
specification forbids: an issue and a comment sharing an id. It also
rendered a project page with broken links and no install instruction.

- Ids are checked across issues and comments, not within each.
- A reference token naming this board resolves, or it is an error.
  `depends_on: [app-zzzzzz]` on board `app` previously passed.
- `kinds` entries are checked against the board's own declarations.
- Warnings where the specification asks for them: an `about` path that
  names nothing at HEAD with no commit to resolve from, `resolution`
  outside a complete column or holding prose, a board with no `key`.
- Timestamps are checked against the published grammar, not merely for a
  trailing offset.
- Project metadata: keywords, classifiers, documentation and changelog
  links, and a project page whose links work.

## 0.1 (draft)

First public draft. A starting point rather than a finished standard;
expect 0.x to move, and expect 0.1 itself to keep moving until it is
marked stable. The version in `board.md` stays `0.1` through that.

One change since first publication tightened conformance rather than
extending it: an id must now be unique across issues *and* comments,
where previously a comment could reuse an issue's id. Section 11 says
minor versions only add, so this is an exception, taken while the draft
had no known implementers and worth naming rather than hiding. Anything
comparable after 0.1 is marked stable will wait for 0.2.

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
- **A reference may carry the slug**: `app-7k2x9m` or
  `app-encryption-disabled-unexpectedly-7k2x9m`. Only the key and the
  trailing id resolve it; the slug is for the reader and may go stale
  without breaking anything. Because a key holds no hyphen and an id is
  exactly six characters, the first segment is always the key and the
  last always the id, so there is no second way to parse a token.
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
