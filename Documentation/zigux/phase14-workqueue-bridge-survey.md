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

The current workqueue bridge packet is intentionally review-only. The manifest already records the landed audit areas and the blocked live-execution boundary, but the packet also needs a survey note that describes the current reread posture in plain language and keeps the bridge-local handoff aligned with the current blocked-maintenance packet.

This survey is a truthfulness surface. It does not reopen the workqueue anchor, claim new runtime ownership, or turn the study packet into a parity statement.

## Current direct readback

Current direct-readback evidence for the workqueue anchor includes:

  * `kernel/workqueue_bridge.zig`
  * `zigux/tests/phase14_workqueue_bridge.zig`
  * `zigux/tests/phase14_workqueue_reviewability.zig`
  * `zigux/tests/phase14_workqueue_bridge_manifest.json`
  * `Documentation/zigux/phase14-workqueue-bridge-slice.md`
  * `Documentation/zigux/phase14-workqueue-bridge-survey.md`
  * `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  * `Documentation/zigux/phase14-core-boundary-traceability.md`
  * `Documentation/zigux/phase14-release-boundary-survey.md`
  * `Documentation/zigux/phase14-productization-gap-survey.md`
  * `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`
  * `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`
  * `Documentation/zigux/phase14-compile-shard-matrix-survey.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/freeze-map.md`
  * `Documentation/zigux/phase15-study-only-anchor-accounting.md`
  * `scripts/zigux/check-phase14-shared-smoke-route.py`
  * `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`
  * `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
  * `scripts/zigux/check-phase14-workqueue-study-only-guardrail.py`
  * `scripts/zigux/validate-phase14.py`
  * `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
  * `zigux/Makefile`

Those directly readable surfaces agree on the same bounded message:

  * `kernel/workqueue.c` remains `Study / Boundary Only`
  * the current bridge-local slice is `phase14-workqueue-scheduler-visible-worker-state-refinement`
  * `zigux/tests/phase14_workqueue_reviewability.zig` is the bridge-local reviewability check
  * the broader shared Phase 14 smoke packet should keep the workqueue boundary shard, the directly readable route checker, the directly readable tests-root reminder checker, the directly readable rollback-threshold sequencing guard, the directly readable compile-shard matrix survey, the directly readable validator surface, the directly readable release-boundary exact-count guard, and the readable current `zigux/Makefile` posture explicit without overstating bridge-local ownership
  * the bridge-local trusted rerun still stops at `zig test zigux/tests/phase14_workqueue_reviewability.zig`, while `make -C zigux phase14-validate` remains the broader shared packet-local validation route rather than bridge-local proof; that `shared_packet_local_only` productization posture belongs to the manifest and must not be read as a promotion signal for the bridge-local packet
  * the missing `phase14-smoke`, `phase14-test`, and `phase14` wrappers still do not count as current proof

## Roadmap and freeze-map alignment

The live workqueue packet currently matches the Phase 14 roadmap and freeze-map guardrails this way:

  * roadmap required feature `boundary maps`: satisfied by `kernel/workqueue_bridge.zig` keeping exactly two `boundary_map_only` bridge areas, `submission-routing` and `allocation-and-attrs`, while exposing the rest of the workqueue surface as explicit stay-in-C decisions
  * roadmap required feature `concurrency audits`: satisfied by the bridge-local manager, pending-bit, delayed-work, flush-drain, rescuer, hotplug, and scheduler-visible worker-state audit checkpoints kept in review-only form
  * roadmap required feature `explicit stay-in-C decisions where warranted`: satisfied by the bridge-local blocked-live-execution handoff and the survey's explicit stay-in-C boundaries around manager-role serialization, forward-progress accounting, callback dispatch, flush, drain, cancellation completion, delayed timer-base and CPU-affinity handoff, delayed requeue control, runtime `max_active` retuning, rescuer execution, scheduler-visible worker-state transitions, and topology rebinding
  * roadmap required feature `wrapper-first or study-only posture`: satisfied by keeping `kernel/workqueue.c` in the freeze map's `Study / Boundary Only` bucket and limiting trusted bridge-local reruns to reviewability evidence rather than live execution claims

That alignment is intentionally narrow. It shows that the packet has a real reviewable foothold for boundary mapping and audit work, while the freeze map still blocks any claim that Zigux owns the runtime workqueue engine.

## Remaining gap versus roadmap

The remaining roadmap-backed gap is also intentionally narrow:

  * the boundary-map foothold is landed, but it is intentionally limited to the two bridge areas `submission-routing` and `allocation-and-attrs`
  * every other named bridge area still stays in the stay-in-C audit packet, so the current gap is no longer “missing a boundary map” but “keeping the boundary map deliberately small while the freeze map blocks stronger ownership claims”
  * the packet is still a review-only study surface rather than a deliverable wrapper around live worker execution
  * the freeze map still blocks any ownership claim for manager-role serialization, forward-progress accounting, callback dispatch, flush or drain completion, delayed timer-base and CPU-affinity handoff, delayed requeue control, runtime `max_active` retuning, rescuer execution, scheduler-visible worker-state parity, or hotplug-driven topology rebinding
  * the shared Phase 14 route layer still stops at `make -C zigux phase14-validate`; the older `phase14-smoke`, `phase14-test`, and `phase14` wrapper names remain absent from the readable current `zigux/Makefile` body
  * the bridge-local trust surface still stops at `zig test zigux/tests/phase14_workqueue_reviewability.zig`, while broader build-side proof such as directly readable `zigux/tests/phase14_build.zig` remains shared-packet evidence rather than a bridge-local promotion signal

That is the honest boundary gap for this lane on current `master`: the reviewable study packet exists and matches the roadmap's wrapper-first posture, but the freeze map still keeps the runtime workqueue engine in C and the broader executable packet still does not justify a stronger ownership claim.

## Current workqueue packet posture

The landed workqueue packet is strong enough to keep the following review-only areas explicit:

  * boundary-map-only submission routing through `queue_work_on()` and `__queue_work()`
  * boundary-map-only allocation and attribute shaping through `__alloc_workqueue()` and `devm_alloc_workqueue()`
  * worker-pool manager-role serialization and forward-progress accounting around `manage_workers()` and `struct worker_pool`
  * ordered `max_active` throttling and last-pool reentrancy handoff inside `__queue_work()`
  * callback execution and idle-sleep handoff around `process_one_work()` and `worker_thread()`
  * pending-bit claim windows
  * delayed timer handoff back into `__queue_work()`
  * delayed requeue governance
  * flush and drain color progression
  * cancellation completion handoff through `__cancel_work_sync()`, `disable_work()`, and `__flush_work()`
  * rescuer mayday coordination
  * scheduler-visible worker-state transitions
  * hotplug topology rebinding

Those two boundary-map-only entrypoint groups are the current roadmap-backed bridge foothold. The rest of the packet stays review-only so Phase 14 can keep `kernel/workqueue.c` honest as a boundary-study target without implying live worker execution or wrapper ownership.

The newer bridge-local concurrency audit plus the explicit cancel-path handoff keep the manager, forward-progress, inactive-list, reentrancy, callback-window, idle-sleep, delayed timer-base plus CPU-affinity handoff, delayed requeue, runtime `max_active` retuning, cancellation-completion, scheduler-visible worker-state, and hotplug-topology seams explicit as stay-in-C evidence rather than as a live wrapper claim.

The packet is still blocked from claiming:

  * live worker-pool execution
  * manager-role serialization and forward-progress ownership
  * callback dispatch ownership
  * flush, drain, and cancellation completion ownership
  * delayed-work timer-base and CPU-affinity handoff ownership
  * delayed-work requeue control ownership
  * runtime `max_active` retuning ownership
  * scheduler-visible worker-state parity
  * rescuer execution ownership
  * hotplug-driven migration and topology-rebinding ownership

## Shared-packet alignment

The workqueue-local packet should stay aligned with the shared Phase 14 smoke packet on these points:

  * the workqueue anchor remains the non-frozen study-only foothold inside Phase 14
  * the shared Phase 14 smoke packet should continue naming the workqueue manifest, `zigux/tests/phase14_workqueue_reviewability.zig`, `Documentation/zigux/phase14-compile-shard-matrix-survey.md`, `scripts/zigux/check-phase14-shared-smoke-route.py`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-workqueue-study-only-guardrail.py`, `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, and the readable current `zigux/Makefile` posture
  * the bridge-local trusted rerun stays limited to the direct Zig test, while the broader `make -C zigux phase14-validate` route and its shared checker chain remain shared packet-local validation rather than bridge-local trust gates
  * any future same-lane reminder repair should keep the workqueue packet explicit without presenting missing `phase14-smoke`, `phase14-test`, and `phase14` wrappers as current proof unless a fresh reread shows they returned
  * the next same-lane step stays inside the bridge, dedicated tests, manifest, slice note, and this survey until the bridge-local blocked-maintenance handoff is aligned again; leave broader `phase14_build` rerun vocabulary to the shared Phase 14 smoke packet as shared-packet evidence rather than a bridge-local trust promotion signal

## Exact productization checks

For the current bounded step, productization behavior is only considered verified when the packet keeps these exact checks aligned with the same study-only posture:

  * direct bridge-local trust gate:
    * `zig test zigux/tests/phase14_workqueue_reviewability.zig`
  * shared packet-local productization checks:
    * `python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test`
    * `python3 scripts/zigux/check-phase14-shared-smoke-route.py`
    * `python3 scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test`
    * `python3 scripts/zigux/check-phase14-tests-readme-smoke-summary.py`
    * `python3 scripts/zigux/validate-phase14.py --self-test`
    * `python3 scripts/zigux/validate-phase14.py`
    * `python3 scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test`
    * `python3 scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
    * `python3 scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test`
    * `python3 scripts/zigux/check-phase14-release-boundary-exact-counts.py`
    * `make -C zigux phase14-validate`

