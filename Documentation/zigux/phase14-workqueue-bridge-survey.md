# Phase 14 Workqueue Bridge Survey

This document records the bounded Phase 14 survey lane around `kernel/workqueue.c`.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_SLICE=workqueue-boundary-map-audit`
- scope: the landed `kernel/workqueue_bridge.zig` boundary map, its explicit stay-in-C decisions, its expanded concurrency audit outline, its pending-bit, delayed-work, and flush-color follow-up audits, its dedicated Phase 14 test gate and manifest, the shared Phase 14 build wiring, and the lane notes that compare the current packet against the roadmap
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

The highest-value honest step in this lane is therefore not to sketch a fake async runtime in Zig. It is to keep a reviewable boundary map that names submission, allocation, delayed-work, flush or drain, worker-pool, rescuer, and scheduler boundaries while explicitly keeping the coupled concurrency core in C.

## Survey findings

- `kernel/workqueue.c` is present on `master` and is large enough that even a minimal wrapper can easily overstate what Zigux owns if the boundary is not written down first.
- `kernel/workqueue_internal.h` makes the coupling visible: `struct worker`, `struct worker_pool`, and the scheduler-facing `wq_worker_running()` or `wq_worker_sleeping()` hooks expose exactly why this lane needs stay-in-C decisions before implementation claims.
- `lib/test_workqueue.c` shows there is already a kernel-side test surface around real execution behavior, which reinforces that the first Zigux artifact should be descriptive and reviewable rather than another runtime.
- the live repo already had `zigux/kernel/export_shim.zig`, which made a kernel-adjacent Phase 14 boundary-map file a natural next step without inventing a new namespace.
- the `kernel/workqueue_bridge.zig` starter stays intentionally narrow around boundary recording for submission routing, allocation and attrs, flush or cancel coordination, worker-pool concurrency ownership, and rescuer or scheduler hooks.
- the same bridge makes the roadmap-required stay-in-C packet explicit instead of leaving it implied by the boundary map alone: `manage_workers()`, the `worker_pool` state machine, `rescuer_thread()`, and the scheduler-facing `wq_worker_running()` or `wq_worker_sleeping()` hooks are all recorded as reviewable stay-in-C decisions.
- the bridge carries an expanded concurrency audit outline around `manage_workers()`, `worker_pool` forward-progress fields, the `__queue_work()` `max_active` gate, the `__queue_work()` `last_pool->lock` handoff, the `process_one_work()` unlock or relock execution window, the `worker_thread()` idle sleep transition, `rescuer_thread()`, and `wq_worker_running()` or `wq_worker_sleeping()`, still without claiming live execution ownership.
- the bridge now also audits `try_to_grab_pending()`, `queue_work_on()`, and the unbound `__queue_work()` `pwq->refcnt` retry path so pending-bit ownership and refcount retry rules are reviewable before any wrapper claims live submission control.
- the bridge now also audits `queue_delayed_work_on()`, `mod_delayed_work_on()`, `__queue_delayed_work()`, and `delayed_work_timer_fn()` so delayed enqueue aliases, timer-expiry handoff, and delayed requeue governance stay explicit while timer-base, CPU-affinity, and delayed-work requeue ownership remain in C.
- the bridge now also records the `__flush_workqueue()` color cascade, `start_flush_work()` barrier insertion, `pwq_dec_nr_in_flight()` release path, and `rescuer_thread()` mayday recovery handoff so active-color progression, chained flusher ownership, rescue wakeups, and regular-worker restart behavior remain reviewable without pretending a wrapper owns them.
- against the Phase 14 roadmap, the original workqueue boundary-map gap is now closed: Zigux has the required boundary map, a review-only concurrency audit, and explicit stay-in-C decisions. The remaining lane-local gap is narrower and still review-only: a shared checklist wording refresh should land before the later drain or cancel audit so reviewers see the same blocked-maintenance packet the survey and manifest already describe.

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
- landed `phase14-workqueue-pending-bit-followup`
- landed `phase14-workqueue-delayed-submission-alias-followup`
- landed `phase14-workqueue-delayed-timer-expiry-followup`
- landed `phase14-workqueue-delayed-requeue-governance`
- landed `phase14-workqueue-flush-drain-governance`
- landed `phase14-workqueue-rescuer-mayday-governance`
- reviewer-facing drift: `Documentation/zigux/review-checklist.md` still needs to describe this current blocked-maintenance packet instead of the older workqueue story
- ready-next `phase14-workqueue-drain-cancel-followup`
- blocked `phase14-workqueue-live-execution-blocker`

This keeps the lane explicit without overstating progress: Zigux has already closed the roadmap-level workqueue boundary-map gap with a real Phase 14 boundary map, explicit stay-in-C decisions, and review-only concurrency audits for submission, delayed-work, flush-color, and rescuer ownership. What remains open inside this lane is narrower: the shared checklist wording still lags the current packet, the drain or cancel audit is still pending right after that reviewer-facing repair, and Zigux still does not claim live worker-pool execution, scheduler-hook parity, hotplug rebinding, or a direct `kernel/workqueue.c` rewrite.

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

First realign `Documentation/zigux/review-checklist.md` with this current blocked-maintenance packet so reviewers see the same delayed-work, flush-color, and stay-in-C boundaries the survey and manifest already carry. After that, stay in this same workqueue lane and audit `drain_workqueue()`, `__flush_work()`, and `__cancel_work_sync()` so the bridge records reflush looping, single-work barrier waiting, and cancellation completion boundaries before any wrapper claims draining or cancellation parity. The remaining blocker after those review-only steps is unchanged: Zigux still does not own live worker-pool execution, delayed-work requeue control, scheduler callbacks, rescuer behavior, CPU-hotplug migration, or unbound topology rebinding for `kernel/workqueue.c`.
