# Phase 14 Core Boundary Traceability

This note records the current roadmap-to-repo traceability for the Phase 14 core-adjacent concurrency anchors that remain explicitly outside active Zig delivery: `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c`.

## Why this note exists

The Phase 14 roadmap still names these anchors as study-only or freeze-in-C work.
What this shared note can honestly do on current `master` is restate that retained-in-C posture in one place and point reviewers at the remaining directly readable boundary evidence.
What it must not do anymore is pretend that the older manifest-backed shared smoke packet and anchor-local replay bundle are still present when direct current-`master` reads do not recover those files.

This note stays narrow on purpose.
It does not add a bridge, reopen a freeze decision, or claim a new status.
It only records the current bounded evidence posture and the explicit reasons these anchors still stay in C.

## Roadmap posture

- `kernel/workqueue.c`: `Study / Boundary Only` in the roadmap and freeze map. `kernel/workqueue_bridge.zig` remains review-only boundary evidence rather than a live execution or ownership claim.
- `kernel/trace/ring_buffer.c`: `Study / Boundary Only` in the roadmap and freeze map. `kernel/trace/ring_buffer.zig` remains blocked until much stronger long-horizon evidence exists.
- `net/core/skbuff.c`: `Freeze In C Initially` in the roadmap and freeze map. `net/core/skbuff_bridge.zig` is review-only boundary evidence, not a parity claim or ownership transfer.
- `kernel/rcu/tree.c`: `Freeze In C Initially` in the roadmap and freeze map. `kernel/rcu/tree_bridge.zig` remains blocked on stay-in-C evidence.

## Current direct readback

- current authenticated reads still recover this note, `Documentation/zigux/README.md`, and `Documentation/zigux/phase14-skbuff-bridge-survey.md`
- current authenticated reads do not recover these previously named Phase 14 packet files:
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  - `Documentation/zigux/phase14-ring-buffer-survey.md`
  - `Documentation/zigux/phase14-rcu-tree-survey.md`
  - `Documentation/zigux/phase14-workqueue-bridge-survey.md`
  - `zigux/tests/phase14_end_to_end_smoke_manifest.json`
  - `zigux/tests/phase14_skbuff_bridge_manifest.json`
  - `zigux/tests/phase14_ring_buffer_manifest.json`
  - `zigux/tests/phase14_rcu_tree_manifest.json`
  - `zigux/tests/phase14_build.zig`
- the surviving `Documentation/zigux/phase14-skbuff-bridge-survey.md` already says the earlier skbuff anchor packet is absent and that its older compile-route wording is archival only
- because those packet files are absent from direct current-`master` readback, this note must stay limited to roadmap posture and retained-in-C ownership; it is not a live replay contract

## Retained-in-C boundaries

### Workqueue

Live worker-pool execution, delayed-work requeue ownership, flush and drain completion ownership, timer-base and CPU-affinity handoff, hotplug transitions, rescuer behavior, scheduler-visible worker state, runtime `max_active` retuning, and forward-progress correctness still remain in C.
The honest current statement is boundary-study only, not a live bridge or replay claim.

### Ring buffer

Reserve or commit publication, the `cmpxchg()`-guarded `reader_page` handoff, `ring_buffer_alloc_read_page()` import and guarded remote-reader metadata setup, `ring_buffer_read_page()` consume or extract serialization, exported-page forced-copy decisions, wakeup or watermark publication, tracefs reader competition, mapped-reader limitations, tracefs splice or resize lockouts, and `rb_remove_pages()` mapped-reader lifetime teardown still stay with the shipped C implementation.
The honest current statement is boundary-study only, not a live survey or replay claim.

### Skbuff

Live skb lifetime, shared-info `dataref` and header-write ownership, destructor ordering, checksum-state ownership, segmentation metadata, qdisc-facing publication, and the final sock-owned tail transfer still remain in C.
The surviving skbuff survey note keeps that stay-in-C posture explicit while also marking the older skbuff packet as absent on current `master`.

### RCU tree

Grace-period sequence publication, the memory-ordering lock network, expedited funnel or stall behavior, NOCB wakeups, idle-watch and dyntick re-entry transitions, quiescent-state propagation, callback enqueue and batch invocation, public wait and callback-barrier ownership, and CPU hotplug callback migration still remain in C.
The honest current statement is freeze-in-C boundary evidence only, not a live bridge or replay claim.

## Shared packet status

- treat the older shared smoke packet and the older anchor-local manifest inventory as archival references only until current-`master` readback recovers them again
- do not use this note to claim live `make -C zigux phase14-*` or `zig build ... --build-file zigux/tests/phase14_build.zig` evidence while that build file and the named manifest bundle are absent from direct readback
- if broader reminder surfaces such as `Documentation/zigux/README.md` or `Documentation/zigux/review-checklist.md` still mention the older smoke bundle, treat that wording as historical until direct readback recovers the exact survey, manifest, and build files named above; the current truthful review packet is this note plus `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase14-skbuff-bridge-survey.md`
- any future replay claim for this Phase 14 family must first restore or re-expose the exact survey, manifest, and build files on current `master`

## What this note does not claim

- `kernel/workqueue.zig`
- `kernel/trace/ring_buffer.zig`
- `net/core/skbuff.c` parity or lifetime ownership
- any live `kernel/rcu/tree_bridge.zig` ownership claim
- any live shared smoke replay packet on current `master`
- any freeze-map status change
- any Architecture Council reopen request

## Next bounded step

Keep this cross-anchor note aligned only when direct current-`master` reads either recover the missing Phase 14 packet files or another visible Phase 14 note starts claiming them as live again.
Until then, keep follow-through note-local and truthfulness-only rather than reopening anchor-local bridge, manifest, validator, or freeze-governance work from this shared boundary note.
