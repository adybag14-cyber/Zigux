# Zigux Freeze Map

This file records code that should not move into active Zigux delivery without an explicit Architecture Council decision.

## Freeze In C Initially
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Policy
- deep-core files do not become sprint targets by enthusiasm alone
- research is allowed
- product commitments require explicit gates, validation, and ownership
- if evidence is not overwhelming, keep the code in C and document why
