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

## Governance For Freeze-Map Changes
- changes to either list require an explicit Architecture Council decision with written rationale
- any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate, and rollback owner in the reviewable record for that lane
- direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change

## Stay-In-C Policy
- the existing C implementation remains the product source of truth for every freeze-in-C anchor
- allowed near-term Zigux work on those anchors is limited to survey notes, boundary manifests, validation gates, and explicit non-goal records
- wrapper-first or helper-first experiments may continue only for study-only anchors, and they still must keep scheduler, MM, RCU, skbuff, and other deep-core ownership explicit
- if validation is incomplete, contradictory, or too weak to justify a status change, keep the code in C and record the blocker

## Policy
- deep-core files do not become sprint targets by enthusiasm alone
- research is allowed
- product commitments require explicit gates, validation, and ownership
- if evidence is not overwhelming, keep the code in C and document why
