# Changelog

## 0.1 (draft)

First public draft. A starting point rather than a finished standard;
expect 0.x to move.

- **The format.** Directory as workflow state, filename as identity
  (slug plus a random six-character id), YAML frontmatter for
  attributes, CommonMark body, append-only comments under a timestamped
  heading grammar, references by id rather than path.
- **Board vocabulary.** `board.md` declares ordered columns and,
  optionally, the `kinds` an issue may have and which kinds may contain
  which. The specification names no hierarchy of its own. Ready boards
  for Kanban, Scrum and Shape Up ship in `profiles/`.
- **Open Knowledge Format compatibility.** A board is a conforming OKF
  v0.2 bundle: `type` on every file, OKF's actor convention, OKF's
  unknown-key rule. `resource: oif:<key>/<id>` carries the stable
  identity. The one deliberate divergence is documented in section 9.
- **Tooling.** A validator with no dependency beyond a YAML parser, JSON
  schemas for each file type, and a portable agent skill that works in
  any harness reading the Agent Skills convention.

### A note for anyone who saw a pre-release draft

An earlier draft recommended `.gitattributes` with `merge=union` on
issue files. **Do not use it.** When two branches each append a comment
and the bodies share any line, including a blank line or a list item,
git emits the shared lines once and one comment's body is lost with no
conflict raised. The default merge driver is no safer: it marks only the
heading lines as conflicting while the shared body sits below as common
context, so the obvious resolution collapses two comments into one.

Section 7.1 documents the hazard. Section 7.2 defines sidecar comments,
files keyed by issue id, which cannot conflict.
