# Phase 14 Workqueue Allocation And Attributes Boundary Audit

This note records a narrow wrapper-first audit step for the `kernel/workqueue.c` bridge packet.

## Status

- `PHASE14_LANE_KEY=P14-L02`
- `PHASE14_PHASE=Phase 14`
- `PHASE14_ANCHOR=kernel/workqueue.c`
- `PHASE14_STATUS=blocked_maintenance`
- `PHASE14_SCOPE=allocation-and-attrs`
- `PHASE14_POSTURE=study_only_boundary_map`

## Why this audit exists

The current `kernel/workqueue_bridge.zig` packet already exposes `allocation-and-attrs` as one of the two `boundary_map_only` footholds. This audit keeps that seam explicit and reviewable without widening runtime ownership.

The point is narrow:

- keep `__alloc_workqueue()` explicit as the primary allocation anchor
- keep `devm_alloc_workqueue()` explicit as the device-managed lifetime companion
- keep flag shaping, ordered-workqueue rules, rescuer policy, affinity shaping, and lifetime ownership in C
- avoid presenting allocation helpers as proof that worker execution, rescuer execution, or scheduler-visible behavior moved into Zig

## Current readback contract

This audit is aligned with the directly readable bridge packet when all of the following stay true:

- `kernel/workqueue_bridge.zig` keeps `allocation-and-attrs` in the boundary map
- `kernel/workqueue_bridge.zig` keeps `allocation-and-attrs` in the wrapper candidate packet
- the ownership for that seam remains `boundary_map_only`
- the anchor symbols remain `__alloc_workqueue` and `devm_alloc_workqueue`
- the blocked-by wording continues to keep rescuer policy, ordered-workqueue rules, affinity shaping, and lifetime ownership in C

## Non-goals

This audit does not claim:

- a live allocator wrapper
- a Zig-owned rescuer policy
- a Zig-owned ordered-workqueue policy
- a status change for `kernel/workqueue.c`

## Replay

- `python3 scripts/zigux/check-phase14-workqueue-allocation-attrs-boundary.py --self-test`
- `python3 scripts/zigux/check-phase14-workqueue-allocation-attrs-boundary.py`

## Next bounded step

Keep this seam in blocked maintenance unless the workqueue bridge drops the explicit `allocation-and-attrs` wrapper-first foothold or narrower stay-in-C evidence appears around allocation metadata without implying live worker execution ownership.
