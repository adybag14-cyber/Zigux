# Phase 14 Core Boundary Traceability

This note records the current roadmap-to-repo traceability for the Phase 14 core-adjacent concurrency anchors that remain explicitly outside active Zig delivery: `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c`.

## Why this note exists

The Phase 14 roadmap still names these anchors as study-only or freeze-in-C work.
What this shared note can honestly do on current `master` is restate that retained-in-C posture in one place and point reviewers at the remaining directly readable boundary evidence plus the still-live shared smoke packet that ties those reminders together.
What it must not do is turn that shared packet into a parity claim, an ownership transfer, or a reason to reopen the freeze posture for any of the four anchors.

This note stays narrow on purpose.
It does not add a bridge, reopen a freeze decision, or claim a new status.
It only records the current bounded evidence posture and the explicit reasons these anchors still stay in C.

## Roadmap posture

- `kernel/workqueue.c`: `Study / Boundary Only` in the roadmap and freeze map. `kernel/workqueue_bridge.zig` remains review-only boundary evidence rather than a live execution or ownership claim.
- `kernel/trace/ring_buffer.c`: `Study / Boundary Only` in the roadmap and freeze map. `kernel/trace/ring_buffer.zig` remains blocked until much stronger long-horizon evidence exists.
- `net/core/skbuff.c`: `Freeze In C Initially` in the roadmap and freeze map. `Documentation/zigux/phase14-skbuff-bridge-survey.md` is the surviving skbuff truthfulness marker on current `master`; `net/core/skbuff_bridge.zig` is not currently shipped, so there is no live skbuff-local bridge or compile route to treat as evidence.
- `kernel/rcu/tree.c`: `Freeze In C Initially` in the roadmap and freeze map. `kernel/rcu/tree_bridge.zig` remains blocked on stay-in-C evidence.

## Current direct readback

- current direct reads in this slot now recover this note, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-productization-gap-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md`
- those readable documentation surfaces now keep the narrower repo-reality split explicit: the shared smoke note, the cross-anchor traceability note, the release-and-gap notes, and the freeze-map plus study-only-accounting companions are readable again; the workqueue boundary shard is also directly readable again through `Documentation/zigux/phase14-workqueue-bridge-survey.md` and `zigux/tests/phase14_workqueue_bridge_manifest.json`, while the validator, build, shared manifest, and remaining anchor-local survey or bridge packet members still need separate successful readback before they can be reused here as direct current-`master` evidence
- because that shared documentation packet is directly readable on current `master`, this note should treat that documentation layer as live shared evidence while keeping the anchor-local executable packet and retained-in-C decisions explicitly bounded

## Retained-in-C boundaries

### Workqueue

Live worker-pool execution, delayed-work requeue ownership, flush and drain completion ownership, timer-base and CPU-affinity handoff, hotplug transitions, rescuer behavior, scheduler-visible worker state, runtime `max_active` retuning, and forward-progress correctness still remain in C.
The honest current statement is boundary-study only, not a live bridge or replay claim.

### Ring buffer

Reserve or commit publication, the `cmpxchg()`-guarded `reader_page` handoff, `ring_buffer_alloc_read_page()` import and guarded remote-reader metadata setup, `ring_buffer_read_page()` consume or extract serialization, exported-page forced-copy decisions, wakeup or watermark publication, tracefs reader competition, mapped-reader limitations, tracefs splice or resize lockouts, and `rb_remove_pages()` mapped-reader lifetime teardown still stay with the shipped C implementation.
The honest current statement is still boundary-study only: the recovered documentation packet now carries the cross-anchor traceability note, the shared smoke note, the current productization-gap split, and the Phase 15 study-only accounting companion, while the dedicated `P14-L08` survey, manifest, and focused replay remain outside the directly recovered executable layer in this lane.

### Skbuff

Live skb lifetime, shared-info `dataref` and header-write ownership, destructor ordering, checksum-state ownership, segmentation metadata, qdisc-facing publication, and the final sock-owned tail transfer still remain in C.
The surviving skbuff survey note keeps that stay-in-C posture explicit while also marking the older skbuff packet as absent on current `master`, so this shared note must not imply a live `net/core/skbuff_bridge.zig` helper or any skbuff-local compile route.

### RCU tree

Grace-period sequence publication, the memory-ordering lock network, expedited funnel or stall behavior, NOCB wakeups, idle-watch and dyntick re-entry transitions, quiescent-state propagation, callback enqueue and batch invocation, public wait and callback-barrier ownership, and CPU hotplug callback migration still remain in C.
The honest current statement is freeze-in-C boundary evidence only, not a live bridge or replay claim.

## Shared packet status

- treat the current shared smoke packet as live shared evidence for the recovered documentation layer, the mixed-source validator readback, and the packet-local rerun vocabulary preserved in the shared smoke note
- do not use that packet to claim current wrapper-backed replay, executable-layer recovery, direct ownership transfer, parity, or unfrozen delivery for workqueue, ring buffer, skbuff, or RCU tree
- the shared packet wording is now aligned on this point: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, and `Documentation/zigux/phase14-shared-smoke-current-master-gap.md` keep the older `phase14-*` commands framed as packet-local rerun vocabulary while the readable `zigux/Makefile` body stays on the returned Phase 2, Phase 3, and Phase 10 routes and the build, manifest, checker, and bridge companions remain separate readback gaps
- if a future direct readback loses any of the shared survey, manifest, validator, Makefile, or build-file anchors again, narrow this note back to a truthfulness-only retained-in-C summary and update the shared packet wording immediately
- any future expansion beyond this shared reminder packet still needs explicit re-read evidence for the anchor-local files it names, plus the existing freeze-map discipline

## What this note does not claim

- `kernel/workqueue.zig`
- `kernel/trace/ring_buffer.zig`
- `net/core/skbuff.c` parity or lifetime ownership
- any live `kernel/rcu/tree_bridge.zig` ownership claim
- any anchor-local parity or execution claim beyond the shared smoke packet
- any freeze-map status change
- any Architecture Council reopen request

## Next bounded step

Keep this cross-anchor traceability note aligned with the recovered Phase 14 documentation packet and the directly readable workqueue boundary shard.
On the next same-lane reread, compare this note with `Documentation/zigux/phase14-productization-gap-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase14-workqueue-bridge-survey.md`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` to confirm that it still treats workqueue and ring buffer as study-only anchors, skbuff and RCU tree as freeze-in-C anchors, the workqueue reviewability shard as the one directly readable anchor-local foothold, and the broader executable survey or bridge companions as separate readback gaps.
