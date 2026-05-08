# Phase 15 Freeze-Map Governance

This document records the bounded Phase 15 governance lane around `Documentation/zigux/freeze-map.md`.

## Status

- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_LANE_KEY=P15-L03`
- `PHASE15_SLICE=freeze-map-governance-current-freeze-blocker-evidence-verify`
- scope: the live freeze map, the existing dedicated Phase 15 manifest and test gate, the shared validator-first route already shipped for the current governance packet, and one bounded maintenance follow-up that keeps the current freeze anchor set, blocker evidence, and shared governance provenance aligned with the already-landed parity-scorecard, review-process, indefinite-C policy, retained stay-in-C closeout, and per-anchor evidence-archive reporting posture
- survey provenance refreshed against verified `master` head `4fc891b380cdd2991dff7676ade7f844df1b55fd` observed on May 8, 2026 after shared Phase 15 readback showed the freeze-map note still pointed at older verified head `9342905d34fb98d6fcd88cf2e88efed7355131d2` even though the current freeze anchor set and blocker dispositions matched the newer shared governance packet
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/check-phase15-scripts-readme-alignment.py`
  - `scripts/zigux/check-phase15-review-process-handoff.py`
  - `zigux/tests/README.md`
  - `zigux/tests/phase15_parity_scorecard.json`
  - `zigux/tests/phase15_freeze_map_manifest.json`
  - `zigux/tests/phase15_freeze_map_governance.zig`
  - `zigux/tests/phase15_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`
  - `zigux/Makefile`

## Why this slice exists

The roadmap's Phase 15 work is about governance, not another burst of deep-core implementation. The live repo now carries much more than the original freeze-map starter: the parity scorecard, Architecture Council review-process note, retained stay-in-C closeout rule, reopen-trigger catalog, indefinite-C policy note, and the shared validator-first route are all already landed.

That makes the freeze-map governance slice slightly stale. Its focused note and manifest still pointed at an older verified-head readback even though the current parity scorecard note and its machine-checkable `zigux/tests/phase15_parity_scorecard.json` manifest already carry the newer exact-head provenance, while the freeze anchor inventory and per-anchor blocker dispositions themselves remain unchanged. The shared Phase 15 scripts packet already keeps the parked governance route reviewable before the shared build replay runs.

The honest bounded step is therefore maintenance, not expansion: refresh the freeze-map-specific lane record so it matches the newer shared governance head, keep its current freeze anchor set and blocker posture explicit, and leave the root policy note aligned with the broader Phase 15 packet's closeout, reopen, and evidence-archive rules.

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
- the freeze-map anchor set and study-only scope therefore stay unchanged on current `master` and match the newer shared governance head `4fc891b380cdd2991dff7676ade7f844df1b55fd`

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
- landed `phase15-current-freeze-blocker-evidence-verify`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight: Zigux now has a reviewable and runnable governance rule for the freeze map that matches the current stay-in-C policy family, the parity-scorecard lane-owner and rollback-owner records, the machine-checkable scorecard manifest, the shared validator-first route, and the per-anchor evidence-archive reporting posture already expected by the broader Phase 15 packet. The lane also now records exact-head parity with the newer shared governance packet while keeping the freeze anchor set and blocker dispositions unchanged, instead of leaving the note parked on the older head marker. What remains blocked is any deep-core status change, not the governance scaffolding itself.

## Non-goals

This slice does not claim:

- an Architecture Council roster, schedule, or approval workflow implementation
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- any new deep-core Zig bridge or wrapper for a freeze-in-C anchor

## Gates

1. run the validator-first route
- `make -C zigux phase15-validate`

2. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

3. run the convenience target
- `make -C zigux phase15`

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode. The next honest action is to wait for one of the named reopen triggers, a drift in the shared validator-first route, or the deep-core blocker posture to change before opening another freeze-map governance slice.
