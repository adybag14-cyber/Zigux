# Phase 14 RCU Tree Survey
This document records the current Phase 14 boundary-study packet for `kernel/rcu/tree.c` as it exists on verified `master`.
## Status
- `PHASE14_LANE_KEY=P14-L16`
- `PHASE14_STATUS_BUCKET=freeze_in_c`
- `PHASE14_ANCHOR=kernel/rcu/tree.c`
- `PHASE14_ROADMAP_DESTINATION=kernel/rcu/tree_bridge.zig`
- `PHASE14_BLOCKED_GAP=phase14-rcu-tree-bridge-blocker`
- survey provenance captured against verified `master` head `4c889233d157960514b241bcd5aff7cac5fda312`
- directly readable dedicated packet surfaces on current `master`:
  - `Documentation/zigux/phase14-rcu-tree-survey.md`
  - `kernel/rcu/tree_bridge.zig`
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase14-core-boundary-traceability.md`
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- executable packet companions confirmed on current `master` through public GitHub fallback:
  - `zigux/tests/phase14_rcu_tree_manifest.json`
  - `zigux/tests/phase14_rcu_tree_survey.zig`
- authenticated contents-path readback still stays partial for those executable companions, so this note keeps the freeze-in-C blocker and review-only bridge boundary map as the owner surfaces rather than claiming restored local replay or active ownership
- dedicated compile-route guard surface:
  - `scripts/zigux/check-phase14-rcu-compile-route.py`
- dedicated rollback guard surface:
  - `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`

## Why this packet exists
The Phase 14 roadmap treats `kernel/rcu/tree.c` as a freeze-in-C anchor even while it recommends `kernel/rcu/tree_bridge.zig` as a possible long-horizon destination.

This packet keeps that distinction honest: it records the current boundary evidence, the blocker that still keeps Tree RCU in C, the exact dedicated note and review-only bridge boundary map that remain directly readable on `master`, and the executable companions that public GitHub fallback confirms are still live even while authenticated contents-path reads stay partial. This note stays narrow on purpose. It does not reopen the freeze decision, it does not claim active `kernel/rcu/tree_bridge.zig` ownership, and it does not widen into the shared Phase 14 smoke lane beyond the RCU packet it already depends on.

## Exact evidence captured
- freeze-map posture:
  - `Documentation/zigux/freeze-map.md` keeps `kernel/rcu/tree.c` in `Freeze In C Initially`
- directly readable dedicated packet surfaces on current `master`:
  - `Documentation/zigux/phase14-rcu-tree-survey.md`
  - `kernel/rcu/tree_bridge.zig`
  - `Documentation/zigux/phase14-core-boundary-traceability.md`
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  - `Documentation/zigux/freeze-map.md`
- executable packet companions confirmed on current `master` through public GitHub fallback:
  - `zigux/tests/phase14_rcu_tree_manifest.json`
  - `zigux/tests/phase14_rcu_tree_survey.zig`
- authenticated contents-path readback still stays partial for those executable companions, so the dedicated note continues to treat the freeze-in-C blocker, the review-only bridge boundary map, and the shared owner-map packet as the live owner surfaces for this lane
- shared Phase 14 reminder surfaces that still carry the bounded owner-map tie-back:
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  - `Documentation/zigux/phase14-core-boundary-traceability.md`
- packet-local rerun vocabulary that public fallback now corroborates, even though this lane still lacks a local exact-replay environment on current `master`:
  - `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
  - `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
- dedicated compile-route guard surface:
  - `python3 scripts/zigux/check-phase14-rcu-compile-route.py`
- dedicated rollback guard surface:
  - `python3 scripts/zigux/check-phase14-rcu-rollback-guardrail.py`

## Boundary findings
- grace-period sequence publication still stays in C because `rcu_start_this_gp`, `rcu_gp_init`, and `__note_gp_changes` remain coupled to the live `rcu_node` hierarchy and GP sequencing state
- the memory-ordering lock network still stays in C because `raw_spin_lock_rcu_node`, `smp_mb__after_unlock_lock`, and `smp_store_release` remain a live ordering contract rather than a detachable bridge seam
- expedited funnel and stall behavior still stays in C because CPU selection, forcing, and sequence completion remain coupled through `sync_rcu_exp_select_cpus`, `synchronize_rcu_expedited_wait_once`, and `rcu_exp_gp_seq_end`
- NOCB wakeup handoff still stays in C because bypass pressure, deferred wakeups, and offload handoff remain coupled through `rcu_nocb_bypass_lock`, `wake_nocb_gp_defer`, and `do_nocb_deferred_wakeup`
- idle-watch and dyntick re-entry transitions still stay in C because `rcu_is_watching`, `rcu_watching_snap_save`, and `invoke_rcu_core` still rely on live per-CPU watching-state snapshots and wakeup choices
- quiescent-state propagation and callback acceleration still stay in C because `rcu_report_qs_rnp`, `note_gp_changes`, and `rcu_accelerate_cbs` still climb the live hierarchy under lock and fold sequence changes into callback state
- callback enqueue and batch invocation still stays in C because `__call_rcu_common`, `call_rcu_core`, and `rcu_do_batch` remain tied to segmented callback lists, overload tracking, and bounded drain behavior
- force-quiescent-state escalation still stays in C because `rcu_force_quiescent_state`, `rcu_gp_kthread_wake`, and `rcu_gp_fqs_loop` still couple root-node escalation, grace-period wake coordination, and the FQS loop through live `rcu_state` and `rcu_node` ownership
- poll-cookie sequencing, synchronize_rcu wait-head rollover, and completion cleanup handoff still stay in C because `rcu_poll_gp_seq_start_unlocked`, `rcu_poll_gp_seq_end_unlocked`, `rcu_sr_normal_gp_init`, and `rcu_sr_normal_gp_cleanup_work` still share `gp_seq_polled` visibility, grace-period completion state, wait-head rollover, and later cleanup handoff inside the live Tree RCU state machine
- public wait and callback-barrier ownership still stays in C because `synchronize_rcu`, `get_state_synchronize_rcu`, `poll_state_synchronize_rcu`, and `rcu_barrier` still couple public waiting, polling-cookie APIs, and callback-drain guarantees to deep-core Tree RCU sequencing
- CPU hotplug callback migration still stays in C because `rcutree_prepare_cpu`, `rcutree_offline_cpu`, and `rcutree_migrate_callbacks` remain tied to live CPU enrollment, teardown, and callback migration state

## Bridge blocker
`kernel/rcu/tree_bridge.zig` remains blocked by `phase14-rcu-tree-bridge-blocker`.
The current survey evidence still shows force-quiescent-state escalation, poll-cookie sequencing plus synchronize_rcu wait-head rollover and completion cleanup handoff, public wait and callback-barrier ownership, CPU hotplug callback migration, expedited waits, grace-period publication, NOCB offload, idle-watch re-entry, quiescent-state propagation, callback enqueue, and the memory-ordering lock network as one live deep-core ownership surface. That is still a freeze-in-C posture, not a review-ready bridge seam.

## Compile-route guard
- machine-check surface: `scripts/zigux/check-phase14-rcu-compile-route.py` keeps the dedicated RCU compile row fail-closed on the shared-manifest entry, the focused `phase14_build` wiring, and this note's replay vocabulary.
- route posture: the checker treats `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all` and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` as packet-local review routes corroborated by public fallback, not as active ownership or parity claims.
- freeze posture: the compile-route guard adds drift detection for the RCU matrix row without weakening the existing freeze-in-C blocker or the rollback threshold.

