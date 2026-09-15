---
type: board
oif: "0.1"
key: ex
title: Minimal example board
columns:
  - name: backlog
  - name: doing
    wip: 2
  - name: done
    complete: true
kinds:
  - name: feature
    contains: [task, bug]
  - name: task
  - name: bug
---

# Minimal example board

Three columns, three issues, no tool required. Move an issue with
`git mv`. Create one by writing a file named `<slug>-<id>.md`.
