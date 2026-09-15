---
type: issue
resource: oif:oif/41469f
title: Minimal Python validator
kind: task
priority: high
requested_by: human:sean
created: 2026-09-13T05:00:00Z
---

A single-module validator with no dependency beyond PyYAML that checks the conformance list in SPEC.md section 8 and exits non-zero on error.

## Acceptance Criteria

- [x] `python -m oifmd validate examples/minimal` passes
- [x] `python -m oifmd validate .` passes on this repository
