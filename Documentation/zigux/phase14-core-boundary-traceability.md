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
- `net/core/skbuff.c`: `Freeze In C Initially` in the roadmap and freeze map. `net/core/skbuff_bridge.zig` is review-only boundary evidence, not a parity claim or ownership transfer.
- `kernel/rcu/tree.c`: `Freeze In C Initially` in the roadmap and freeze map. `kernel/rcu/tree_bridge.zig` remains blocked on stay-in-C evidence.

## Current direct readback

- current direct reads in this slot still recover this note, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `scripts/zigux/validate-phase14.py`, `zigux/Makefile`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_build.zig`
- those shared packet surfaces still keep the four-checker reminder packet explicit around `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, along with `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `make -C zigux phase14-test`
- because that shared smoke packet is still directly readable on current `master`, this note should treat it as live shared evidence while keeping the anchor-local bridges, surveys, and retained-in-C decisions explicitly bounded

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

- treat the current shared smoke packet as live shared evidence for the validator-first route, the focused smoke shard, and the full replay entrypoints named above
- do not use that packet to claim direct ownership transfer, parity, or unfrozen delivery for workqueue, ring buffer, skbuff, or RCU tree
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

Keep this cross-anchor note aligned when the shared smoke packet moves.
On the next same-lane reread, compare this note with `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `scripts/zigux/validate-phase14.py`, `zigux/Makefile`, and `zigux/tests/phase14_end_to_end_smoke_manifest.json` for the next already-landed shared marker that still lacks fail-closed coverage, without reopening anchor-local bridge or freeze-governance work from this shared boundary note.
