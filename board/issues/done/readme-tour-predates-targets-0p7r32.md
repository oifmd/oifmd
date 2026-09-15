---
type: issue
resource: oif:oif/0p7r32
title: The README tour predates targets and standalone comments
kind: task
priority: medium
about:
  - path: README.md
created: 2026-09-15T15:30:00+10:00
---

The sixty-second tour shows a board of issues about nothing in
particular. Now that a record can name what it is about, the tour should
show an issue pointing at a file, because that is the part no other
git-native tracker does.

## Acceptance Criteria

- [x] The tour shows `about` in the worked example
- [x] The standalone comment form appears
- [x] `oifmd about <path>` appears as the discovery command
