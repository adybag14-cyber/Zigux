# Phase 14 RCU Tree Survey

This document records the bounded Phase 14 survey lane `P14-L16` around `kernel/rcu/tree.c`.

## Status
- `PHASE14_STATUS=freeze_in_c`
- `PHASE14_SLICE=rcu-tree-survey-gap`
- `PHASE14_LANE_KEY=P14-L16`
- `PHASE14_SURVEYED_COMMIT=4c889233d157960514b241bcd5aff7cac5fda312`
- scope: the dedicated Phase 14 RCU tree survey gate, its manifest, the shared Phase 14 build wiring, the shared review checklist entry for this boundary packet, and this lane note that compares the roadmap destination against the current freeze boundary without shipping a bridge
- survey provenance refreshed against verified `master` head `4c889233d157960514b241bcd5aff7cac5fda312`
- product boundary:
  - `zigux/tests/phase14_rcu_tree_survey.zig`
  - `zigux/tests/phase14_rcu_tree_manifest.json`
  - `zigux/tests/phase14_build.zig`
  - `Documentation/zigux/phase14-rcu-tree-survey.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 14 roadmap names `kernel/rcu/tree_bridge.zig` as the long-term destination for a bounded RCU tree study, but the current freeze map also lists `kernel/rcu/tree.c` in the deep-core keep-it-in-C set.
That tension matters because the live anchor is already 4,931 lines and it does not stand alone. `kernel/rcu/tree_plugin.h` adds another 1,369 lines of plugin and flavor glue, `kernel/rcu/tree_exp.h` adds 1,118 lines of expedited-GP coordination, `kernel/rcu/tree_nocb.h` adds 1,702 lines of callback-offload logic, and even nearby `kernel/rcu/update.c` still depends on the existing state machine.
The upstream design references also stay large and specific: `Documentation/RCU/Design/Requirements/Requirements.rst` is 2,873 lines and `Documentation/RCU/Design/Memory-Ordering/Tree-RCU-Memory-Ordering.rst` adds another 648 lines of ordering detail.
The honest move for this lane is therefore not to start `kernel/rcu/tree_bridge.zig`.
It is to make the blocked state reviewable and record the stay-in-C checklist seams, rollback threshold, and blocker packet so future runs can compare the roadmap target against the current freeze boundary without overstating progress or sneaking in a placeholder wrapper.

## Roadmap boundary map
- `zigux/tests/`: `reviewable_survey_landed` via `zigux/tests/phase14_rcu_tree_survey.zig`, which keeps the RCU tree blocker, rollback threshold, and survey package machine-checkable beside the rest of the Phase 14 gates.
- `Documentation/zigux/`: `reviewable_survey_landed` via `Documentation/zigux/phase14-rcu-tree-survey.md`, which records the roadmap-vs-freeze comparison, the current checklist seams, the rollback threshold, and the current freeze-in-C blocker in one reviewable note.
- `kernel/rcu/tree_bridge.zig`: `blocked_on_stay_in_c_evidence` because `kernel/rcu/tree.c` is still a freeze-in-C anchor and the current survey evidence still ties grace-period publication, expedited waits, public wait-and-barrier APIs, NOCB offload, idle-or-dyntick watching transitions, CPU hotplug migration, and memory-ordering behavior tightly enough that a Phase 14 bridge claim or a placeholder wrapper would overstate progress.

## Survey findings
- `kernel/rcu/tree.c` is present on `master` at 4,931 lines and remains part of the explicit freeze-in-C set.
- `kernel/rcu/tree_plugin.h`, `kernel/rcu/tree_exp.h`, and `kernel/rcu/tree_nocb.h` show that normal GP sequencing, expedited waits, and callback offload are split across tightly coupled files rather than living behind a small helper seam.
- `kernel/rcu/update.c` remains a nearby consumer of the same RCU state machine, which makes a one-file bridge story misleading.
- `Documentation/RCU/Design/Requirements/Requirements.rst` and `Documentation/RCU/Design/Memory-Ordering/Tree-RCU-Memory-Ordering.rst` reinforce that Tree RCU correctness depends on ordering and quiescent-state guarantees, not only on symbol cataloging.
- the live repo already had `zigux/tests/phase14_build.zig`, `zigux/Makefile` Phase 14 wiring, `Documentation/zigux/freeze-map.md`, the workqueue bridge lane, the ring-buffer survey lane, and the skbuff bridge lane, so the highest-value non-overlapping RCU step remains a survey package that records why the roadmap destination stays blocked.
- the current manifest now records a landed freeze-boundary checklist around grace-period sequence publication, the memory-ordering lock network, expedited-GP funnel or stall behavior, NOCB bypass or wakeup handoffs, idle-watch re-entry and core invocation, quiescent-state propagation plus callback acceleration, callback enqueue plus batch invocation, callback offload, public wait and barrier APIs, CPU hotplug and callback migration, and the rollback threshold that governs any future reopen attempt.

## Decision checklist
- landed `phase14-rcu-tree-boundary-decision-checklist`
- `grace-period-sequence-publication`: keep `rcu_start_this_gp()`, `rcu_gp_init()`, and `__note_gp_changes()` in C because `gp_seq`, `qsmask`, and `rcu_node` propagation remain coupled to the live hierarchy and ordering rules.
- `memory-ordering-lock-network`: keep `raw_spin_lock_rcu_node()`, `smp_mb__after_unlock_lock()`, and `smp_store_release()` in C because Tree RCU's grace-period ordering guarantee still depends on the documented `rcu_node` lock network, GP publication stores, polling-order semantics, and CPU-hotplug publication rules rather than a detachable wrapper contract.
- `expedited-funnel-and-stall-path`: keep `sync_rcu_exp_select_cpus()`, `synchronize_rcu_expedited_wait_once()`, and `rcu_exp_gp_seq_end()` in C because CPU selection, IPI forcing, timeout handling, and sequence serialization still move together.
- `nocb-offload-wakeup-handoff`: keep `rcu_nocb_bypass_lock()`, `wake_nocb_gp_defer()`, and `do_nocb_deferred_wakeup()` in C because bypass pressure, kthread wakeups, and deferred GP signaling are still part of the same offload state machine.
- `idle-watch-reentry-and-core-invocation`: keep `rcu_is_watching()`, `rcu_watching_snap_save()`, and `invoke_rcu_core()` in C because extended-quiescent-state detection still depends on per-CPU watching state, remote dyntick snapshot ordering, and the same live choice between softirq and rcuc-kthread wakeups.
- `quiescent-state-propagation-and-callback-acceleration`: keep `rcu_report_qs_rnp()`, `note_gp_changes()`, and `rcu_accelerate_cbs()` in C because quiescent-state reporting still walks the locked `rcu_node` tree, `note_gp_changes()` still folds GP transitions into per-CPU callback state, and callback acceleration still depends on segmented callback lists plus offload state.
- `callback-enqueue-and-batch-invocation`: keep `__call_rcu_common()`, `call_rcu_core()`, and `rcu_do_batch()` in C because callback enqueue still routes through per-CPU segmented callback lists, overload tracking, NOCB offload selection, grace-period forcing, and time-bounded callback invocation.

## Memory-ordering network follow-up

This run closes one narrower ordering-boundary gap without changing the blocked bridge posture.
- `Documentation/RCU/Design/Memory-Ordering/Tree-RCU-Memory-Ordering.rst` does not describe a detachable helper seam. It documents the `rcu_node` lock-ordering network itself, including the way `raw_spin_lock_rcu_node()` acquisition relies on `smp_mb__after_unlock_lock()` so ordering can propagate across the live hierarchy instead of through a small wrapper boundary.
- `rcu_gp_init()` and the hotplug-side `rcutree_report_cpu_starting()` path still publish shared state with `smp_store_release()`, which means grace-period startup, CPU enrollment, and the visibility rules for later polling or callback paths still travel through the same core ordering contract.
- `kernel/rcu/update.c` keeps that same contract user-visible through `synchronize_rcu()`, `start_poll_synchronize_rcu()`, and `poll_state_synchronize_rcu_full()`, and the memory-ordering document explicitly calls out those polling primitives as consumers of the same grace-period ordering guarantee.
The net result is still survey-only: the lock-ordering network, GP publication stores, and polling-order semantics remain explicitly in C, not as a new opening for `kernel/rcu/tree_bridge.zig`.

## Callback offload and wakeup follow-up

This run treats the callback-offload audit as landed stay-in-C evidence rather than a bridge opening.
- `call_rcu_nocb()` is not just a detached enqueue shim. It first tries the bypass path, falls back to `rcutree_enqueue()` when needed, and then funnels wake-versus-defer behavior through `__call_rcu_nocb_wake()` based on queue state, lazy-callback posture, and whether interrupts are already disabled.
- `nocb_gp_wait()` is also not a leaf wait wrapper. It scans the offloaded `rcu_data` set, flushes bypass lists when pressure or age says to, advances callbacks under the live `rcu_node` lock, chooses the nearest grace-period sequence to wait for, and coordinates callback-thread wakeups while CPUs are being offloaded or re-offloaded.
- `rcu_nocb_flush_deferred_wakeup()` stays coupled to the same GP wakeup machinery because it is only a public fastpath entry into `do_nocb_deferred_wakeup()`, which still depends on the current CPU's `rcu_data`, deferred-wakeup eligibility, and the shared NOCB GP wake lock and timer policy.
The net result is still survey-only: offloaded callback enqueue, grace-period wait selection, and deferred wakeup flushing remain explicitly in C, not as a new opening for `kernel/rcu/tree_bridge.zig`.

## Idle-watch and core-invocation follow-up

This run keeps the idle-watch re-entry packet reviewable without changing the blocked bridge posture.
- `rcu_is_watching()` is not just a convenience predicate. It snapshots per-CPU watching state with preemption disabled so entry, exit, idle, and offline transitions still report whether read-side critical sections are legal on the current CPU.
- `rcu_watching_snap_save()` is not a passive counter read. Its acquire ordering and EQS check are what let force-quiescent-state logic decide whether a remote CPU really passed through dyntick idle or merely looked idle while grace-period publication was still in flight.
- `invoke_rcu_core()` is also not a narrow wake helper. It chooses between raising `RCU_SOFTIRQ` directly and waking the per-CPU `rcuc` kthread, and callers such as `call_rcu_core()` or the extended-quiescent-state re-evaluation path depend on that live watching or idle state.
The net result is still survey-only: idle-watch transitions, dyntick snapshot ordering, and core re-entry remain explicitly in C, not as a new opening for `kernel/rcu/tree_bridge.zig`.

## Public wait and barrier follow-up

This run keeps the public wait and callback-drain surfaces explicitly frozen in C.
- `synchronize_rcu()` is not just a friendly wait wrapper. Outside the boot-only vacuous path it still chooses between normal and expedited grace-period machinery, and even the early-boot fast path updates `gp_seq` and the local `rcu_node` chain directly instead of crossing a small detached contract.
- `start_poll_synchronize_rcu()` and `poll_state_synchronize_rcu_full()` are also not passive status helpers. They snapshot grace-period state with ordering barriers, lock the live root `rcu_node` path when they need to start a new GP, and rely on the exact sequencing between `rcu_state.gp_seq`, the root node's `gp_seq`, and expedited state so callers do not observe a too-short grace period.
- `rcu_barrier()` is still deeper than a generic flush primitive. It serializes concurrent barrier calls with the shared mutex and barrier sequence, inspects every CPU's callback lists, entrains callbacks across online and offline or offloaded CPUs, and waits on the shared completion before the callback-drain boundary is considered done.
The net result is still survey-only: public wait, polling-cookie, and callback-barrier ownership remain reviewable without implying a bridge candidate.

## CPU hotplug and callback migration follow-up

This run keeps CPU-enrollment, teardown, and callback migration explicitly inside the freeze boundary.
- `rcutree_prepare_cpu()` is not just a setup helper. It wires the new CPU into the live hierarchy, local callback state, and grace-period bookkeeping before the CPU can participate in ordinary Tree RCU execution.
- `rcutree_report_cpu_dead()` is not just a teardown callback. It updates the hierarchy masks and quiescent-state bookkeeping that determine whether the active grace period can advance once a CPU leaves service.
- `rcutree_migrate_callbacks()` is also not a detached list move. It rehomes live callback ownership between CPUs while preserving ordering, wakeup state, and the same overloaded or offloaded bookkeeping that ordinary callback execution uses.
The net result is still survey-only: CPU hotplug enrollment, teardown, and callback migration remain explicitly in C, not as a new opening for `kernel/rcu/tree_bridge.zig`.

## Rollback threshold

Any future Architecture Council reopen discussion must satisfy the same rollback threshold that the manifest now records.
- status bucket: `freeze_in_c`
- blocker status: `blocked_on_stay_in_c_evidence`
- owner: `Core-Adjacent Pod`
- rollback owner: `Repo Tooling Pod`
- required evidence:
  - Architecture Council reopen record linked from the reviewable packet
  - parity scorecard evidence and benchmark notes attached to the same review packet
  - validation replay command and evidence archive path recorded beside the latest blocker disposition
- automatic return-to-blocked trigger set:
  - any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the Architecture Council reopen record
  - missing parity scorecard evidence, benchmark notes, or replay command in the active review packet
  - freeze-map, survey note, or manifest drift that drops the blocked bridge disposition or rollback owner

This rollback threshold exists to stop quiet bridge momentum. A placeholder or empty `kernel/rcu/tree_bridge.zig` wrapper is not acceptable evidence and must trigger an automatic return to the blocked posture.

## Recorded gaps

The current lane state is:
- landed `phase14-build-gate`
- landed `phase14-make-target`
- landed `phase14-freeze-map-note`
- landed `phase14-rcu-tree-survey-gate`
- landed `phase14-rcu-tree-survey-note`
- landed `phase14-rcu-tree-boundary-decision-checklist`
- landed `phase14-rcu-tree-quiescent-state-followup`
- landed `phase14-rcu-tree-callback-enqueue-followup`
- landed `phase14-rcu-tree-callback-offload-followup`
- landed `phase14-rcu-tree-idle-watch-followup`
- landed `phase14-rcu-tree-public-wait-and-barrier-followup`
- landed `phase14-rcu-tree-cpu-hotplug-followup`
- landed `phase14-rcu-tree-memory-ordering-followup`
- landed `phase14-rcu-tree-rollback-threshold-guardrail`
- blocked `phase14-rcu-tree-bridge-blocker`

This keeps the lane honest: Zigux now has an explicit reviewable record that `kernel/rcu/tree.c` remains in the freeze set for now, and that the repo still does not ship a placeholder or empty `kernel/rcu/tree_bridge.zig` wrapper.

## Non-goals

This survey slice does not claim:
- a `kernel/rcu/tree_bridge.zig` implementation
- a placeholder or empty `kernel/rcu/tree_bridge.zig` wrapper
- grace-period start or completion parity
- expedited-GP CPU selection, IPI, or stall handling parity
- NOCB bypass, wakeup, or callback-offload ownership
- idle-watch or dyntick-state ownership
- quiescent-state propagation parity
- callback acceleration, callback invocation, or callback offload ownership
- public wait, polling-cookie, or callback-barrier ownership
- CPU hotplug or callback migration ownership

## Gates

This anchor-local packet stays tied to the shared Phase 14 replay routes rather than a standalone RCU-only build target.
1. run the shared validator
   - `make -C zigux phase14-validate`
2. run the focused smoke shard
   - `make -C zigux phase14-smoke`
   - `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
3. run the shared full-bundle replay
   - `make -C zigux phase14-test`
   - `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
4. run the convenience wrapper
   - `make -C zigux phase14`

## Next bounded step

Keep this packet blocked until a real Architecture Council reopen record, parity scorecard evidence, benchmark notes, and replay command all travel together in the same reviewable packet. Any drift that drops the blocked bridge disposition, rollback owner, or required evidence must force an automatic return to the blocked posture.