Those productization-facing checks verify shared packet-local routing and reminder-surface behavior. They do not promote the workqueue bridge to owner status, and they do not replace the direct Zig replay as the bridge-local trust gate.

## Study-Only Guardrail

- manifest-backed guardrail: `phase14-workqueue-study-only-guardrail` keeps this study-only packet fail-closed until the same bridge-local packet carries narrower stay-in-C evidence instead of a lighter bridge-presence or shared-route claim.
- machine-check surface: `scripts/zigux/check-phase14-workqueue-study-only-guardrail.py` keeps the dedicated survey and manifest fail-closed on the lane key, blocked-maintenance posture, bridge-local trust gate, shared packet-local validation posture, blocked gap, and required reread evidence.
- required evidence before any trust promotion:
  - direct bridge-local trust gate: `zig test zigux/tests/phase14_workqueue_reviewability.zig`
  - bridge-local reread of `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, `Documentation/zigux/phase14-workqueue-bridge-slice.md`, and `Documentation/zigux/phase14-workqueue-bridge-survey.md`
  - explicit blocker retention for `phase14-workqueue-live-execution-blocker` together with the current `blocked_maintenance` posture
- automatic return-to-blocked triggers:
  - any wording that treats `make -C zigux phase14-validate` or shared packet-local validation as a replacement for the direct bridge-local trust gate
  - missing `phase14-workqueue-live-execution-blocker`, `blocked_maintenance`, or `shared_packet_local_only` wording in the active survey or manifest
  - any claim of live worker execution, callback dispatch ownership, flush or drain completion ownership, delayed-work requeue control, scheduler-visible worker-state parity, rescuer execution ownership, or hotplug-driven topology rebinding ownership

## Non-goals

This survey does not claim:

  * `kernel/workqueue.zig`
  * a returned make-backed focused workqueue route
  * live enqueue, drain, cancel, or rescuer ownership
  * scheduler-facing parity
  * any Phase 15 status change

## Next bounded step

Keep the workqueue anchor in blocked maintenance. If the bridge-local packet drifts again, reread the bridge, dedicated tests, manifest, this survey, and the slice note together until the bridge-local blocked-maintenance handoff is aligned again. Leave broader `phase14_build` rerun vocabulary to the shared Phase 14 smoke packet as shared-packet evidence rather than a bridge-local trust promotion signal.