## Rollback guardrail
- manifest-backed guardrail: `phase14-rcu-tree-rollback-threshold-guardrail` keeps this freeze-in-C packet fail-closed until the same review packet carries the required reopen evidence instead of a lighter status-review claim.
- machine-check surface: `scripts/zigux/check-phase14-rcu-rollback-guardrail.py` keeps the dedicated note fail-closed on its lane key, blocked gap, companion-readback wording, rollback owner, and required reopen evidence.
- rollback owner: `Repo Tooling Pod`
- required evidence before any status review:
  - `Architecture Council` reopen record linked from the active review packet
  - parity scorecard evidence and benchmark notes attached to the same review packet
  - validation replay command and evidence archive path recorded beside the latest blocker disposition
- automatic return-to-blocked triggers:
  - any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the `Architecture Council` reopen record
  - missing parity scorecard evidence, benchmark notes, or replay command in the active review packet
  - freeze-map, survey note, or dedicated-check drift that drops the blocked bridge disposition, the companion-readback warning, or the rollback owner

## Non-goals
- any live `kernel/rcu/tree_bridge.zig` ownership claim
- any freeze-map status change
- any Architecture Council reopen request
- any claim that Tree RCU is now a study-only anchor instead of a freeze-in-C anchor

## Next bounded step
Keep this dedicated RCU packet aligned only when the dedicated note, the executable-companion readback, the compile-route guard, the freeze map, or the shared Phase 14 owner-map packet changes in a way that would otherwise hide the current freeze-in-C blocker.
If authenticated contents-path readback recovers for the executable companions too, update this note and the dedicated checker together before restoring any stronger exact-readback wording.
