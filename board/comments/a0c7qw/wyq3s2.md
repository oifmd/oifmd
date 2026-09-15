---
type: comment
resource: oif:oif/a0c7qw/wyq3s2
at: 2026-09-15T21:02:00+10:00
by: claude-code/2
kind: finding
---

Migration has a shape and the documents made every adopter derive it.
The reporter worked out that a per-issue history list maps exactly onto
comment files — same three required keys, with the source's event name
riding along as an extra key — and noted they only found it by spotting
that the shapes matched.

Added as section 7.3 and a shorter version in the skill, with the
mapping table: sequential key to `aliases`, history entries to comment
files, `status` field deleted because the directory carries it, tracker
URL to `external_ids`, closing report to a comment rather than
`resolution`.

Also added a note to derive ids deterministically from the source key if
the migration might run twice, or a second run produces a second set of
files.
