# Phase 14 Workqueue Boundary Map

This note records a bounded Phase 14 review surface for `kernel/workqueue.c`.

## Status

- `PHASE14_STATUS=workqueue_boundary_map_landed`
- `PHASE14_LANE_KEY=P14-L02`
- `PHASE14_SCOPE=kernel/workqueue bridge boundary mapping`
- `PHASE14_POSTURE=study_only_wrapper_first`
- read against current `master` governance reminders on `2026-05-22`

## Why this slice exists

The roadmap keeps `kernel/workqueue.c` in the study-only bucket. That means Phase 14 work should map the boundary, isolate a future wrapper seam, and make the stay-in-C decision explicit for the risk-heavy parts instead of implying delivery readiness.

This slice gives the lane one reviewable artifact that future bridge work can reuse without reopening the whole deep-core concurrency discussion from scratch.

## Roadmap basis

- `kernel/workqueue.c` is a core-adjacent boundary-study target first, not a rewrite target
- the allowed Phase 14 posture is wrapper-first or study-only, not direct parity claims
- any future `kernel/workqueue_bridge.zig` work must stay smaller than the worker-pool scheduler, concurrency policy, rescue-worker lifecycle, and flush/cancel execution core

## Boundary map

### Keep in C

- worker-pool creation, destruction, and global lifecycle
- worker wakeup, parking, rescue, and concurrency-management internals
- flush, cancel, drain, and barrier execution semantics
- CPU-hotplug, freezer, reclaim, and lock-order interactions
- delayed-work timer coordination and requeue ordering

### Candidate wrapper-first seam

- queue request classification at the API boundary
- explicit queue target selection metadata
- non-owning shape checks for `work_struct`, `delayed_work`, and queue flags
- argument normalization for a future bridge contract that still hands execution back to C immediately

### Future bridge contract constraints

- any bridge must stay metadata-only on first entry
- the bridge may validate shape, flags, and queue-selection intent, but it must not own worker execution
- the bridge must treat `schedule_work*`, `queue_work*`, `mod_delayed_work*`, `flush_*`, and cancel paths as distinct call families with different rollback expectations
- no Phase 14 follow-up may present queue completion, wakeup policy, timer ownership, or forward-progress guarantees as Zig-owned behavior

## Current bounded recommendation

The smallest honest future bridge seam is a contract layer that describes queue-submission intent without moving scheduling or worker execution out of C.

That means the first future code-facing follow-up should be a boundary descriptor or wrapper contract around submission metadata, not a queue runner, worker abstraction, timer rewrite, or drain/flush helper port.

## Anchors that must stay aligned

- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `kernel/workqueue.c`
- future-only reference: `kernel/workqueue_bridge.zig`

## Non-goals

This slice does not claim:

- a shipped `kernel/workqueue_bridge.zig`
- permission to move workqueue execution, timers, flush/cancel semantics, or worker-pool ownership into Zig
- parity evidence for `kernel/workqueue.c`
- an Architecture Council decision to move this anchor beyond study-only posture

## Next bounded step

Keep this note parked until one narrower follow-up is justified:

- a metadata-only wrapper contract for queue-submission intent
- a call-family audit that separates submission, delayed-work, and flush/cancel surfaces
- a validator that keeps this boundary map aligned with the freeze-map and study-only accounting notes
