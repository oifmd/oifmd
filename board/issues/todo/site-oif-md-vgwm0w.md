---
type: issue
resource: oif:oif/vgwm0w
title: Publish oif.md from docs/ with raw spec and llms.txt
kind: task
priority: high
requested_by: human:sean
created: 2026-09-13T05:00:00Z
---

GitHub Pages from `docs/` with the CNAME for oif.md. Agents fetch
rather than browse, so serve SPEC.md raw at a stable URL and publish an
`llms.txt` that points at it.

## Acceptance Criteria

- [ ] https://oif.md renders README content
- [ ] https://oif.md/SPEC.md returns the spec as text/markdown
- [ ] https://oif.md/llms.txt exists
