---
type: issue
resource: oif:oif/vzbc4r
title: Serve oif.md, because three shipped artifacts already link to it
kind: bug
priority: high
about:
  - path: pyproject.toml
  - path: README.md
  - path: skill/SKILL.md
created: 2026-09-15T16:00:00+10:00
---

`oifmd` is published on PyPI with `Homepage = https://oif.md`, the
README carries a Site line, and the agent skill tells a reader the spec
is at `https://oif.md/SPEC.md`. None of those resolve. An agent
following the skill's own link gets a dead fetch today.

Serve four paths and the bleeding stops:

- `/` — the skill rendered, including the bootstrap block, so an agent
  handed only the domain can act without a second fetch
- `/skill.md` — the skill raw, the curl target for `.claude/skills/oif/`
- `/SPEC.md` — the spec raw
- `/llms.txt` — a short index, for agents crawling rather than executing

Build from this repository so the site copies nothing. A second copy of
the spec will diverge from the first, and the copy people read will be
the stale one.

Independent of when this repository goes public.

## Acceptance Criteria

- [ ] `https://oif.md/` returns the skill with the bootstrap block
- [ ] `/skill.md` and `/SPEC.md` return raw markdown with a markdown content type
- [ ] `/llms.txt` exists
- [ ] Site content is generated from the repository, never hand-copied
