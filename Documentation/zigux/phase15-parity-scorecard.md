# Phase 15 Parity Scorecard

This document records the bounded Phase 15 governance lane for the deep-core freeze set.

## Status

- `PHASE15_STATUS=freeze_in_c_governance`
- `PHASE15_SLICE=parity-scorecard-baseline`
- scope: a reviewable scorecard that captures council inputs, evidence thresholds, validation gates, rollback ownership, and current blocker posture for the active freeze-in-C anchors
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `zigux/tests/phase15_parity_scorecard.json`
  - `zigux/tests/phase15_parity_scorecard.zig`
  - `zigux/tests/phase15_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The roadmap says Phase 15 is about honest long-term governance for the final mixed-language steady state. The live repo already records the freeze set in `Documentation/zigux/freeze-map.md`, but it still lacked the required parity scorecard that tells reviewers what evidence is needed before any frozen anchor can change status.

That gap matters because the current anchors are still large and deeply coupled: `kernel/sched/core.c` is 11,235 lines, `mm/page_alloc.c` is 7,795 lines, `kernel/rcu/tree.c` is 4,931 lines, `kernel/rcu/tree_plugin.h` is 1,369 lines, `kernel/rcu/tree_exp.h` is 1,118 lines, `kernel/rcu/tree_nocb.h` is 1,702 lines, `net/core/skbuff.c` is 7,476 lines, and `include/linux/skbuff.h` adds another 5,467 lines of shared metadata and inline rules. The repo also already carries Phase 14 blocker evidence for `kernel/rcu/tree.c` and `net/core/skbuff.c`, which makes a governance scorecard the next honest step instead of another implementation starter.

## Scorecard Entries

### `kernel/sched/core.c`

- current status: `freeze_in_c`
- current repo evidence:
  - active freeze-map anchor with no Zig surface or dedicated Phase 15 validation gate
  - large 11,235-line scheduler core still exceeds the current bounded-lane posture
- council inputs:
  - Architecture Council decision naming a narrow ownership seam
  - PMO or Release Management sign-off on rollback and release blast radius
  - Validation and Perf Team sign-off on the benchmark and regression plan
- evidence thresholds:
  - a written seam inventory that isolates one bounded scheduler responsibility
  - a proof that the candidate slice does not widen into class balancing, hotplug, or wakeup policy ownership
  - a benchmark plan with explicit latency and fairness regression thresholds
- validation gates:
  - dedicated Phase 15 scorecard test and manifest replay
  - a future lane-local parity harness before any status change
  - explicit rollback rehearsal and owner
- rollback owner: `Architecture Council + PMO / Release Management`

### `mm/page_alloc.c`

- current status: `freeze_in_c`
- current repo evidence:
  - active freeze-map anchor with no Zig surface or dedicated Phase 15 validation gate
  - large 7,795-line allocator core still exceeds the current bounded-lane posture
- council inputs:
  - Architecture Council decision naming a narrow ownership seam
  - Toolchain and Kbuild Team confirmation that the build surface stays bounded
  - Validation and Perf Team sign-off on allocator-sensitive stress coverage
- evidence thresholds:
  - a written seam inventory that isolates one bounded allocator-facing responsibility
  - proof that watermarks, reclaim interaction, and zone-balancing ownership stay in C
  - a stress-validation plan with explicit failure and rollback criteria
- validation gates:
  - dedicated Phase 15 scorecard test and manifest replay
  - a future lane-local parity harness before any status change
  - explicit rollback rehearsal and owner
- rollback owner: `Architecture Council + Validation and Perf Team`

### `kernel/rcu/tree.c`

- current status: `freeze_in_c`
- current repo evidence:
  - active freeze-map anchor with a published Phase 14 survey and blocker evidence
  - `kernel/rcu/tree.c` is 4,931 lines, with `tree_plugin.h`, `tree_exp.h`, and `tree_nocb.h` still documenting tight sidecar coupling
- council inputs:
  - Architecture Council review of the existing Phase 14 survey package
  - ABI and Runtime Team sign-off on any proposed seam ownership
  - Validation and Perf Team sign-off on quiescent-state and ordering coverage
- evidence thresholds:
  - the Phase 14 survey blockers must be answered with a narrower follow-up than the current freeze boundary
  - proof that grace-period sequencing, expedited-GP behavior, and NOCB wakeup ownership remain explicit
  - a documented ordering-validation plan before any status change
- validation gates:
  - dedicated Phase 15 scorecard test and manifest replay
  - existing Phase 14 survey evidence must stay green
  - a future lane-local parity harness before any status change
- rollback owner: `Architecture Council + ABI and Runtime Team`

### `net/core/skbuff.c`

- current status: `freeze_in_c`
- current repo evidence:
  - active freeze-map anchor with a published Phase 14 skbuff boundary survey
  - `net/core/skbuff.c` is 7,476 lines and `include/linux/skbuff.h` adds 5,467 lines of shared metadata and inline rules
- council inputs:
  - Architecture Council review of the existing Phase 14 skbuff survey package
  - Shared Subsystems Pod sign-off on the candidate boundary
  - Validation and Perf Team sign-off on packet-lifetime and checksum coverage
- evidence thresholds:
  - the Phase 14 survey blockers must be answered with a narrower follow-up than the current lifetime boundary
  - proof that refcounted lifetime, destructor ordering, checksum ownership, and segmentation ownership remain explicit
  - a documented packet-path validation plan before any status change
- validation gates:
  - dedicated Phase 15 scorecard test and manifest replay
  - existing Phase 14 survey evidence must stay green
  - a future lane-local parity harness before any status change
- rollback owner: `Architecture Council + Shared Subsystems Pod`

## Recorded Gaps

The current lane state is:

- landed `phase15-freeze-map-governance-note`
- landed `phase15-review-checklist-scorecard-question`
- landed `phase15-parity-scorecard-note`
- landed `phase15-council-review-gate`
- landed `phase15-parity-scorecard-manifest`
- landed `phase15-parity-scorecard-test`
- landed `phase15-build-gate`
- landed `phase15-make-target`
- ready-next `phase15-evidence-archive-followup`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane honest: Zigux now has a reviewable Phase 15 scorecard for the frozen anchors, but it still does not claim a scheduler slice, allocator slice, new RCU bridge, or direct skbuff rewrite.

## Architecture Council Review Gate

Before a freeze-in-C anchor can enter active status-review discussion, the scorecard record must carry one Architecture Council decision record that names:

- the decision record ID and the lane owner responsible for the proposed seam
- the current validation gate set and the rollback owner who would return the anchor to C-only operation
- the evidence archive path that preserves linked surveys and blocker follow-ups, benchmark notes, and replay commands
- the latest blocker disposition stating whether the anchor remains blocked, is ready for narrower follow-up, or has been rejected for status change

A frozen anchor leaves active discussion only after the Architecture Council sign-off, validation evidence links, rollback ownership, evidence archive path, and latest blocker disposition are all recorded together in the scorecard.

If any one of those fields is missing, stale, or contradicted by the linked evidence, the anchor remains in the freeze-in-C set and the review closes with an explicit stay-in-C outcome.

## Non-goals

This scorecard slice does not claim:

- a `kernel/sched/core.zig` surface
- a `mm/page_alloc.zig` surface
- a new `kernel/rcu/tree_bridge.zig`
- a direct `net/core/skbuff.c` rewrite
- Architecture Council approval for any status change
- completed parity harnesses for any deep-core anchor

## Gates

1. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

2. run the convenience target
- `make -C zigux phase15`

## Next bounded step

Stay in the Phase 15 governance lane and add one small evidence-archive follow-up next, limited to standardizing where Council decision records, benchmark notes, blocker dispositions, and replay commands are stored for each frozen anchor.
