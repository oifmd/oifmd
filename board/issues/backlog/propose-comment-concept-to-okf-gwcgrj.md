---
type: issue
resource: oif:oif/gwcgrj
title: Propose a Comment concept to OKF, after evidence
kind: task
priority: low
created: 2026-09-15T14:30:00+10:00
---

OKF has no way to record what a reviewer said about a concept. Its
`verified[]` carries only `{by, at}`, so it records that someone
confirmed something but never their reasoning, and the spec explicitly
declines to store subjective scores in `sources[]`. `log.md` is
per-directory prose with no attribution structure. The nearest live
proposal is `open-knowledge-format#13`, which adds `refuted[]` with a
one-line `reason` and covers only the negative case.

The gap: a knowledge corpus agents keep regenerating needs somewhere a
human can durably say "this table is wrong" or "I checked this and it
holds", attributed and machine-readable, that survives the next
regeneration because nothing rewrites it.

Proposed shape, an ordinary OKF concept in a sidecar tree:

- `type: Comment`
- `about`: one `sources`-shaped entry with the target's stable id, its
  path as a fallback hint, and which revision was reviewed
- `assessment`: `confirms` / `disputes` / `note`. A verb enum, not a
  quality score; OKF already rejects subjective scores as unportable
- `generated: {by, at}` for authorship, reusing OKF's own key
- `in_reply_to` as a plain link for threading

Critically, comments must NOT move trust tiers. OKF section 11 says
consumers derive tiers only from specified fields. A comment is
evidence; a producer or human promotes it into `verified` or `refuted`
on the target. Otherwise an agent could downgrade a concept by
commenting.

**Do not file yet.** Blocked on the identity proposal landing, since a
comment pointing at a path-identified concept is the most fragile
inbound link in a bundle. Also blocked on running OIF boards long enough
to report real counts: concurrent-append saves, rename dangles. The
upstream culture rewards measurements over designs; maintainers are
near-silent on issues and the one community spec pull request closed
unmerged, so peer convergence with evidence is what moves things.

## Acceptance Criteria

- [ ] Identity proposal filed and its reception assessed
- [ ] Comment frontmatter aligned to OKF vocabulary
- [ ] Evidence gathered from running boards
- [ ] Issue filed citing prior art, with `external_ids.github` recorded here
