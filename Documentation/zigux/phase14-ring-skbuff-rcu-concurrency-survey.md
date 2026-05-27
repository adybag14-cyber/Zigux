# Phase 14 Ring Skbuff RCU Concurrency Survey

This note records the bounded `P14-L12` cross-anchor concurrency audit for the Phase 14 packets around `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c`.

## Status

- `PHASE14_LANE_KEY=P14-L12`
- `PHASE14_PHASE=Phase 14`
- `PHASE14_STATUS_BUCKET=cross_anchor_stay_in_c_audit`
- `PHASE14_PROVENANCE_MODE=dated_master_readback`
- surveyed against `current-master-readback-2026-05-27`
- this note stays inside roadmap-backed concurrency audits and explicit stay-in-C decisions; it does not reopen ring-buffer, skbuff, or RCU bridge ownership

## Why this slice exists

The Phase 14 roadmap asks for boundary maps, concurrency audits, and explicit stay-in-C decisions around core-adjacent internals. Current `master` already carries anchor-local packets for:

- `P14-L08` ring-buffer study-only survey evidence
- `P14-L11` skbuff freeze-in-C boundary evidence
- `P14-L16` RCU freeze-in-C boundary evidence

The missing bounded gap is the cross-anchor statement those three packets now justify together: publication and ordering ownership, consumer lifetime and teardown ownership, and asynchronous wake or escalation ownership still remain C-owned concurrency state machines across this family.

## Anchor posture

- `kernel/trace/ring_buffer.c`: `study_only`
- `net/core/skbuff.c`: `freeze_in_c`
- `kernel/rcu/tree.c`: `freeze_in_c`
- `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` remain the governing reminders for the study-only versus freeze-in-C split

## Cross-anchor concurrency findings

### Publication and ordering ownership

- ring-buffer reserve or commit publication, `reader_page` handoff, and mapped-reader metadata publication still stay in C
- skbuff qdisc-facing publication, shared-info header-write ownership, and checksum-state ownership still stay in C
- RCU grace-period sequence publication and the memory-ordering lock network still stay in C

These are not three unrelated helper gaps. They are one cross-anchor warning that publication and ordering state still belongs to mature C-owned concurrency machinery.

### Consumer lifetime and teardown ownership

- ring-buffer read-page extraction, reader-page consume boundaries, and `rb_remove_pages()` mapped-reader lifetime teardown still stay in C
- skbuff destructor ordering, zerocopy fragment orphaning, shared-frag ownership transfer, and the final sock-owned tail transfer still stay in C
- RCU callback enqueue and batch invocation, public wait and callback-barrier ownership, and CPU hotplug callback migration still stay in C

Across all three anchors, teardown is still coupled to live ownership transitions rather than to a wrapper-safe Zig seam.

### Asynchronous wake or escalation ownership

- ring-buffer wakeup or watermark publication and tracefs reader competition still stay in C
- skbuff queue ownership and deferred destructor-side ownership escalation still stay in C
- RCU expedited funnel behavior, force-quiescent-state escalation, and NOCB wakeup handoff still stay in C

The shared product reading is still blocker accounting, not bridge readiness.

## Shared boundary result

- keep `P14-L08`, `P14-L11`, and `P14-L16` on their dedicated anchor-local packets
- keep this cross-anchor note limited to concurrency-audit truthfulness
- do not treat the current shared `phase14-validate` route, any focused build shard, or any returned anchor-local executable companion as ownership transfer evidence for these concurrency surfaces
- if a future lane changes one of these three anchor packets materially, reread this note before reusing older cross-anchor language

## Non-goals

This note does not claim:

- a `kernel/trace/ring_buffer.zig` implementation
- parity or runtime ownership for `net/core/skbuff.c`
- active `kernel/rcu/tree_bridge.zig` ownership
- any freeze-map status change
- any Architecture Council reopen request

## Next bounded step

Keep this note parked unless the ring-buffer, skbuff, or RCU anchor-local surveys change their concurrency blocker wording enough that the shared cross-anchor summary would drift.
If the lane reopens, keep the next move on the smallest truthfulness repair inside this note and its checker before widening into any anchor-local reminder or shared Phase 14 route surface.
