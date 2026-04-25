# Phase 14 Workqueue Bridge Survey

This document records the bounded Phase 14 survey lane around `kernel/workqueue.c`.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_SLICE=workqueue-boundary-map-starter`
- scope: the landed `kernel/workqueue_bridge.zig` boundary map, its dedicated Phase 14 test gate and manifest, the shared Phase 14 build wiring, and the lane notes that compare the new foothold against the roadmap
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
- the live `kernel/workqueue_bridge.zig` slice stays intentionally narrow around boundary recording for submission routing, allocation and attrs, flush or cancel coordination, worker-pool concurrency ownership, and rescuer or scheduler hooks.
- the bridge now includes a bounded concurrency audit checklist around `manage_workers()`, `pool->lock` ownership, the mayday-to-rescuer path, and `wq_worker_running()` or `wq_worker_sleeping()` pairing, which closes the earlier stale note that still described the audit surface as only future work.
- the next honest workqueue-facing step is to tighten one field-level audit note around forward-progress state, `WORKER_NOT_RUNNING`, and the narrowest lock-domain wording, still without claiming live execution ownership.

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
- ready-next `phase14-workqueue-field-audit-followup`
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

Stay in the Phase 14 workqueue lane and tighten one tiny `kernel/workqueue_bridge.zig` field-level audit note next, limited to forward-progress state, `WORKER_NOT_RUNNING`, and the narrowest `pool->lock` wording before any wrapper leaves the current boundary-map-only posture.
