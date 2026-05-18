# Phase 14 Workqueue Bridge Slice

This note records the current bounded workqueue bridge packet for the Core-Adjacent Pod.

## Status

  * `PHASE14_LANE_KEY=P14-L04`
  * `PHASE14_PHASE=Phase 14`
  * `PHASE14_ANCHOR=kernel/workqueue.c`
  * `PHASE14_STATUS=blocked_maintenance`
  * `PHASE14_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement`
  * `PHASE14_POSTURE=study_only_boundary_map`
  * `PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`
  * `PHASE14_DIRECT_ZIG_TEST=zigux/tests/phase14_workqueue_bridge.zig`
  * `PHASE14_MANIFEST=zigux/tests/phase14_workqueue_bridge_manifest.json`

## Why this slice exists

Phase 14 keeps `kernel/workqueue.c` in a wrapper-first, study-only posture. The shipped bridge and manifest already name the current blocked-maintenance packet, but the packet also needs a bridge-local note that says plainly which bounded audit step is current and which runtime behaviors still stay in C.

This slice stays intentionally narrow. It records the currently landed scheduler-visible worker-state refinement and the reviewability surfaces that keep the workqueue boundary packet honest. It does not claim live execution ownership, a new wrapper, or any status change for the anchor.

## Current bounded packet

The directly landed workqueue packet currently consists of:

  * `kernel/workqueue_bridge.zig`
  * `zigux/tests/phase14_workqueue_bridge.zig`
  * `zigux/tests/phase14_workqueue_reviewability.zig`
  * `zigux/tests/phase14_workqueue_bridge_manifest.json`

This slice note exists to keep those files aligned on the same current bounded step:

  * `phase14-workqueue-scheduler-visible-worker-state-refinement`
  * lane `P14-L04`
  * status `blocked maintenance`
  * anchor `kernel/workqueue.c`

## Current bounded findings

The bridge packet now carries explicit review-only coverage for:

  * queue submission routing through `queue_work_on()` and `__queue_work()`
  * delayed-work timer expiry and delayed requeue governance
  * flush and drain color progression
  * rescuer mayday handoff
  * hotplug topology rebinding
  * scheduler-visible worker-state transitions around `wq_worker_running()` and `wq_worker_sleeping()`

That is enough to keep the workqueue anchor reviewable as a bounded boundary-study packet. It is not enough to claim live ownership over worker execution, callback dispatch, scheduler parity, runtime `max_active` retuning, hotplug migration, or delayed-work control.

## Reviewability contract

Keep the following facts aligned across the bridge, manifest, reviewability test, and shared Phase 14 smoke packet:

  * the workqueue packet remains in blocked maintenance
  * the current slice id remains `phase14-workqueue-scheduler-visible-worker-state-refinement`
  * `zigux/tests/phase14_workqueue_reviewability.zig` remains the bridge-local reviewability surface
  * the live blocker remains `phase14-workqueue-live-execution-blocker`
  * the next broader same-lane step is still a packet-local reread, not a live execution port

## Non-goals

This slice does not claim:

  * a live `kernel/workqueue.zig`
  * callback execution ownership
  * delayed-work timer ownership
  * flush or drain completion ownership
  * scheduler hook ownership
  * rescuer-thread ownership
  * hotplug-driven worker migration ownership

## Next bounded step

Keep the packet in blocked maintenance and reread `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, and the shared Phase 14 smoke packet together before widening scope.
