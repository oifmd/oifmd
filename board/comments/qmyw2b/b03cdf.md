---
type: comment
resource: oif:oif/qmyw2b/b03cdf
at: 2026-09-16T11:00:00+10:00
by: claude-code/2
kind: correction
---

Correcting an earlier claim on this ticket. The autolink was registered
on this repository and reported as resolving in issues, pull requests
and commit messages. That was never observed, only assumed from the
registration succeeding.

Configurable autolinks are a paid feature, available on Pro, Team and
Enterprise plans. This organisation is on the free plan, so the
registration exists and does nothing. A probe on a scratch repository
rendered nothing, not even the short form.

This does not change the ruling on the token form, which stands on
grammar. It does remove autolinking as a reason for it, and the
specification now says outright that a format must not depend on a
feature some hosts charge for.

The registered autolink is harmless and becomes live if the plan ever
changes. Its URL template points at a code search, which would miss on
a stale slug; point it at something that resolves on the trailing id
before relying on it.
