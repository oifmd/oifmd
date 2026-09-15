---
type: issue
resource: oif:oif/3y12nn
title: JavaScript validator published as @oifmd/oifmd on npm (bin oifmd)
kind: task
priority: low
requested_by: human:sean
created: 2026-09-13T05:00:00Z
---

Same conformance checks as the Python package so JS-native agent tooling can validate without Python.

Unscoped `oifmd` is refused by npm's similarity filter with a 403
against the existing `oxfmt`. `oif-md` normalises to the same string, so
do not retry unscoped; the filter re-evaluates every new unscoped name
against the whole registry and offers no dry-run check.

The bin stays `oifmd`, so `npx @oifmd/oifmd validate .` and
`oifmd validate .` both match the Python CLI. Keeping the package name
equal to the scope also satisfies npm's bin-selection rule permanently:
`npm exec` picks the bin whose name equals the package name minus the
scope, so a second bin can be added later without breaking `npx`.
