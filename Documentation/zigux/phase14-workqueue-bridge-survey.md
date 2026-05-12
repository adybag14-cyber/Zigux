# Phase 14 Workqueue Bridge Survey

This document records the bounded Phase 14 survey lane around `kernel/workqueue.c`.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_SLICE=workqueue-boundary-map-audit`
- scope: the landed `kernel/workqueue_bridge.zig` boundary map, its explicit stay-in-C decisions, its expanded concurrency audit outline, its dedicated Phase 14 test gate and manifest, the shared Phase 14 build wiring, and the lane notes that compare the current packet against the roadmap
- product boundary:
  - `kernel/workqueue_bridge.zig`
  - `zigux/tests/phase14_workqueue_bridge.zig`
  - `zigux/tests/phase14_workqueue_bridge_manifest.json`
  - `zigux/tests/phase14_build.zig`
  - `Documentation/zigux/phase14-workqueue-bridge-slice.md`
  - `Documentation/zigux/phase14-workqueue-bridge-survey.md`

## Why this slice exists

The Phase 14 roadmap explicitly names `kernel/workqueue.c` as a boundary-study target and calls for boundary maps, concurrency audits, explicit stay-in-C decisions, and a wrapper-first or study-only posture.

That matters because the live `kernel/workqueue.c` anchor is already 8,439 lines, its internal header adds more worker and scheduler coupling, and the nearby `lib/test_workqueue.c` surface still depends on real kernel execution behavior.

The file mixes queue submission, pool routing, worker creation and culling, flush and cancel sequencing, delayed work, rescuer handling, CPU hotplug behavior, scheduler callbacks, watchdog-style progress checks, affinity or pod layout choices, and debug or statistics plumbing.

The highest-value honest step in this lane is therefore not to sketch a fake async runtime in Zig. It is to keep a reviewable boundary map that names submission, allocation, delayed-work, flush or cancel, worker-pool, rescuer, and scheduler boundaries while explicitly keeping the coupled concurrency core in C.

## Survey findings

- `kernel/workqueue.c` is present on `master` and is large enough that even a minimal wrapper can easily overstate what Zigux owns if the boundary is not written down first.
- `kernel/workqueue_internal.h` makes the coupling visible: `struct worker`, `struct worker_pool`, and the scheduler-facing `wq_worker_running()` or `wq_worker_sleeping()` hooks expose exactly why this lane needs stay-in-C decisions before implementation claims.
- `lib/test_workqueue.c` shows there is already a kernel-side test surface around real execution behavior, which reinforces that the first Zigux artifact should be descriptive and reviewable rather than another runtime.
- the live repo already had `zigux/kernel/export_shim.zig`, which made a kernel-adjacent Phase 14 boundary-map file a natural next step without inventing a new namespace.
- the `kernel/workqueue_bridge.zig` starter stays intentionally narrow around boundary recording for submission routing, allocation and attrs, flush or cancel coordination, worker-pool concurrency ownership, and rescuer or scheduler hooks.
- the same bridge makes the roadmap-required stay-in-C packet explicit instead of leaving it implied by the boundary map alone: `manage_workers()`, the `worker_pool` state machine, `rescuer_thread()`, and the scheduler-facing `wq_worker_running()` or `wq_worker_sleeping()` hooks are all recorded as reviewable stay-in-C decisions.
- the bridge carries an expanded concurrency audit outline around `manage_workers()`, `worker_pool` forward-progress fields, the `__queue_work()` `max_active` gate, the `__queue_work()` `last_pool->lock` handoff, the `process_one_work()` unlock or relock execution window, the `worker_thread()` idle sleep transition, scheduler hook state transitions, and the rescuer mayday handoff, still without claiming live execution ownership.
- the bridge still frames `try_to_grab_pending()`, `queue_work_on()`, and the unbound `__queue_work()` `pwq->refcnt` retry path as the next audit step rather than a landed checkpoint, which keeps pending-bit ownership and refcount retry rules explicitly parked in the review-only backlog.
- the bridge still keeps delayed-work timer-base ownership, flush completion, draining, cancellation completion, and rescuer execution inside the stay-in-C boundary packet; those areas are named as boundary surfaces, but they are not yet recorded as separate landed follow-up audits.
- against the Phase 14 roadmap, the original workqueue boundary-map gap is now closed: Zigux has the required boundary map, a review-only concurrency audit, and explicit stay-in-C decisions. The remaining lane-local gap is narrower and still review-only: the next bounded step is the pending-bit audit already named in the slice note, while the live execution blocker remains unchanged afterward.

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
- landed `phase14-workqueue-lock-handoff-audit`
- ready-next `phase14-workqueue-pending-bit-audit`
- blocked `phase14-workqueue-live-execution-blocker`

This keeps the lane explicit without overstating progress: Zigux has already closed the roadmap-level workqueue boundary-map gap with a real Phase 14 boundary map, explicit stay-in-C decisions, and review-only concurrency audits for submission routing, allocation, flush or cancel boundaries, manager or scheduler ownership, and the current eight-checkpoint audit outline. What remains open inside this lane is narrower: the pending-bit audit is next, and Zigux still does not claim live worker-pool execution, scheduler-hook parity, hotplug rebinding, or a direct `kernel/workqueue.c` rewrite.

## Non-goals

This survey slice does not claim:

- worker creation or idle-cull logic
- pool wakeup, busy hashing, or forward-progress behavior
- delayed-work timer-base ownership or CPU-hotplug rebinding
- rescuer execution ownership
- scheduler hook parity
- flush, cancel, or draining correctness
- a direct `kernel/workqueue.c` port

## Gates

1. run the dedicated Phase 14 build
- `zig build test --build-file zigux/tests/phase14_build.zig`

2. run the convenience target
- `make -C zigux phase14`

## Next bounded step

Stay in this same workqueue lane and audit `try_to_grab_pending()`, `queue_work_on()`, and the unbound `__queue_work()` `pwq->refcnt` retry path so the bridge records pending-bit ownership and refcount retry rules before any wrapper leaves the current boundary-map-only posture. The remaining blocker after that review-only step is unchanged: Zigux still does not own live worker-pool execution, delayed-work requeue control, scheduler callbacks, rescuer behavior, CPU-hotplug migration, or unbound topology rebinding for `kernel/workqueue.c`.
