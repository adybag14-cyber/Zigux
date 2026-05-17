# Phase 13 devres scatterlist helper slice

This slice adds one helper-first scatterlist planner beside the existing `lib/devres.zig` and `lib/devres_dma_coherent.zig` packet.

## Scope

- anchor: `lib/devres.c`
- Zigux helper: `lib/devres_scatterlist.zig`
- focused replay: `zigux/tests/phase13_devres_scatterlist.zig`
- lane intent: keep one reviewable scatterlist bookkeeping foothold without widening into live DMA-backed execution or live `sg_*` traversal

## What landed

- `DevresScatterlistHelper.descriptor()` names the same `lib/devres.c` anchor while keeping `touches_live_dma = false` and `touches_live_scatterlist = false`
- `planManagedScatterlistMap()` models a helper-first retained-record decision around original segment count, mapped segment count, and detach-time unmap readiness
- `planManagedScatterlistUnmap()` keeps the release match exact across original and mapped segment counts so the detach bookkeeping surface stays reviewable
- the focused replay proves success retention, zero-segment cleanup, impossible over-mapped cleanup, allocation failure, and exact-versus-mismatched unmap matching

## Non-goals

- no live `dma_map_sgtable()` or `dma_unmap_sgtable()` execution
- no `struct scatterlist`, `sg_table`, or `sg_*` iteration helpers
- no live DMA ownership, merge, chaining, or detach-time scatter-gather cleanup beyond the helper-first bookkeeping plan
