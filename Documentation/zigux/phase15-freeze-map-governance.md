# Phase 15 Freeze-Map Governance

This document records the bounded Phase 15 governance lane around `Documentation/zigux/freeze-map.md`.

## Status

- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_LANE_KEY=P15-L04`
- `PHASE15_SLICE=freeze-map-governance-anchor-reporting-field-sync`
- scope: the live freeze map, the existing dedicated Phase 15 manifest and test gate, and one bounded maintenance follow-up that keeps the root freeze-map note aligned with the already-landed parity-scorecard, review-process, indefinite-C policy, retained stay-in-C closeout, and per-anchor evidence-archive reporting posture
- survey provenance refreshed against verified `master` head `9342905d34fb98d6fcd88cf2e88efed7355131d2`
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `zigux/tests/phase15_freeze_map_manifest.json`
  - `zigux/tests/phase15_freeze_map_governance.zig`
  - `zigux/tests/phase15_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The roadmap's Phase 15 work is about governance, not another burst of deep-core implementation. The live repo now carries much more than the original freeze-map starter: the parity scorecard, Architecture Council review-process note, retained stay-in-C closeout rule, reopen-trigger catalog, and indefinite-C policy note are all already landed.

That makes the original freeze-map governance slice slightly stale. Its focused note and manifest still stopped at a partial owner inventory even though the current parity scorecard now carries the authoritative per-anchor rollback owner, evidence-archive path, benchmark-notes status, replay command, and latest blocker disposition fields that the root freeze-map policy already requires.

The honest bounded step is therefore maintenance, not expansion: refresh the freeze-map-specific lane record so it matches current repo reality, align its anchor inventory with the scorecard-backed reporting fields that already govern retained stay-in-C review packets, and keep the current blocker posture explicit while the central policy note carries the same closeout and reopen rules as the later governance artifacts.

## Landed governance rules

- changes to the freeze or study lists require an explicit Architecture Council decision with written rationale
- any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate, and rollback owner in a reviewable record
- direct Zig bridge or port claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change
- the stay-in-C policy says the C implementation remains the product source of truth, and ambiguous validation must keep the code in C with an explicit blocker
- a freeze-in-C review that closes without a status change must retain the blocker, record `retired_from_active_discussion`, and keep the documented reopen triggers attached to the evidence archive
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review

## Freeze-In-C Anchor Governance Inventory

- `kernel/sched/core.c`: owner `Architecture Council`; phase `Phase 15`; status bucket `freeze_in_c`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + PMO / Release Management`; evidence archive path `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`; benchmark notes `pending_until_bounded_scheduler_seam_exists`; replay command `zig build test --build-file zigux/tests/phase15_build.zig`; latest blocker disposition `blocked_no_bounded_scheduler_seam`
- `mm/page_alloc.c`: owner `Architecture Council`; phase `Phase 15`; status bucket `freeze_in_c`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + Validation and Perf Team`; evidence archive path `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`; benchmark notes `pending_until_bounded_allocator_seam_exists`; replay command `zig build test --build-file zigux/tests/phase15_build.zig`; latest blocker disposition `blocked_no_bounded_allocator_seam`
- `kernel/rcu/tree.c`: owner `ABI and Runtime Team`; phase `Phase 15`; status bucket `freeze_in_c`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + ABI and Runtime Team`; evidence archive path `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`; benchmark notes `pending_until_rcu_followup_is_narrower_than_freeze_boundary`; replay command `zig build test --build-file zigux/tests/phase15_build.zig`; latest blocker disposition `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `net/core/skbuff.c`: owner `Shared Subsystems Pod`; phase `Phase 15`; status bucket `freeze_in_c`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + Shared Subsystems Pod`; evidence archive path `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`; benchmark notes `pending_until_skbuff_followup_is_narrower_than_lifetime_boundary`; replay command `zig build test --build-file zigux/tests/phase15_build.zig`; latest blocker disposition `blocked_packet_lifetime_boundary_still_too_wide`

## Current blocker posture

- `kernel/sched/core.c` remains blocked as `blocked_no_bounded_scheduler_seam` because the repo still has no bounded scheduler seam
- `mm/page_alloc.c` remains blocked as `blocked_no_bounded_allocator_seam` because the repo still has no bounded allocator seam
- `kernel/rcu/tree.c` remains blocked as `blocked_phase14_followup_still_wider_than_allowed_rcu_seam` because the published Phase 14 follow-up is still wider than the allowed RCU seam
- `net/core/skbuff.c` remains blocked as `blocked_packet_lifetime_boundary_still_too_wide` because the published Phase 14 follow-up is still wider than the allowed packet-lifetime boundary
- the freeze-map anchor set therefore stays unchanged on current `master`

## Recorded gaps

The current lane state is:

- landed `phase15-freeze-map-governance-doc`
- landed `phase15-freeze-map-governance-note`
- landed `phase15-build-gate`
- landed `phase15-make-target`
- landed `phase15-stay-in-c-closeout-sync`
- landed `phase15-governance-family-alignment`
- landed `phase15-blocker-ownership-sync`
- landed `phase15-anchor-reporting-field-sync`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight: Zigux now has a reviewable and runnable governance rule for the freeze map that matches the current stay-in-C policy family, the parity-scorecard lane-owner and rollback-owner records, and the per-anchor evidence-archive reporting posture already expected by the broader Phase 15 packet. What remains blocked is any deep-core status change, not the governance scaffolding itself.

## Non-goals

This slice does not claim:

- an Architecture Council roster, schedule, or approval workflow implementation
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- any new deep-core Zig bridge or wrapper for a freeze-in-C anchor

## Gates

1. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

2. run the convenience target
- `make -C zigux phase15`

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode. The next honest action is to wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another freeze-map governance slice.