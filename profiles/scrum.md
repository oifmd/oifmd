---
type: board
oif: "0.1"
key: scr
title: Scrum
columns:
  - name: backlog
  - name: sprint
  - name: doing
  - name: review
  - name: done
    complete: true
kinds:
  - name: epic
    contains: [story]
  - name: story
    contains: [task, bug]
  - name: task
  - name: bug
---

# Scrum

Epics contain stories, stories contain tasks and bugs. Put `milestone`
in frontmatter to name the sprint; it round-trips as an unknown key
until a later spec version names it.
