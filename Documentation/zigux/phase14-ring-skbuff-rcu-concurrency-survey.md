# Phase 14 Ring Buffer, Skbuff, and RCU Concurrency Survey

This note records the bounded `P14-L12` cross-anchor study packet for the three Phase 14 concurrency-heavy anchors that still stay outside active Zig ownership: `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c`.

## Status
- `PHASE14_LANE_KEY=P14-L12`
- `PHASE14_STATUS_BUCKET=study_only_cross_anchor`
- `PHASE14_SCOPE=ring-buffer-skbuff-rcu-concurrency`
- `PHASE14_BLOCKED_GAP=phase14-cross-anchor-concurrency-bridge-blocker`
- roadmap-aligned owner surfaces for this packet:
  - `Documentation/zigux/phase14-ring-buffer-survey.md`
  - `Documentation/zigux/phase14-skbuff-bridge-survey.md`
  - `Documentation/zigux/phase14-rcu-tree-survey.md`
  - `Documentation/zigux/phase14-core-boundary-traceability.md`
  - `Documentation/zigux/freeze-map.md`
- retained posture from the roadmap and freeze map:
  - `kernel/trace/ring_buffer.c`: `Study / Boundary Only`
  - `net/core/skbuff.c`: `Freeze In C Initially`
  - `kernel/rcu/tree.c`: `Freeze In C Initially`

## Why this packet exists
The roadmap does not just ask for isolated boundary notes. It explicitly asks for concurrency audits and explicit stay-in-C decisions where warranted.

Current `master` already has dedicated anchor-local packets for ring buffer, skbuff, and RCU tree.
What it did not yet have was one bounded note that names the shared concurrency pattern across those three anchors and explains why that pattern still blocks a wider bridge story.

This packet stays narrow on purpose.
It does not reopen any anchor-local blocker.
It does not claim parity.
It does not claim ownership transfer.
It records one cross-anchor finding: the same three classes of concurrency contract keep reappearing across the ring-buffer, skbuff, and RCU packets, and those contracts still belong to the shipped C implementations.

## Cross-anchor finding
The three anchor-local packets now support one shared conclusion:

1. Publication and ordering ownership still stays in C.
- ring buffer: reserve or commit publication, head-page rotation, and reader-visible metadata publication still stay coupled inside `ring_buffer_lock_reserve()`, `ring_buffer_unlock_commit()`, `rb_move_tail()`, `rb_update_meta_page()`, and the related reader-page choreography.
- skbuff: qdisc-facing publication, checksum ownership, segmentation metadata, and the final sock-owned tail transfer still stay coupled inside the live `validate_xmit_skb_list()` path and its destructor-linked ownership updates.
- RCU tree: grace-period sequence publication, the memory-ordering lock network, and public wait-visible sequence state still stay coupled inside `rcu_start_this_gp`, `rcu_gp_init`, `__note_gp_changes`, `raw_spin_lock_rcu_node`, `smp_mb__after_unlock_lock`, and `smp_store_release`.

2. Consumer lifetime and teardown ownership still stays in C.
- ring buffer: reader-page handoff, read-page extraction, tracefs read-versus-splice lifetime, and mapped-reader teardown still stay coupled inside `rb_get_reader_page()`, `ring_buffer_read_page()`, `tracing_buffers_read()`, `tracing_buffers_splice_read()`, and `rb_remove_pages()`.
- skbuff: skb lifetime, shared-info `dataref`, destructor ordering, `sock_wfree`, `tail->destructor`, `tail->sk`, `tail->next`, `segs->prev`, and the consumer-side `tail = skb->prev` reset still stay coupled inside the existing C-owned teardown and transmission path.
- RCU tree: callback enqueue, callback drain, callback-barrier ownership, synchronize_rcu wait-head rollover, completion cleanup, and CPU hotplug callback migration still stay coupled inside `__call_rcu_common`, `rcu_do_batch`, `rcu_barrier`, `rcu_sr_normal_gp_init`, `rcu_sr_normal_gp_cleanup_work`, `rcutree_prepare_cpu`, `rcutree_offline_cpu`, and `rcutree_migrate_callbacks`.

3. Asynchronous wake, offload, and escalation ownership still stays in C.
- ring buffer: wakeup or watermark publication, mapped-reader ioctl wakeups, remote-reader metadata import, and resize or snapshot lockouts still stay coupled inside `ring_buffer_wait()`, `ring_buffer_poll_wait()`, `rb_wake_up_waiters()`, `ring_buffer_map_get_reader()`, `rb_read_remote_meta_page()`, and `ring_buffer_resize()`.
- skbuff: queue publication, segmentation-side follow-on ownership, and destructor-backed handoff still stay coupled inside the same transmission and queue-drain path instead of exposing a bridge-safe async seam.
- RCU tree: expedited waits, force-quiescent-state escalation, NOCB deferred wakeups, idle-watch transitions, and hotplug-facing callback handoff still stay coupled inside `sync_rcu_exp_select_cpus`, `synchronize_rcu_expedited_wait_once`, `rcu_force_quiescent_state`, `rcu_gp_fqs_loop`, `wake_nocb_gp_defer`, `do_nocb_deferred_wakeup`, `rcu_is_watching`, and `invoke_rcu_core`.

## Explicit stay-in-C decision
- do not treat `kernel/trace/ring_buffer.zig` as an active bridge target; the ring-buffer packet still supports study-only evidence, not live ownership.
- do not treat the returned skbuff bridge packet as a parity or runtime-ownership signal; the packet remains review-only boundary evidence while `phase14-skbuff-live-ownership-blocker` stays open.
- do not treat `kernel/rcu/tree_bridge.zig` as a live bridge claim; the dedicated RCU packet remains freeze-in-C evidence while `phase14-rcu-tree-bridge-blocker` stays open.
- do not collapse these three anchors into one generic wrapper story; their shared blocker is precisely that publication, lifetime, and escalation semantics are still concurrency-owned C state machines rather than detachable helper seams.

## Reopen threshold
- `phase14-cross-anchor-concurrency-bridge-blocker` remains open until a future packet can show narrower evidence than the current anchor-local surveys.
- minimum reopen evidence for any wider cross-anchor status review:
  - `Architecture Council` reopen record linked from the active packet that proposes the wider review
  - parity scorecard and benchmark evidence attached to the exact anchor-local packet being reconsidered
  - replay command and evidence archive path recorded beside the latest blocker disposition
- automatic return-to-blocked triggers:
  - any wording that upgrades this packet into parity, bridge ownership, or a freeze-map status change
  - any cross-anchor summary that drops the explicit study-only or freeze-in-C distinction between ring buffer, skbuff, and RCU tree
  - any same-family reminder note that repeats a shared bridge claim without updated anchor-local evidence

## Non-goals
- a new shared build route
- a shared wrapper surface for the three anchors
- any claim that the ring-buffer, skbuff, or RCU executable companions now imply shared replay parity
- any freeze-map status change

## Next bounded step
Keep this packet parked unless one of the three anchor-local surveys, the shared core traceability note, or the freeze map drifts in a way that hides the shared concurrency blocker described here.
If the packet reopens, prefer the smallest truthfulness repair inside this note first, then update the owning anchor-local survey only if that survey is the surface that actually drifted.
