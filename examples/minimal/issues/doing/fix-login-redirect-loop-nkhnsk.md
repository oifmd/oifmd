---
type: issue
resource: oif:ex/nkhnsk
title: Login form rejects passwords containing "!"
kind: bug
priority: high
assignees:
- coder/1.4
requested_by: human:sam
tags:
- auth
depends_on: []
created: 2026-09-13T03:10:00Z
external_ids:
  github: acme/app#412
---

Submitting a correct password with `!` clears the form and shows
"invalid credentials". Expected: login succeeds.

## Acceptance Criteria

- [x] Reproduce with a failing test
- [ ] Fix without changing the hashing path
- [ ] Reviewer verdict recorded
