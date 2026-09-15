---
type: comment
resource: oif:oif/vzbc4r/9g3ntp
at: 2026-09-15T16:20:00+10:00
by: claude-code/2
kind: progress
result: live
---

`https://oif.md` serves, with a certificate issued and HTTPS enforced.
The github.io address now redirects here, so the links already shipped
in the PyPI metadata and the agent skill resolve.

Verified on the real domain: the root page as HTML, the spec and skill
as `text/markdown`, the schemas as JSON, both `llms` files, and the
brand images. The root page carries the whole bootstrap, so an agent
handed only the domain can create a board without a second fetch.

The site is generated from this repository on every push rather than
committed, so it cannot drift from the specification it publishes.
