---
type: board
oif: "0.1"
key: kan
title: Kanban
columns:
  - name: backlog
  - name: ready
  - name: doing
    wip: 3
  - name: review
    wip: 2
  - name: done
    complete: true
---

# Kanban

Flow-based. No iterations, no hierarchy. `kind` is free text; use it or
leave it out. Limit work in progress and pull from the right.
