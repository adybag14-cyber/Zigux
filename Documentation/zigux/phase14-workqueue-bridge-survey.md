# Phase 14 Workqueue Bridge Survey

This document records the bounded Phase 14 survey lane around `kernel/workqueue.c`.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_SLICE=workqueue-blocked-maintenance`
- `PHASE14_LANE_KEY=P14-L02`
- `PHASE14_SURVEYED_COMMIT=542acd7b12c52211ef9a8bd790fa2e2b3367cbf0`
- `PHASE14_STATUS_BUCKET=study_only`
- `PHASE14_ROLLBACK_OWNER=Repo Tooling Pod`
- `PHASE14_REVIEW_BLOCKER_STATUS=blocked_on_stay_in_c_evidence`
- scope: the landed `kernel/workqueue_bridge.zig` boundary map plus its expanded concurrency audit outline and new flush-color, barrier-insertion, in-flight release, drain-or-cancel, disable-or-delayed-cancel, delayed-submission alias, and delayed-timer handoff checkpoints, its dedicated Phase 14 test gate and manifest, the shared Phase 14 build wiring, and the lane notes that compare the new foothold against the roadmap
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

The highest-value honest step in this lane was not to sketch a fake async runtime in Zig. It was to add a reviewable boundary map that names the submission, allocation, flush or cancel, worker-pool, and rescuer or scheduler boundaries while explicitly keeping the coupled concurrency core in C, and the current review task is to keep that study packet aligned as the audit grows.

This packet now states its guardrails directly instead of relying on the shared smoke packet alone: the workqueue bridge remains `study_only`, `kernel/workqueue.c` stays the source of truth, the rollback owner remains `Repo Tooling Pod`, and any future edit that weakens explicit stay-in-C wording for worker pools, scheduler hooks, delayed timers, rescuer execution, or hotplug migration should fall back to blocked maintenance rather than advancing the bridge into new behavior claims.

## Survey findings

- `kernel/workqueue.c` is present on `master` and is large enough that even a minimal wrapper can easily overstate what Zigux owns if the boundary is not written down first.
- `kernel/workqueue_internal.h` makes the coupling visible: `struct worker`, `struct worker_pool`, and the scheduler-facing `wq_worker_running()` or `wq_worker_sleeping()` hooks expose exactly why this lane needs stay-in-C decisions before implementation claims.
- `lib/test_workqueue.c` shows there is already a kernel-side test surface around real execution behavior, which reinforces that the first Zigux artifact should be descriptive and reviewable rather than another runtime.
- the live repo already had `zigux/kernel/export_shim.zig`, which made a kernel-adjacent Phase 14 boundary-map file a natural next step without inventing a new namespace.
- the new `kernel/workqueue_bridge.zig` starter stays intentionally narrow around boundary recording for submission routing, allocation and attrs, flush or cancel coordination, worker-pool concurrency ownership, and rescuer or scheduler hooks.
- the bridge now carries an expanded concurrency audit outline around `manage_workers()`, `worker_pool` forward-progress fields, the `__queue_work()` `max_active` gate, the irq-disabled `try_to_grab_pending()` or `queue_work_on()` PENDING-bit claim window, the unbound `__queue_work()` `pwq->refcnt` retry loop, the `__queue_work()` `last_pool->lock` handoff, the `__flush_workqueue()` flush-color cascade, the `start_flush_work()` barrier insertion path, the `pwq_dec_nr_in_flight()` in-flight release path, the `drain_workqueue()` or `__flush_work()` or `__cancel_work_sync()` reflush-and-cancel checkpoint, the disable-depth and delayed-cancel sync checkpoint around `__cancel_work()`, `clear_pending_if_disabled()`, `__cancel_work_sync()`, and `cancel_delayed_work_sync()`, the delayed-wrapper alias checkpoint around `disable_delayed_work()`, `disable_delayed_work_sync()`, and `enable_delayed_work()`, the delayed-submission alias checkpoint around `queue_delayed_work_on()`, `mod_delayed_work_on()`, and `__queue_delayed_work()`, the newly landed delayed timer-expiry checkpoint around `delayed_work_timer_fn()` and its handoff back into `__queue_work()`, the `process_one_work()` unlock or relock execution window, the `worker_thread()` idle sleep transition, `rescuer_thread()`, and `wq_worker_running()` or `wq_worker_sleeping()`, still without claiming live execution ownership.
- the delayed timer handoff audit now closes the last review-only ready-next step in this workqueue packet; what remains is blocked live execution and ownership work that still belongs in C.

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
- landed `phase14-workqueue-pending-bit-audit`
- landed `phase14-workqueue-flush-color-followup`
- landed `phase14-workqueue-drain-cancel-followup`
- landed `phase14-workqueue-disable-delayed-followup`
- landed `phase14-workqueue-delayed-disable-wrapper-followup`
- landed `phase14-workqueue-delayed-submission-alias-followup`
- landed `phase14-workqueue-delayed-timer-handoff-followup`
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
- reclassifying this packet out of `study_only` without fresh stay-in-C evidence and rollback-ready review text
- a direct `kernel/workqueue.c` port

## Gates

1. run the dedicated Phase 14 build
- `zig build test --build-file zigux/tests/phase14_build.zig`

2. run the convenience target
- `make -C zigux phase14`

## Next bounded step

Leave this lane in blocked maintenance unless the shared Phase 14 smoke packet or this workqueue survey drifts. Any reopen should stay review-only and keep timer-base, CPU-affinity, and requeue ownership in C.
