---
type: issue
resource: oif:oif/9m27dj
title: 'Importer: GitHub Issues export to OIF'
kind: task
priority: medium
requested_by: human:sean
created: 2026-09-13T05:00:00Z
---

Take `gh issue list --json` output, write one file per issue, keep `owner/repo#N` in `external_ids.github`, and each GitHub comment as a comment file under `comments/<issue-id>/`, with `by` following the actor convention.
