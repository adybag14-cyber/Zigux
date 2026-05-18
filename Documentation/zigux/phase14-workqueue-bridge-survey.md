# Phase 14 Workqueue Bridge Survey

This survey records the current direct-readback posture for the bounded `kernel/workqueue.c` study packet on `master`.

## Status

  * `PHASE14_STATUS=blocked_maintenance`
  * `PHASE14_LANE_KEY=P14-L04`
  * `PHASE14_PHASE=Phase 14`
  * `PHASE14_ANCHOR=kernel/workqueue.c`
  * `PHASE14_SURVEYED_COMMIT=9b98d3b9c812840bf279508030be0b8de093736c`
  * `PHASE14_CURRENT_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement`
  * `PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`
  * `PHASE14_SHARED_SMOKE_PACKET=shared Phase 14 smoke packet`
  * `PHASE14_BLOCKER=phase14-workqueue-live-execution-blocker`

## Why this survey exists

The current workqueue bridge packet is intentionally review-only. The manifest already records the landed audit areas and the blocked live-execution boundary, but the packet also needs a survey note that describes the current reread posture in plain language and keeps the shared Phase 14 smoke packet aligned with the bridge-local handoff.

This survey is a truthfulness surface. It does not reopen the workqueue anchor, claim new runtime ownership, or turn the study packet into a parity statement.

## Current direct readback

Current direct-readback evidence for the workqueue anchor includes:

  * `kernel/workqueue_bridge.zig`
  * `zigux/tests/phase14_workqueue_bridge.zig`
  * `zigux/tests/phase14_workqueue_reviewability.zig`
  * `zigux/tests/phase14_workqueue_bridge_manifest.json`
  * `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  * `Documentation/zigux/phase14-core-boundary-traceability.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/freeze-map.md`

Those directly readable surfaces agree on the same bounded message:

  * `kernel/workqueue.c` remains `Study / Boundary Only`
  * the current bridge-local slice is `phase14-workqueue-scheduler-visible-worker-state-refinement`
  * `zigux/tests/phase14_workqueue_reviewability.zig` is the bridge-local reviewability check
  * the broader shared Phase 14 smoke packet should keep the workqueue boundary shard explicit without overstating build-backed replay
  * the bridge-local trusted rerun stays limited to `zig test zigux/tests/phase14_workqueue_reviewability.zig`, while the broader shared Phase 14 smoke packet keeps `zig build test --build-file zigux/tests/phase14_build.zig --summary all` and the older `phase14-*` Makefile wrappers framed as shared packet-local rerun vocabulary rather than direct bridge-local trust gates

## Current workqueue packet posture

The landed workqueue packet is strong enough to keep the following review-only areas explicit:

  * boundary-map-only submission routing through `queue_work_on()` and `__queue_work()`
  * boundary-map-only allocation and attribute shaping through `__alloc_workqueue()` and `devm_alloc_workqueue()`
  * pending-bit claim windows
  * delayed timer handoff back into `__queue_work()`
  * delayed requeue governance
  * flush and drain color progression
  * rescuer mayday coordination
  * scheduler-visible worker-state transitions
  * hotplug topology rebinding

Those two boundary-map-only entrypoint groups are the current roadmap-backed bridge foothold. The rest of the packet stays review-only so Phase 14 can keep `kernel/workqueue.c` honest as a boundary-study target without implying live worker execution or wrapper ownership.

The packet is still blocked from claiming:

  * live worker-pool execution
  * callback dispatch ownership
  * delayed-work control ownership
  * runtime `max_active` retuning ownership
  * scheduler parity
  * hotplug-driven migration ownership

## Shared-packet alignment

The workqueue-local packet should stay aligned with the shared Phase 14 smoke packet on these points:

  * the workqueue anchor remains the non-frozen study-only foothold inside Phase 14
  * the shared Phase 14 smoke packet should continue naming the workqueue manifest and `zigux/tests/phase14_workqueue_reviewability.zig`
  * the bridge-local trusted rerun stays limited to the direct Zig test, while broader `phase14_build.zig` and `phase14-*` wrapper commands remain shared packet-local vocabulary until a future reread proves the build layer is directly readable again
  * any future same-lane reminder repair should keep the workqueue packet explicit without presenting a returned `phase14-*` wrapper route as current proof unless a fresh reread shows it
  * the next broader same-lane step is still packet-local reread and reminder alignment, not live execution work

## Non-goals

This survey does not claim:

  * `kernel/workqueue.zig`
  * a returned make-backed Phase 14 route
  * live enqueue, drain, cancel, or rescuer ownership
  * scheduler-facing parity
  * any Phase 15 status change

## Next bounded step

Keep the workqueue anchor in blocked maintenance. If the bridge-local packet drifts again, reread the bridge, dedicated tests, manifest, this survey, the slice note, and the shared Phase 14 smoke packet together before deciding whether the next same-lane follow-up is another truthfulness repair or a separate shared-packet restore.