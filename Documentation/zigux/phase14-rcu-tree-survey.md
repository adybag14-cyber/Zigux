# Phase 14 RCU Tree Survey

This document records the bounded Phase 14 survey lane around `kernel/rcu/tree.c`.

## Status

- `PHASE14_STATUS=freeze_in_c`
- `PHASE14_SLICE=rcu-tree-survey-gap`
- `PHASE14_SURVEYED_COMMIT=4e45e5a392cca82429228d42d89c480fd413042b`
- scope: the dedicated Phase 14 RCU tree survey gate, its manifest, the shared Phase 14 build wiring, and this lane note that compares the roadmap destination against the current freeze boundary without shipping a bridge
- survey provenance refreshed against verified `master` head `4e45e5a392cca82429228d42d89c480fd413042b`
- product boundary:
  - `zigux/tests/phase14_rcu_tree_survey.zig`
  - `zigux/tests/phase14_rcu_tree_manifest.json`
  - `zigux/tests/phase14_build.zig`
  - `Documentation/zigux/phase14-rcu-tree-survey.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 14 roadmap names `kernel/rcu/tree_bridge.zig` as the long-term destination for a bounded RCU tree study, but the current freeze map also lists `kernel/rcu/tree.c` in the deep-core keep-it-in-C set.

That tension matters because the live anchor is already 4,931 lines and it does not stand alone. `kernel/rcu/tree_plugin.h` adds another 1,369 lines of plugin and flavor glue, `kernel/rcu/tree_exp.h` adds 1,118 lines of expedited-GP coordination, `kernel/rcu/tree_nocb.h` adds 1,702 lines of callback-offload logic, and even nearby `kernel/rcu/update.c` still depends on the existing state machine. The upstream design references also stay large and specific: `Documentation/RCU/Design/Requirements/Requirements.rst` is 2,873 lines and `Documentation/RCU/Design/Memory-Ordering/Tree-RCU-Memory-Ordering.rst` adds another 648 lines of ordering detail.

The honest move for this lane is therefore not to start `kernel/rcu/tree_bridge.zig`. It is to make the blocked state reviewable and record the first stay-in-C checklist seams so future runs can compare the roadmap target against the current freeze boundary without overstating progress.

## Roadmap boundary map

- `zigux/tests/`: `reviewable_survey_landed` via `zigux/tests/phase14_rcu_tree_survey.zig`, which keeps the RCU tree blocker and its survey package machine-checkable beside the rest of the Phase 14 gates.
- `Documentation/zigux/`: `reviewable_survey_landed` via `Documentation/zigux/phase14-rcu-tree-survey.md`, which records the roadmap-vs-freeze comparison, the current checklist seams, and the current freeze-in-C blocker in one reviewable note.
- `kernel/rcu/tree_bridge.zig`: `blocked_on_stay_in_c_evidence` because `kernel/rcu/tree.c` is still a freeze-in-C anchor and the current survey evidence still ties grace-period publication, expedited waits, NOCB offload, quiescent-state propagation, and callback lifecycle behavior to the live Tree RCU state machine.

## Survey findings

- `kernel/rcu/tree.c` is present on `master` at 4,931 lines and remains part of the explicit freeze-in-C set.
- `kernel/rcu/tree_plugin.h`, `kernel/rcu/tree_exp.h`, and `kernel/rcu/tree_nocb.h` show that normal GP sequencing, expedited waits, and callback offload are split across tightly coupled files rather than living behind a small helper seam.
- `kernel/rcu/update.c` remains a nearby consumer of the same RCU state machine, which makes a one-file bridge story misleading.
- `Documentation/RCU/Design/Requirements/Requirements.rst` and `Documentation/RCU/Design/Memory-Ordering/Tree-RCU-Memory-Ordering.rst` reinforce that Tree RCU correctness depends on ordering and quiescent-state guarantees, not only on symbol cataloging.
- the live repo already had `zigux/tests/phase14_build.zig`, `zigux/Makefile` Phase 14 wiring, `Documentation/zigux/freeze-map.md`, the workqueue bridge lane, the ring-buffer survey lane, and the skbuff bridge lane, so the highest-value non-overlapping RCU step is a survey package that records why the roadmap destination remains blocked.
- the survey manifest now records a landed freeze-boundary checklist around grace-period sequence publication, expedited-GP funnel or stall behavior, NOCB bypass or wakeup handoffs, the quiescent-state propagation path that climbs the `rcu_node` hierarchy while also accelerating callbacks, and the callback enqueue-plus-batch path that routes through per-CPU callback lists before invocation.

## Decision checklist

- landed `phase14-rcu-tree-boundary-decision-checklist`
- `grace-period-sequence-publication`: keep `rcu_start_this_gp()`, `rcu_gp_init()`, and `__note_gp_changes()` in C because `gp_seq`, `qsmask`, and `rcu_node` propagation remain coupled to the live hierarchy and ordering rules.
- `expedited-funnel-and-stall-path`: keep `sync_rcu_exp_select_cpus()`, `synchronize_rcu_expedited_wait_once()`, and `rcu_exp_gp_seq_end()` in C because CPU selection, IPI forcing, timeout handling, and sequence serialization still move together.
- `nocb-offload-wakeup-handoff`: keep `rcu_nocb_bypass_lock()`, `wake_nocb_gp_defer()`, and `do_nocb_deferred_wakeup()` in C because bypass pressure, kthread wakeups, and deferred GP signaling are still part of the same offload state machine.
- `quiescent-state-propagation-and-callback-acceleration`: keep `rcu_report_qs_rnp()`, `note_gp_changes()`, and `rcu_accelerate_cbs()` in C because quiescent-state reporting still walks the locked `rcu_node` tree, `note_gp_changes()` still folds GP transitions into per-CPU callback state, and callback acceleration still depends on segmented callback lists plus offload state.
- `callback-enqueue-and-batch-invocation`: keep `__call_rcu_common()`, `call_rcu_core()`, and `rcu_do_batch()` in C because callback enqueue still routes through per-CPU segmented callback lists, overload tracking, NOCB offload selection, grace-period forcing, and time-bounded callback invocation.

## Quiescent-state follow-up

This run closes the previously recorded quiescent-state follow-up without changing the underlying freeze decision.

- `rcu_report_qs_rnp()` is not a leaf helper. It clears `qsmask` state under `rcu_node` locking, may recurse toward parent nodes, and ends up publishing quiescent-state completion through the live hierarchy, which makes it a poor candidate for a small standalone Zig boundary.
- `note_gp_changes()` is also not just bookkeeping. It feeds `__note_gp_changes()`, updates each CPU's local `gp_seq` view, advances or accelerates callbacks, and can trigger wakeup decisions after folding new GP state into per-CPU callback lists.
- `rcu_accelerate_cbs()` sits directly on the callback segmentation path, so even this seemingly smaller helper seam still depends on the active grace-period sequence, segmented callback lists, and offload behavior rather than a narrow data-only contract.

The net result is still survey-only: quiescent-state propagation and callback acceleration are now explicitly documented as stay-in-C behavior, not as a new opening for `kernel/rcu/tree_bridge.zig`.

## Callback enqueue and batch follow-up

This run closes the previously recorded callback enqueue follow-up without changing the underlying freeze decision.

- `__call_rcu_common()` is not just a thin callback wrapper. It validates the callback head, records debug state, chooses lazy versus hurry behavior, checks per-CPU overload, and then routes either into `call_rcu_nocb()` for offloaded CPUs or into the regular per-CPU path.
- `call_rcu_core()` is where enqueue pressure starts influencing grace-period behavior. After `rcutree_enqueue()` it can force the core awake from an extended quiescent state, fold in fresh grace-period state with `note_gp_changes()`, accelerate callbacks for a new grace period, or kick force-quiescent-state processing when queue depth crosses the live threshold.
- `rcu_do_batch()` is also still deeply coupled. It extracts ready callbacks under the NOCB lock, relies on the ordering established by prior grace-period publication, enforces batch and time limits, invokes callbacks directly, and then requeues leftovers while updating overload and force-QS bookkeeping.

The net result is still survey-only: callback enqueue, grace-period kick decisions, and callback invocation remain explicitly in C, not as a new opening for `kernel/rcu/tree_bridge.zig`.

## Callback offload and wakeup follow-up

This run closes the previously recorded callback-offload follow-up without changing the underlying freeze decision.

- `call_rcu_nocb()` is not just a detached enqueue shim. It first tries the bypass path, falls back to `rcutree_enqueue()` when needed, and then funnels wake-versus-defer behavior through `__call_rcu_nocb_wake()` based on queue state, lazy-callback posture, and whether interrupts are already disabled.
- `nocb_gp_wait()` is also not a leaf wait wrapper. It scans the offloaded `rcu_data` set, flushes bypass lists when pressure or age says to, advances callbacks under the live `rcu_node` lock, chooses the nearest grace-period sequence to wait for, and coordinates callback-thread wakeups while CPUs are being offloaded or re-offloaded.
- `rcu_nocb_flush_deferred_wakeup()` stays coupled to the same GP wakeup machinery because it is only a public fastpath entry into `do_nocb_deferred_wakeup()`, which still depends on the current CPU's `rcu_data`, deferred-wakeup eligibility, and the shared NOCB GP wake lock and timer policy.

The net result is still survey-only: offloaded callback enqueue, GP wait selection, and deferred wakeup flushing remain explicitly in C, not as a new opening for `kernel/rcu/tree_bridge.zig`.

## Rollback threshold guardrail

This run adds one narrow rollback-threshold guardrail so the lane cannot quietly drift from "blocked survey" into "bridge momentum."

- current status bucket: `freeze_in_c`
- active review blocker status: `blocked_on_stay_in_c_evidence`
- lane owner: `Core-Adjacent Pod`
- rollback owner: `Repo Tooling Pod`

Any future Architecture Council reopen attempt for `kernel/rcu/tree_bridge.zig` has to keep all of this explicit in the same reviewable packet:

- `Architecture Council reopen record linked from the reviewable packet`
- `parity scorecard evidence and benchmark notes attached to the same review packet`
- `validation replay command and evidence archive path recorded beside the latest blocker disposition`

If any of the following happens, the lane rolls straight back to the current blocked freeze posture instead of lingering in an implied review state:

- any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the Architecture Council reopen record
- `missing parity scorecard evidence, benchmark notes, or replay command in the active review packet`
- `freeze-map, survey note, or manifest drift that drops the blocked bridge disposition or rollback owner`

This is intentionally strict. The roadmap already treats `kernel/rcu/tree.c` as a freeze-in-C anchor, so the threshold for reopening review has to be stronger than "the survey changed" or "a bridge file appeared."

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
- landed `phase14-rcu-tree-rollback-threshold-guardrail`
- blocked `phase14-rcu-tree-bridge-blocker`

This keeps the lane honest: Zigux now has an explicit reviewable record that `kernel/rcu/tree.c` remains in the freeze set for now, and that the repo still does not ship `kernel/rcu/tree_bridge.zig`.

## Non-goals

This survey slice does not claim:

- a `kernel/rcu/tree_bridge.zig` implementation
- grace-period start or completion parity
- expedited-GP CPU selection, IPI, or stall handling parity
- NOCB bypass, wakeup, or callback-offload ownership
- quiescent-state propagation parity
- callback acceleration, callback invocation, or callback offload ownership

## Gates

1. run the dedicated Phase 14 build
- `zig build test --build-file zigux/tests/phase14_build.zig`

2. run the convenience target
- `make -C zigux phase14`

## Next bounded step

Keep the Phase 14 RCU tree lane parked unless the freeze posture changes. The survey now records grace-period publication, expedited waits, NOCB wakeup ownership, quiescent-state propagation, callback enqueue, callback offload, deferred wakeup flushing, and the rollback threshold that would force any weak status-review attempt back to blocked freeze posture, so another lane-local follow-up would risk inventing motion without a narrower blocker change.
