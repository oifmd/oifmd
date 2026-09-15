# Changelog

## 0.1 (draft, unreleased)

- Initial specification: directory-as-state, filename-as-identity,
  frontmatter attributes, CommonMark body, append-only comment grammar,
  reference syntax, merge guidance, conformance rules.
- JSON Schema for `board.md` and issue frontmatter.
- Minimal validator (`python -m oifmd validate <board>`).
- OKF compatibility: `type: issue` and `type: board` required, `tags`
  and `description` adopt OKF names, `resource: oif:<key>/<id>` as the
  stable identity, mandatory prose-only `index.md` per column, section 9
  rewritten as the compatibility profile with the identity divergence
  stated.
- `column.md` (`type: column`) replaces the per-column index as the
  required placeholder, because OKF index files carry no frontmatter and
  must be link listings. `oifmd index` generates an OKF-shaped root
  index that never goes stale.
- **Removed the `merge=union` recommendation.** Measured: when two
  branches append comments whose bodies share any line, union merge
  emits the shared lines once and silently drops one comment's body.
  The default driver is no better, marking only the heading lines as
  conflicting while the shared body sits below as common context, so a
  resolver keeping both headings collapses two comments into one.
  Section 7.1 documents the hazard; 7.2 adds sidecar comments, files
  keyed by issue id, which cannot conflict.
- Optional `kinds` in `board.md`: a per-board vocabulary for `kind` with
  containment rules, validated when declared. `profiles/` ships ready
  boards for Kanban, Scrum and Shape Up.
