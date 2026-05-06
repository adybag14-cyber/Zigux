# Phase 14 Core Boundary Traceability

This note records the current roadmap-to-repo traceability for the Phase 14 core-adjacent concurrency anchors that remain explicitly outside active Zig delivery: `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c`.

## Why this note exists

The Phase 14 roadmap already names these anchors as study-only or freeze-in-C work, and the repo already carries anchor-local manifests plus survey notes for each one. What the shared smoke packet still needs is one cross-anchor note that ties those packets back to the roadmap in one place, names the current shared evidence path, and makes the retained-in-C concurrency ownership obvious without forcing readers to hop across four separate lane notes or depend on run memory.

This note stays narrow on purpose. It does not add a bridge, reopen a freeze decision, or claim a new status. It only records the current bounded evidence bundle and the explicit reasons these anchors still stay in C.

## Roadmap posture

- `kernel/workqueue.c`: `Study / Boundary Only` in the roadmap and freeze map. `kernel/workqueue_bridge.zig` remains review-only boundary evidence rather than a live execution or ownership claim.
- `kernel/trace/ring_buffer.c`: `Study / Boundary Only` in the roadmap and freeze map. `kernel/trace/ring_buffer.zig` remains blocked until much stronger long-horizon evidence exists.
- `net/core/skbuff.c`: `Freeze In C Initially` in the roadmap and freeze map. `net/core/skbuff_bridge.zig` is review-only boundary evidence, not a parity claim or ownership transfer.
- `kernel/rcu/tree.c`: `Freeze In C Initially` in the roadmap and freeze map. `kernel/rcu/tree_bridge.zig` remains blocked on stay-in-C evidence.

## Current repo evidence

### Workqueue

- manifest: `zigux/tests/phase14_workqueue_bridge_manifest.json`
- survey note: `Documentation/zigux/phase14-workqueue-bridge-survey.md`
- lane key: `P14-L04`
- surveyed commit: `9e278f632d6d5097cb8cfc2dc61744ae105baa8c`
- ready-next gap: none currently recorded
- blocked gap: `phase14-workqueue-live-execution-blocker`
- retained-in-C boundary: live worker-pool execution, draining, delayed-work requeue ownership, timer-base and CPU-affinity handoff, hotplug transitions, rescuer behavior, scheduler callbacks, and forward-progress correctness still remain in C because they share `worker_pool` state, pending-bit handoff, delayed timer expiry, and scheduler-visible ownership that the current boundary map only records for reviewability.

### Ring buffer

- manifest: `zigux/tests/phase14_ring_buffer_manifest.json`
- survey note: `Documentation/zigux/phase14-ring-buffer-survey.md`
- lane key: `P14-L08`
- surveyed commit: `946d5c73fdb763ba860a20879b05da54e1896e8c`
- ready-next gap: `phase14-ring-buffer-read-page-copy-followup`
- blocked gap: `phase14-ring-buffer-zig-port-blocker`
- retained-in-C boundary: reserve or commit publication, reader-page handoff, remote-reader metadata, wakeup or watermark publication, mapped-reader limitations, and tracefs splice or resize lockouts still stay with the shipped C implementation because they share per-CPU page choreography, reader-visible loss accounting, wait-queue state, and `resize_disabled` ownership.

### Skbuff

- manifest: `zigux/tests/phase14_skbuff_bridge_manifest.json`
- survey note: `Documentation/zigux/phase14-skbuff-bridge-survey.md`
- lane key: `P14-L11`
- surveyed commit: `f05e02445443e7743c3675a6f8ca4f70f6e736fb`
- ready-next gap: none currently recorded
- blocked gap: `phase14-skbuff-live-ownership-blocker`
- retained-in-C boundary: live skb lifetime, destructor ordering, qdisc-owned publication, checksum-state ownership, segmentation behavior, and final drop pruning still remain in C even though the repo now carries a review-only boundary map through `validate_xmit_skb_list()` republish plus the observational `__dev_direct_xmit()` identity-drop checkpoint, both of which keep qdisc publication, queue ownership, and skb lifetime ownership explicitly outside Zigux.

### RCU tree

- manifest: `zigux/tests/phase14_rcu_tree_manifest.json`
- survey note: `Documentation/zigux/phase14-rcu-tree-survey.md`
- lane key: `P14-L16`
- surveyed commit: `4c889233d157960514b241bcd5aff7cac5fda312`
- ready-next gap: none currently recorded
- blocked gap: `phase14-rcu-tree-bridge-blocker`
- retained-in-C boundary: grace-period sequence publication, the memory-ordering lock network, expedited funnel or stall behavior, NOCB wakeups, quiescent-state propagation, callback enqueue, and callback batch invocation still remain in C because they share the live `rcu_node` hierarchy, offload state, CPU-hotplug handoff, and memory-ordering guarantees.

## Shared replay contract

The four anchor packets above are also carried together by the Phase 14 shared smoke packet:

- manifest: `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- survey note: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- validator entrypoint: `make -C zigux phase14-validate`
- shared replay: `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
- convenience target: `make -C zigux phase14`

That shared packet matters because it proves the workqueue, ring-buffer, skbuff, and RCU anchor notes still agree on their exact surveyed commits, lane keys, ready-next versus blocked posture, and stay-in-C decisions instead of drifting independently or disappearing from the shared evidence path.

## What this lane does not claim

- `kernel/workqueue.zig`
- `kernel/trace/ring_buffer.zig`
- `net/core/skbuff.c` parity or lifetime ownership
- `kernel/rcu/tree_bridge.zig`
- any freeze-map status change
- any Architecture Council reopen request

## Next bounded step

Keep this cross-anchor traceability note aligned only when one of the four anchor packets or the shared smoke packet changes in a way that would otherwise hide a roadmap or stay-in-C boundary shift. Anchor-local audit work should continue in the existing workqueue, ring-buffer, skbuff, and RCU lanes rather than here.
