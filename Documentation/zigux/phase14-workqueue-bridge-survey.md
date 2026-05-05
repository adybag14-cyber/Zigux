# Phase 14 Workqueue Bridge Survey

This document records the bounded Phase 14 survey lane around `kernel/workqueue.c`.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_LANE_KEY=P14-L01`
- `PHASE14_SURVEYED_COMMIT=9e278f632d6d5097cb8cfc2dc61744ae105baa8c`
- `PHASE14_SLICE=workqueue-delayed-submission-alias-audit`
- scope: the landed `kernel/workqueue_bridge.zig` boundary map plus its expanded concurrency audit outline and new pending-bit, retry, and delayed-submission alias checkpoints, its dedicated Phase 14 test gate and manifest, the shared Phase 14 build wiring, and the lane notes that compare the new foothold against the roadmap
- product boundary:
  - `kernel/workqueue_bridge.zig`
  - `zigux/tests/phase14_workqueue_bridge.zig`
  - `zigux/tests/phase14_workqueue_bridge_manifest.json`
  - `zigux/tests/phase14_build.zig`
  - `Documentation/zigux/phase14-workqueue-bridge-slice.md`
  - `Documentation/zigux/phase14-workqueue-bridge-survey.md`

## Why this slice exists

The Phase 14 roadmap explicitly names `kernel/workqueue.c` as a boundary-study target and calls for boundary maps, concurrency audits, explicit stay-in-C decisions, and a wrapper-first or study-only posture.

That matters because the live `kernel/workqueue.c` anchor is already 8,439 lines, its internal header adds more worker and scheduler coupling, and the nearby `lib/test_workqueue.c` surface still depends on real kernel execution behavior. The file mixes queue submission, pool routing, worker creation and culling, flush and cancel sequencing, delayed work, rescuer handling, CPU hotplug behavior, scheduler callbacks, watchdog-style progress checks, affinity or pod layout choices, and debug or statistics plumbing.

The highest-value honest step in this lane is therefore not to sketch a fake async runtime in Zig. It is to add a reviewable boundary map that names the submission, allocation, flush or cancel, worker-pool, and rescuer or scheduler boundaries while explicitly keeping the coupled concurrency core in C.

## Survey findings

- `kernel/workqueue.c` is present on `master` and is large enough that even a minimal wrapper can easily overstate what Zigux owns if the boundary is not written down first.
- `kernel/workqueue_internal.h` makes the coupling visible: `struct worker`, `struct worker_pool`, and the scheduler-facing `wq_worker_running()` or `wq_worker_sleeping()` hooks expose exactly why this lane needs stay-in-C decisions before implementation claims.
- `lib/test_workqueue.c` shows there is already a kernel-side test surface around real execution behavior, which reinforces that the first Zigux artifact should be descriptive and reviewable rather than another runtime.
- the live repo already had `zigux/kernel/export_shim.zig`, which made a kernel-adjacent Phase 14 boundary-map file a natural next step without inventing a new namespace.
- the new `kernel/workqueue_bridge.zig` starter stays intentionally narrow around boundary recording for submission routing, allocation and attrs, flush or cancel coordination, worker-pool concurrency ownership, and rescuer or scheduler hooks.
- the bridge now carries an expanded concurrency audit outline around `manage_workers()`, `worker_pool` forward-progress fields, the `__queue_work()` `max_active` gate, the `try_to_grab_pending()` plus `queue_work_on()` pending-bit claim handoff, the unbound `__queue_work()` `pwq->refcnt` retry path, the delayed-submission alias fan-in through `queue_delayed_work_on()`, `mod_delayed_work_on()`, and `__queue_delayed_work()`, the `__queue_work()` `last_pool->lock` handoff, the `process_one_work()` unlock or relock execution window, the `worker_thread()` idle sleep transition, `rescuer_thread()`, and `wq_worker_running()` or `wq_worker_sleeping()`, still without claiming live execution ownership.
- the next honest workqueue-facing step is a delayed timer-expiry handoff audit around `delayed_work_timer_fn()` and `__queue_work()` so the lane names timer-driven submission ownership before any wrapper claims live delayed-work execution.

## Recorded gaps

The current lane state is:

- landed `phase14-build-gate`
- landed `phase14-make-target`
- landed `phase14-kernel-export-shim-foundation`
- landed `phase14-workqueue-boundary-map-starter`
- landed `phase14-workqueue-test-gate`
- landed `phase14-workqueue-slice-note`
- landed `phase14-workqueue-survey-note`
- landed `phase14-workqueue-concurrency-audit-outline`
- landed `phase14-workqueue-max-active-audit`
- landed `phase14-workqueue-pending-bit-followup`
- landed `phase14-workqueue-delayed-submission-alias-followup`
- landed `phase14-workqueue-lock-handoff-audit`
- ready-next `phase14-workqueue-delayed-timer-expiry-followup`
- blocked `phase14-workqueue-live-execution-blocker`

This keeps the lane explicit without overstating progress: Zigux now has a real Phase 14 boundary map for workqueue ownership and non-goals, but it still does not claim live worker-pool execution, scheduler-hook parity, or a direct `kernel/workqueue.c` rewrite.

## Non-goals

This survey slice does not claim:

- worker creation or idle-cull logic
- pool wakeup, busy hashing, or forward-progress behavior
- delayed-work timers or CPU hotplug behavior
- rescuer execution
- scheduler hook parity
- flush, cancel, or draining correctness
- a direct `kernel/workqueue.c` port

## Gates

1. run the dedicated Phase 14 build
- `zig build test --build-file zigux/tests/phase14_build.zig`

2. run the convenience target
- `make -C zigux phase14`

## Next bounded step

Stay in the Phase 14 workqueue lane and add one tiny `kernel/workqueue_bridge.zig` delayed timer-expiry audit next, limited to `delayed_work_timer_fn()` and its handoff into `__queue_work()` so the bridge records timer-driven submission ownership before any wrapper leaves the current boundary-map-only posture.
