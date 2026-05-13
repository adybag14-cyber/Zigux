# Phase 14 Workqueue Bridge Survey

This document records the bounded Phase 14 survey lane around `kernel/workqueue.c`.

## Status

- `PHASE14_STATUS=blocked_maintenance`
- `PHASE14_LANE_KEY=P14-L04`
- `PHASE14_SURVEYED_COMMIT=9b98d3b9c812840bf279508030be0b8de093736c`
- `PHASE14_SLICE=workqueue-scheduler-visible-worker-state-refinement`
- scope: the landed `kernel/workqueue_bridge.zig` boundary map, its expanded review-only concurrency audit, its explicit stay-in-C governance packet for delayed-work requeue, hotplug topology rebinding, runtime `max_active` retuning, worker-pool concurrency, rescuer or scheduler ownership, and the coupled Phase 14 survey or manifest surfaces

## Why this slice exists

The Phase 14 roadmap treats `kernel/workqueue.c` as a boundary-study target first. The honest product move is still a reviewable bridge with explicit stay-in-C decisions, not a fake async runtime or a direct port.

That remains true because the anchor mixes submission routing, delayed-work timer ownership, flush and drain color accounting, worker creation and culling, rescuer handling, scheduler-visible worker state, and hotplug-driven topology rebinding.

## Current packet state

The live `kernel/workqueue_bridge.zig` packet is already beyond the older eight-checkpoint starter. The bridge now records:

- the original manager-role, forward-progress, `max_active`, lock-handoff, execution-window, idle-sleep, scheduler-hook, and rescuer-mayday checkpoints
- the landed `phase14-workqueue-pending-bit-followup`
- the landed `phase14-workqueue-delayed-submission-alias-followup`
- the landed `phase14-workqueue-delayed-timer-expiry-followup`
- the landed `phase14-workqueue-delayed-requeue-governance`
- the landed `phase14-workqueue-flush-drain-governance`
- the landed `phase14-workqueue-rescuer-mayday-governance`

The bridge and its direct Zig test now describe a blocked maintenance packet with eight boundary areas, fifteen review-only audit checkpoints, and seven blocked live behaviors. That means the lane is no longer waiting on the pending-bit audit itself. The remaining work is to keep the survey, manifest, slice note, and shared Phase 14 reminder surfaces truthful about the bridge that is already landed.

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
- blocked `phase14-workqueue-live-execution-blocker`

This keeps the lane explicit without overstating progress. Zigux still does not claim live worker-pool execution, delayed-work requeue control, scheduler callback parity, rescuer execution ownership, hotplug migration, runtime `max_active` retuning ownership, or a direct `kernel/workqueue.c` rewrite.

## Non-goals

This survey slice does not claim:

- live worker creation or idle cull logic
- runtime `max_active` retuning ownership
- delayed-work timer-base ownership outside the review-only note
- flush, drain, or cancellation completion ownership
- scheduler callback parity
- rescuer execution ownership
- hotplug-driven worker migration or unbound topology rebinding ownership
- a direct `kernel/workqueue.c` port

## Gates

1. run the dedicated Phase 14 build
- `zig build test --build-file zigux/tests/phase14_build.zig`
- `make -C zigux phase14-test`

2. run the convenience target
- `make -C zigux phase14`

## Next bounded step

Leave this lane in blocked maintenance unless the shared Phase 14 smoke packet or this workqueue survey drifts. Any reopen should stay review-only and keep the flush-drain active-color governance note, timer-base ownership, CPU affinity, delayed-work requeue ownership, the runtime `max_active` retuning boundary, and live execution in C.
