---
type: issue
resource: oif:oif/r1gnqs
title: Propose a stable concept identity field to the OKF spec
kind: task
priority: high
requested_by: human:sean
created: 2026-09-13T06:00:00Z
---

OKF defines concept identity as the file path and tolerates broken
links, but says nothing about concepts that move or are renamed. OIF
boards move files on every status change and anchor identity in
`resource`. File an issue on the OKF repository proposing that
consumers key on `resource` before path, with `previous_paths` as an
optional trail.

## Acceptance Criteria

- [ ] Issue filed on GoogleCloudPlatform/open-knowledge-format
- [ ] `external_ids.github` recorded here
- [ ] Outcome reflected in SPEC.md section 9
