# Phase 14 Core Boundary Traceability

This note records the current roadmap-to-repo traceability for the Phase 14 core-adjacent concurrency anchors that remain explicitly outside active Zig delivery: `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c`.
## Why this note exists

The Phase 14 roadmap already names these anchors as study-only or freeze-in-C work, and the repo already carries anchor-local manifests plus survey notes for each one. What the shared smoke packet still needs is one cross-anchor note that ties those packets back to the roadmap in one place, names the current shared evidence path, and makes the retained-in-C concurrency ownership obvious without forcing readers to hop across four separate lane notes or depend on run memory.
This note stays narrow on purpose. It does not add a bridge, reopen a freeze decision, or claim a new status. It only records the current bounded evidence bundle and the explicit reasons these anchors still stay in C.
## Roadmap posture
  * `kernel/workqueue.c`: `Study / Boundary Only` in the roadmap and freeze map. `kernel/workqueue_bridge.zig` remains review-only boundary evidence rather than a live execution or ownership claim.
  * `kernel/trace/ring_buffer.c`: `Study / Boundary Only` in the roadmap and freeze map. `kernel/trace/ring_buffer.zig` remains blocked until much stronger long-horizon evidence exists.
  * `net/core/skbuff.c`: `Freeze In C Initially` in the roadmap and freeze map. `net/core/skbuff_bridge.zig` is review-only boundary evidence, not a parity claim or ownership transfer.
  * `kernel/rcu/tree.c`: `Freeze In C Initially` in the roadmap and freeze map. `kernel/rcu/tree_bridge.zig` remains blocked on stay-in-C evidence.
## Current repo evidence
### Workqueue
  * manifest: `zigux/tests/phase14_workqueue_bridge_manifest.json`
  * survey note: `Documentation/zigux/phase14-workqueue-bridge-survey.md`
  * lane key: `P14-L04`
  * surveyed commit: `9b98d3b9c812840bf279508030be0b8de093736c`
  * ready-next gap: none currently recorded
  * blocked gap: `phase14-workqueue-live-execution-blocker`
  * retained-in-C boundary: live worker-pool execution, delayed-work requeue ownership, flush and drain completion ownership, timer-base and CPU-affinity handoff, hotplug transitions, rescuer behavior, scheduler-visible worker state, runtime `max_active` retuning, and forward-progress correctness still remain in C because the current review-only bridge packet records the manager-role, pending-bit, delayed-submission alias, timer-expiry, delayed-requeue, flush-drain, and rescuer-mayday audits for reviewability without claiming live ownership.
### Ring buffer
  * manifest: `zigux/tests/phase14_ring_buffer_manifest.json`
  * survey note: `Documentation/zigux/phase14-ring-buffer-survey.md`
  * lane key: `P14-L08`
  * surveyed commit: `99cd3249c4bab05b74227ed7ca3869284e818588`
  * ready-next gap: none currently recorded
  * blocked gap: `phase14-ring-buffer-zig-port-blocker`
  * retained-in-C boundary: reserve or commit publication, reader-page handoff and consume serialization, exported-page forced-copy decisions, remote-reader metadata and guarded reader-page import, wakeup or watermark publication, tracefs reader competition, mapped-reader limitations, tracefs splice or resize lockouts, and mapped-reader lifetime teardown still stay with the shipped C implementation because they share per-CPU page choreography, reader-visible loss accounting, wait-queue state, `reader_lock` arbitration, and `resize_disabled` ownership.
### Skbuff
  * manifest: `zigux/tests/phase14_skbuff_bridge_manifest.json`
  * survey note: `Documentation/zigux/phase14-skbuff-bridge-survey.md`
  * lane key: `P14-Y03`
  * surveyed commit: `f05e02445443e7743c3675a6f8ca4f70f6e736fb`
  * ready-next gap: none currently recorded
  * blocked gap: `phase14-skbuff-live-ownership-blocker`
  * retained-in-C boundary: live skb lifetime, shared-info `dataref` and header-write ownership, destructor ordering, checksum-state ownership, segmentation metadata, qdisc-facing publication, and the final sock-owned tail transfer still remain in C even though the repo now carries a review-only boundary map plus concurrency-sensitive checkpoint catalog around `skb_segment()`, `SKB_GSO_PARTIAL`, `SKB_GSO_CB(iter)->data_offset`, `SKB_GSO_CB(nskb)->csum`, `segs->prev`, and `validate_xmit_skb_list()`.
### RCU tree
  * manifest: `zigux/tests/phase14_rcu_tree_manifest.json`
  * survey note: `Documentation/zigux/phase14-rcu-tree-survey.md`
  * lane key: `P14-L14`
  * surveyed commit: `4c889233d157960514b241bcd5aff7cac5fda312`
  * ready-next gap: none currently recorded
  * blocked gap: `phase14-rcu-tree-bridge-blocker`
  * retained-in-C boundary: grace-period sequence publication, the memory-ordering lock network, expedited funnel or stall behavior, NOCB wakeups, idle-watch and dyntick re-entry transitions, quiescent-state propagation, callback enqueue and batch invocation, public wait and callback-barrier ownership, and CPU hotplug callback migration still remain in C because they share the live `rcu_node` hierarchy, offload state, watching-state snapshots, callback-drain coordination, CPU enrollment and teardown paths, and memory-ordering guarantees.
## Shared replay contract

The four anchor packets above are also carried together by the Phase 14 shared smoke packet:
  * manifest: `zigux/tests/phase14_end_to_end_smoke_manifest.json`
  * survey note: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  * full-bundle reviewability replay: `zigux/tests/phase14_workqueue_reviewability.zig`
  * shared packet checkers: `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
  * validator entrypoint: `make -C zigux phase14-validate`
  * focused smoke shard: `make -C zigux phase14-smoke`
  * focused smoke build replay: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
  * shared full replay: `make -C zigux phase14-test`
  * direct shared replay: `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
  * convenience target: `make -C zigux phase14`
That shared packet matters because it keeps the workqueue, ring-buffer, skbuff, and RCU anchor notes tied to the same surveyed commits, parked-or-blocked posture, stay-in-C decisions, shared smoke manifest, full-bundle workqueue reviewability replay, and validator-backed smoke plus full-replay routes instead of drifting independently or disappearing from the shared evidence path. It also acts as the current owner-map surface for bounded-internal follow-through: workqueue routes through `P14-L04`, ring buffer routes through `P14-L08`, skbuff routes through `P14-Y03`, and RCU currently routes through the manifest-backed `P14-L14` owner. Shared-lane runs should treat older packet-local owner labels as packet-local cleanup work only, not as permission to reopen a different bounded-internal lane.
## What this lane does not claim

  * `kernel/workqueue.zig`
  * `kernel/trace/ring_buffer.zig`
  * `net/core/skbuff.c` parity or lifetime ownership
  * any live `kernel/rcu/tree_bridge.zig` ownership claim
  * any freeze-map status change
  * any Architecture Council reopen request
## Next bounded step

Keep this cross-anchor traceability note aligned only when one of the four anchor packets or the shared smoke packet changes in a way that would otherwise hide a roadmap or stay-in-C boundary shift. Shared-lane follow-through should keep packet-local owner-label cleanup inside the affected anchor packet unless the cross-anchor owner map itself drifts. Anchor-local audit work should continue in the existing workqueue, ring-buffer, skbuff, and RCU lanes rather than here.
