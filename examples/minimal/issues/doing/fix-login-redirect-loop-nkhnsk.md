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

## Comments

### 2026-09-13T03:40:00Z coder/1.4

Root cause: the form strips `!` before hashing. Fix in `LoginForm.svelte`.

### 2026-09-13T04:12:00Z human:sam kind=verdict result=changes_requested

Keep the strip for whitespace only. Add a test for the full punctuation set.
