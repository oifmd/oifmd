---
type: issue
resource: oif:oif/a0c7qw
title: First external migration, 41 issues, and what it found
kind: bug
priority: high
resolution: fixed
created: 2026-09-15T21:00:00+10:00
about:
  - path: SPEC.md
  - path: skill/SKILL.md
  - path: src/oifmd/cli.py
---

An agent migrated a 41-issue board onto OIF and reported back. First use
by anyone outside this repository, and it found a spec-versus-validator
gap plus four places the documents assume knowledge the reader does not
have.

Fixed here. See the comments for each finding.

## Acceptance Criteria

- [x] Shared id namespace stated in section 8, which section 9.1 already relied on
- [x] Validator enforces it, verified against the reporter's exact case
- [x] A migration section in both the spec and the skill
- [x] Skill and spec agree on which keys are required
- [x] `resolution` constrained to a token, with two validator warnings
- [x] Block-mapping guidance so frontmatter is not collapsed onto one line
