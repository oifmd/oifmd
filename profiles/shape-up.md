---
type: board
oif: "0.1"
key: shp
title: Shape Up
columns:
  - name: raw
  - name: shaped
  - name: betting_table
  - name: building
    wip: 2
  - name: shipped
    complete: true
  - name: dropped
    complete: true
    hidden: true
kinds:
  - name: pitch
    contains: [scope]
  - name: scope
    contains: [task]
  - name: task
---

# Shape Up

Pitches are bet on, scopes are carved during the cycle, tasks fall out
of scopes. Unbet pitches go to `dropped`, not `backlog`.
