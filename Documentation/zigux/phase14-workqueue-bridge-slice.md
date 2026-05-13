# Phase 14 Workqueue Bridge Slice

- `PHASE14_LANE_KEY=P14-L04`
- `PHASE14_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement`
- reviewed against live `master` `9b98d3b9c812840bf279508030be0b8de093736c`
- anchor: `kernel/workqueue.c`

## Shipped packet

- `kernel/workqueue_bridge.zig` keeps the Phase 14 workqueue study packet boundary-map only and review-first.
- `zigux/tests/phase14_workqueue_bridge.zig` keeps the bridge descriptor, boundary areas, manifest-backed gap inventory, and blocked-maintenance posture aligned.
- `zigux/tests/phase14_workqueue_reviewability.zig` keeps the shared smoke packet, the workqueue survey note, and this slice note from drifting apart.
- `zigux/tests/phase14_workqueue_bridge_manifest.json` records the current lane key, surveyed commit, landed gap ids, and the blocked live-execution boundary.
- `Documentation/zigux/phase14-workqueue-bridge-survey.md` carries the broader roadmap framing for the blocked-maintenance packet.
- `zigux/tests/phase14_build.zig`, `make -C zigux phase14-test`, and `make -C zigux phase14` keep the bounded workqueue bridge packet wired into the Phase 14 validation routes without implying a deep-core port.

## Why this packet exists

- The Phase 14 roadmap names `kernel/workqueue.c` as a boundary-study target, not a rewrite target.
- The live bridge already records eight boundary areas, fifteen review-only audit checkpoints, and seven blocked live behaviors, which is enough to keep the workqueue anchor reviewable without pretending Zigux owns runtime execution.
- The honest next move in this lane is therefore to keep the packet truthful and easy to reread, not to widen into a fake async runtime, scheduler parity, or a direct port of `kernel/workqueue.c`.

## Boundary summary

- `submission-routing` and `allocation-and-attrs` remain the reviewable footholds that explain where queueing and allocation calls cross into the live C implementation.
- Delayed-work timer expiry, timer rearm, CPU affinity, and immediate requeue fallthrough stay explicitly in C through the delayed-work governance packet.
- Flush, drain, and cancellation completion ownership stay in C because active-color progression, chained flushers, and in-flight coordination are still tied to the live worker runtime.
- Worker-pool concurrency, runtime `max_active` retuning, hotplug topology rebinding, and rescuer or scheduler-visible worker state stay review-only because they remain lock-coupled to the live kernel implementation.

## Non-goals

- no live worker-pool execution ownership
- no delayed-work requeue control
- no runtime `max_active` retuning ownership
- no scheduler callback parity
- no rescuer execution ownership
- no hotplug-driven worker migration and topology rebinding ownership
- no direct `kernel/workqueue.c` rewrite

## Next bounded step

Keep this lane in blocked maintenance and reread `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, and `Documentation/zigux/phase14-workqueue-bridge-survey.md` together before touching any broader Phase 14 shared reminder surface.