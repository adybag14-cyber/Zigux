# Phase 14 Workqueue Bridge Survey

This document records the bounded Phase 14 survey lane around `kernel/workqueue.c`.

## Status

- `PHASE14_STATUS=blocked_maintenance`
- `PHASE14_LANE_KEY=P14-L02`
- `PHASE14_SURVEYED_COMMIT=9b98d3b9c812840bf279508030be0b8de093736c`
- `PHASE14_SLICE=workqueue-scheduler-visible-worker-state-refinement`
- scope: the landed `kernel/workqueue_bridge.zig` boundary map plus its expanded concurrency audit outline, the delayed timer-expiry handoff audit, the delayed-work requeue stay-in-C decision, the explicit runtime `max_active` retuning boundary, the explicit flush-drain governance note, the explicit hotplug-topology rebinding note, the explicit scheduler-visible worker-state note, the explicit rescuer or mayday stay-in-C note, its dedicated Phase 14 test gate and manifest, the shared Phase 14 build wiring, and the lane notes that compare the new foothold against the roadmap
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

The highest-value honest step in this lane is therefore not to sketch a fake async runtime in Zig. It is to add a reviewable boundary map that names the submission, allocation, runtime `max_active` retuning, flush or cancel, worker-pool, hotplug-topology, and rescuer or scheduler boundaries while explicitly keeping the coupled concurrency core in C.

## Survey findings

- `kernel/workqueue.c` is present on `master` and is large enough that even a minimal wrapper can easily overstate what Zigux owns if the boundary is not written down first.
- `kernel/workqueue_internal.h` makes the coupling visible: `struct worker`, `struct worker_pool`, and the scheduler-facing `wq_worker_running()` or `wq_worker_sleeping()` hooks expose exactly why this lane needs stay-in-C decisions before implementation claims.
- `lib/test_workqueue.c` shows there is already a kernel-side test surface around real execution behavior, which reinforces that the first Zigux artifact should be descriptive and reviewable rather than another runtime.
- the live repo already had `zigux/kernel/export_shim.zig`, which made a kernel-adjacent Phase 14 boundary-map file a natural next step without inventing a new namespace.
- the new `kernel/workqueue_bridge.zig` starter stays intentionally narrow around boundary recording for submission routing, allocation and attrs, runtime `max_active` retuning ownership, worker-pool concurrency ownership, explicit flush-drain governance, explicit hotplug-topology rebinding governance, and rescuer or scheduler hooks.
- the bridge now carries an expanded concurrency audit outline around `manage_workers()`, `worker_pool` forward-progress fields, the `__queue_work()` `max_active` gate, the separate `workqueue_set_max_active()` plus `pwq_adjust_max_active()` reconfiguration window, the `try_to_grab_pending()` plus `queue_work_on()` pending-bit claim handoff, the unbound `__queue_work()` `pwq->refcnt` retry path, the delayed-submission alias fan-in through `queue_delayed_work_on()`, `mod_delayed_work_on()`, and `__queue_delayed_work()`, the delayed timer-expiry handoff through `delayed_work_timer_fn()` and back into `__queue_work()`, the explicit `mod_delayed_work_on()` delayed-work requeue governance point, the `__flush_workqueue()` plus `drain_workqueue()` active-color ownership seam, the scheduler-visible worker-state transitions around `WORKER_NOT_RUNNING`, `pool->nr_running`, and idle wakeups, the `__queue_work()` `last_pool->lock` handoff, the `process_one_work()` unlock or relock execution window, the `worker_thread()` idle sleep transition, and `rescuer_thread()` plus the `wq->maydays` or `pwq->mayday_cursor` mayday handoff, still without claiming live execution ownership.
- the current honest posture is blocked maintenance rather than another wrapper claim: Zigux now records the delayed-work requeue governance note, the explicit runtime `max_active` retuning boundary, the flush-drain governance note, the hotplug-topology rebinding boundary, the explicit scheduler-visible worker-state note, and the explicit rescuer or mayday note, but worker execution, flush completion, rescuer execution, and the live rebinding path still stay in C.

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
- landed `phase14-workqueue-delayed-timer-expiry-followup`
- landed `phase14-workqueue-delayed-requeue-governance`
- landed `phase14-workqueue-flush-drain-governance`
- landed `phase14-workqueue-lock-handoff-audit`
- landed `phase14-workqueue-rescuer-mayday-governance`
- blocked `phase14-workqueue-live-execution-blocker`

This keeps the lane explicit without overstating progress: Zigux now has a real Phase 14 boundary map for workqueue ownership and non-goals, plus explicit delayed-work requeue, runtime `max_active` retuning, flush-drain, hotplug-topology, and scheduler-visible worker-state stay-in-C decisions, but it still does not claim live worker-pool execution, scheduler-hook parity, delayed-work requeue ownership in Zig, runtime `max_active` retuning ownership in Zig, flush completion ownership in Zig, hotplug rebinding ownership in Zig, or a direct `kernel/workqueue.c` rewrite.

## Non-goals

This survey slice does not claim:

- worker creation or idle-cull logic
- pool wakeup, busy hashing, or forward-progress behavior
- runtime `max_active` retuning ownership
- timer-base ownership, delayed-work requeue behavior, or CPU hotplug behavior
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

Leave this lane in blocked maintenance unless a future run can tighten one equally small rescuer or mayday stay-in-C note without claiming live delayed-work execution, hotplug rebinding ownership, runtime `max_active` retuning ownership, or flush completion.
