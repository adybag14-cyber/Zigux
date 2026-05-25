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

  * exactly two `boundary_map_only` bridge areas: queue submission routing through `queue_work_on()` and `__queue_work()`, plus allocation and attribute shaping through `__alloc_workqueue()` and `devm_alloc_workqueue()`
  * delayed-work timer expiry and delayed requeue governance
  * flush and drain color progression
  * cancellation completion handoff through `__cancel_work_sync()`, `disable_work()`, and `__flush_work()`
  * rescuer mayday handoff
  * hotplug topology rebinding
  * scheduler-visible worker-state transitions around `wq_worker_running()` and `wq_worker_sleeping()`

That is enough to keep the workqueue anchor reviewable as a bounded boundary-study packet. It is not enough to claim live ownership over worker execution, callback dispatch, flush, drain, or cancellation completion, delayed-work requeue control, runtime `max_active` retuning, scheduler-visible worker-state parity, rescuer execution, or hotplug migration and topology rebinding.

The current roadmap-aligned gap is therefore narrow and explicit: the boundary-map foothold is landed, but it is intentionally small. Every other named workqueue bridge area stays in the stay-in-C audit packet until the freeze-map posture changes or genuinely narrower evidence appears.

## Reviewability contract

Keep the following facts aligned across the bridge packet, manifest, reviewability test, the shared review checklist, and the directly coupled slice and survey notes:

  * the workqueue packet remains in blocked maintenance
  * the current slice id remains `phase14-workqueue-scheduler-visible-worker-state-refinement`
  * `zigux/tests/phase14_workqueue_reviewability.zig` remains the bridge-local reviewability surface
  * the explicit cancel-path handoff keeps cancellation completion review-only and in C
  * `Documentation/zigux/review-checklist.md` continues to route reviewers back through the same blocked-maintenance workqueue packet instead of implying a live wrapper or execution claim
  * the live blocker remains `phase14-workqueue-live-execution-blocker`
  * the next same-lane step is still a packet-local reread until the bridge-local blocked-maintenance handoff is aligned again, leaving broader `phase14_build` rerun vocabulary to the shared Phase 14 smoke packet as shared-packet evidence rather than a bridge-local trust promotion signal

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

Keep the packet in blocked maintenance and reread `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, `Documentation/zigux/phase14-workqueue-bridge-slice.md`, and `Documentation/zigux/phase14-workqueue-bridge-survey.md` together until the bridge-local blocked-maintenance handoff is aligned again. Leave broader `phase14_build` rerun vocabulary to the shared Phase 14 smoke packet as shared-packet evidence rather than a bridge-local trust promotion signal.