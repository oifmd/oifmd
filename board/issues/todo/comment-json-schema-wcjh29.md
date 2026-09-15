---
type: issue
resource: oif:oif/wcjh29
title: JSON Schema for comment files
kind: task
priority: medium
created: 2026-09-15T14:30:00+10:00
---

`schema/` has board, column and issue schemas but none for comment
files, which section 4.4 made a first-class file type. Add
`comment.schema.json` covering `type: comment`, the timestamp and actor
keys, `resource`, and free additional properties.

## Acceptance Criteria

- [ ] `schema/comment.schema.json` exists and matches SPEC.md 4.4
- [ ] Referenced from the schema index or README
