# Phase 14 RCU Tree Survey

This document records the bounded Phase 14 survey lane around `kernel/rcu/tree.c`.

## Status

- `PHASE14_STATUS=freeze_in_c`
- `PHASE14_SLICE=rcu-tree-survey-gap`
- scope: the dedicated Phase 14 RCU tree survey gate, its manifest, the shared Phase 14 build wiring, and this lane note that compares the roadmap destination against the current freeze boundary without shipping a bridge
- survey provenance captured against verified `master` head `e023a288013cb2231da9a010b3934773a4b39778`
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

## Survey findings

- `kernel/rcu/tree.c` is present on `master` at 4,931 lines and remains part of the explicit freeze-in-C set.
- `kernel/rcu/tree_plugin.h`, `kernel/rcu/tree_exp.h`, and `kernel/rcu/tree_nocb.h` show that normal GP sequencing, expedited waits, and callback offload are split across tightly coupled files rather than living behind a small helper seam.
- `kernel/rcu/update.c` remains a nearby consumer of the same RCU state machine, which makes a one-file bridge story misleading.
- `Documentation/RCU/Design/Requirements/Requirements.rst` and `Documentation/RCU/Design/Memory-Ordering/Tree-RCU-Memory-Ordering.rst` reinforce that Tree RCU correctness depends on ordering and quiescent-state guarantees, not only on symbol cataloging.
- the live repo already had `zigux/tests/phase14_build.zig`, `zigux/Makefile` Phase 14 wiring, `Documentation/zigux/freeze-map.md`, the workqueue bridge lane, the ring-buffer survey lane, and the skbuff bridge lane, so the highest-value non-overlapping RCU step is a survey package that records why the roadmap destination remains blocked.
- the survey manifest now records a landed freeze-boundary checklist around grace-period sequence publication, expedited-GP funnel or stall behavior, and NOCB bypass or wakeup handoffs so later runs can deepen the audit without inventing `kernel/rcu/tree_bridge.zig`.

## Decision checklist

- landed `phase14-rcu-tree-boundary-decision-checklist`
- `grace-period-sequence-publication`: keep `rcu_start_this_gp()`, `rcu_gp_init()`, and `__note_gp_changes()` in C because `gp_seq`, `qsmask`, and `rcu_node` propagation remain coupled to the live hierarchy and ordering rules.
- `expedited-funnel-and-stall-path`: keep `sync_rcu_exp_select_cpus()`, `synchronize_rcu_expedited_wait_once()`, and `rcu_exp_gp_seq_end()` in C because CPU selection, IPI forcing, timeout handling, and sequence serialization still move together.
- `nocb-offload-wakeup-handoff`: keep `rcu_nocb_bypass_lock()`, `wake_nocb_gp_defer()`, and `do_nocb_deferred_wakeup()` in C because bypass pressure, kthread wakeups, and deferred GP signaling are still part of the same offload state machine.

## Recorded gaps

The current lane state is:

- landed `phase14-build-gate`
- landed `phase14-make-target`
- landed `phase14-freeze-map-note`
- landed `phase14-rcu-tree-survey-gate`
- landed `phase14-rcu-tree-survey-note`
- landed `phase14-rcu-tree-boundary-decision-checklist`
- ready-next `phase14-rcu-tree-quiescent-state-followup`
- blocked `phase14-rcu-tree-bridge-blocker`

This keeps the lane honest: Zigux now has an explicit reviewable record that `kernel/rcu/tree.c` remains in the freeze set for now, and that the repo still does not ship `kernel/rcu/tree_bridge.zig`.

## Non-goals

This survey slice does not claim:

- a `kernel/rcu/tree_bridge.zig` implementation
- grace-period start or completion parity
- expedited-GP CPU selection, IPI, or stall handling parity
- NOCB bypass, wakeup, or callback-offload ownership
- quiescent-state propagation parity
- callback acceleration or callback invocation ownership

## Gates

1. run the dedicated Phase 14 build
- `zig build test --build-file zigux/tests/phase14_build.zig`

2. run the convenience target
- `make -C zigux phase14`

## Next bounded step

Stay in the Phase 14 RCU tree lane and add one small survey-only audit next, limited to `rcu_report_qs_rnp()`, `note_gp_changes()`, and callback acceleration so the lane documents quiescent-state propagation without weakening the current freeze-in-C posture.
