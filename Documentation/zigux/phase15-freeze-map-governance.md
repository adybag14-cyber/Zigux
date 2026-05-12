# Phase 15 Freeze-Map Governance

This document records the bounded Phase 15 governance lane around `Documentation/zigux/freeze-map.md`.

## Status

- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_LANE_KEY=P15-L04`
- `PHASE15_SLICE=freeze-map-deep-core-blocker-dated-readback-alignment`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- scope: the live freeze map, the existing dedicated Phase 15 manifest and freeze-map gate, the shared validator-first route already shipped for the current governance packet, and one bounded maintenance follow-up that keeps the current freeze anchor set, blocker evidence, required approver sets, shared governance provenance, and maintenance-mode handoff aligned with the already-landed parity-scorecard, review-process, indefinite-C policy, retained stay-in-C closeout, per-anchor evidence-archive reporting posture, and an anchor-by-anchor deep-core blocker survey that compares roadmap posture against current repo reality
- survey provenance refreshed against dated `master` readback marker `current-master-readback-2026-05-12` on 2026-05-12 after live compare-against-master showed the previously recorded verified head `4fc891b380cdd2991dff7676ade7f844df1b55fd` no longer matched current `master`
- exact branch-head parity is not recorded for this packet; the parked freeze-map governance note now uses an explicit dated readback marker instead of stale exact-head provenance while keeping the same freeze anchor set and blocker posture
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/validate-phase15.py`
  - `scripts/zigux/check-phase15-scripts-readme-alignment.py`
  - `scripts/zigux/check-phase15-review-process-handoff.py`
  - `zigux/tests/README.md`
  - `zigux/tests/phase15_build.zig`
  - `zigux/tests/phase15_parity_scorecard.zig`
  - `zigux/tests/phase15_parity_scorecard.json`
  - `zigux/tests/phase15_freeze_map_manifest.json`
  - `zigux/tests/phase15_freeze_map_governance.zig`

## Why this slice exists

The roadmap's Phase 15 work is about governance, not another burst of deep-core implementation.

The live repo now carries much more than the original freeze-map starter: the parity scorecard, Architecture Council review-process note, retained stay-in-C closeout rule, reopen-trigger catalog, indefinite-C policy note, and the shared validator-first route are all already landed. That makes the freeze-map governance slice slightly stale.

Shared Phase 15 readback already corrected the packet to the newer exact head and kept the current freeze anchor set and blocker dispositions explicit, but a later compare-against-master check showed that exact-head marker has now fallen behind live `master` even though the actual freeze anchor set and blocker survey still remain the same.

The honest bounded step is therefore truthfulness maintenance, not expansion: keep the same freeze-map-specific lane record, preserve the current freeze anchor set and blocker posture, keep the compact roadmap-versus-repo blocker crosswalk, and convert the stale exact-head claim into an explicit dated readback marker while the central policy note stays aligned with the later governance artifacts' closeout, reopen, evidence-archive, required-approver-set, and maintenance-handoff rules.

## Landed governance rules

- changes to the freeze or study lists require an explicit Architecture Council decision with written rationale
- any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate, and rollback owner in a reviewable record
- direct Zig bridge or port claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change
- the stay-in-C policy says the C implementation remains the product source of truth, and ambiguous validation must keep the code in C with an explicit blocker
- a freeze-in-C review that closes without a status change must retain the blocker, record `retired_from_active_discussion`, and keep the documented reopen triggers attached to the evidence archive
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review

## Freeze-In-C Anchor Governance Inventory

- `kernel/sched/core.c`: owner `Architecture Council`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + PMO / Release Management`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + PMO / Release Management`; evidence archive path `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`; benchmark notes `pending_until_bounded_scheduler_seam_exists`; replay command `zig build test --build-file zigux/tests/phase15_build.zig`; latest blocker disposition `blocked_no_bounded_scheduler_seam`
- `mm/page_alloc.c`: owner `Architecture Council`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + Validation and Perf Team`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + Validation and Perf Team`; evidence archive path `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`; benchmark notes `pending_until_bounded_allocator_seam_exists`; replay command `zig build test --build-file zigux/tests/phase15_build.zig`; latest blocker disposition `blocked_no_bounded_allocator_seam`
- `kernel/rcu/tree.c`: owner `ABI and Runtime Team`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + ABI and Runtime Team`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + ABI and Runtime Team`; evidence archive path `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`; benchmark notes `pending_until_rcu_followup_is_narrower_than_freeze_boundary`; replay command `zig build test --build-file zigux/tests/phase15_build.zig`; latest blocker disposition `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `net/core/skbuff.c`: owner `Shared Subsystems Pod`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + Shared Subsystems Pod`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + Shared Subsystems Pod`; evidence archive path `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`; benchmark notes `pending_until_skbuff_followup_is_narrower_than_lifetime_boundary`; replay command `zig build test --build-file zigux/tests/phase15_build.zig`; latest blocker disposition `blocked_packet_lifetime_boundary_still_too_wide`

## Current blocker posture

- `kernel/sched/core.c` remains blocked as `blocked_no_bounded_scheduler_seam` because the repo still has no bounded scheduler seam
- `mm/page_alloc.c` remains blocked as `blocked_no_bounded_allocator_seam` because the repo still has no bounded allocator seam
- `kernel/rcu/tree.c` remains blocked as `blocked_phase14_followup_still_wider_than_allowed_rcu_seam` because `Documentation/zigux/phase14-rcu-tree-survey.md` on lane P14-L14 still records blocked `phase14-rcu-tree-bridge-blocker`
- `net/core/skbuff.c` remains blocked as `blocked_packet_lifetime_boundary_still_too_wide` because `Documentation/zigux/phase14-core-boundary-traceability.md` still records lane P14-L11 with blocked `phase14-skbuff-live-ownership-blocker` and no smaller ready-next gap
- the freeze-map anchor set and study-only scope therefore stay unchanged on current `master`, and this parked note now records that posture through dated readback marker `current-master-readback-2026-05-12` instead of an older exact-head claim

## Deep-core blockers versus roadmap and repo reality

- `kernel/sched/core.c`: roadmap basis `Phase 15 freeze-in-C anchor that cannot leave the deep-core freeze set until a narrower scheduler seam earns Architecture Council review.` Current repo reality: `Current master still carries only the freeze map and parity-scorecard placeholder packet for scheduler core, with no carried-forward Phase 14 blocker survey and no bounded scheduler seam.` Current blocker: `blocked_no_bounded_scheduler_seam`
- `mm/page_alloc.c`: roadmap basis `Phase 15 freeze-in-C anchor that cannot leave the deep-core freeze set until a narrower allocator seam earns Architecture Council review.` Current repo reality: `Current master still carries only the freeze map and parity-scorecard placeholder packet for page allocator core, with no carried-forward Phase 14 blocker survey and no bounded allocator seam.` Current blocker: `blocked_no_bounded_allocator_seam`
- `kernel/rcu/tree.c`: roadmap basis `Phase 15 keeps Tree RCU frozen unless a narrower-than-freeze follow-up answers the current blocker with Architecture Council reviewable evidence.` Current repo reality: `Current master already carries Documentation/zigux/phase14-rcu-tree-survey.md, where lane P14-L14 still records blocked phase14-rcu-tree-bridge-blocker and keeps Tree RCU parked in a freeze-in-C posture.` Current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `net/core/skbuff.c`: roadmap basis `Phase 15 keeps skbuff frozen unless a narrower-than-lifetime follow-up answers the current blocker with Architecture Council reviewable evidence.` Current repo reality: `Current master already carries Documentation/zigux/phase14-core-boundary-traceability.md, where the shared Phase 14 owner map still records skbuff on lane P14-L11 with blocked phase14-skbuff-live-ownership-blocker and no smaller ready-next gap.` Current blocker: `blocked_packet_lifetime_boundary_still_too_wide`

## Maintenance-Mode Handoff

- current lane posture: `maintenance_mode`
- replay before trusting this parked handoff:
  - `python3 scripts/zigux/validate-phase15.py`
  - `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-review-process-handoff.py`
  - `zig test zigux/tests/phase15_freeze_map_governance.zig`
- reopen only when one of the packet-local conditions below becomes true:
  - a freeze-map anchor changes status bucket, blocker disposition, or required approver set
  - the freeze-in-C or study-only anchor set changes in `Documentation/zigux/freeze-map.md`
  - the shared validator-first route or an adjacent Phase 15 governance packet drifts enough to change the per-anchor evidence-archive, replay-command, stay-in-C, or no-silent-exception posture recorded here
- next future target: stay in maintenance mode unless one of those packet-local reopen conditions fires; if a future truthfulness drift is freeze-map-local, reread `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `zigux/tests/phase15_freeze_map_manifest.json`, and `zigux/tests/phase15_freeze_map_governance.zig`, then keep the repair inside the freeze-map packet and its direct machine-checkable guard instead of reopening shared-summary, parity-scorecard, or readiness packets

## Recorded gaps

The current lane state is:

- landed `phase15-freeze-map-governance-doc`
- landed `phase15-freeze-map-governance-note`
- landed `phase15-build-gate`
- landed `phase15-make-target`
- landed `phase15-stay-in-c-closeout-sync`
- landed `phase15-review-process-required-field-sync`
- landed `phase15-governance-family-alignment`
- landed `phase15-blocker-ownership-sync`
- landed `phase15-freeze-map-required-approver-sync`
- landed `phase15-anchor-reporting-field-sync`
- landed `phase15-current-freeze-blocker-evidence-verify`
- landed `phase15-deep-core-blocker-roadmap-reality-survey`
- landed `phase15-dated-readback-provenance-refresh`
- landed `phase15-freeze-map-maintenance-handoff`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight: Zigux keeps the same reviewable governance rule for the freeze map, the same current stay-in-C policy family, the same parity-scorecard lane-owner and rollback-owner records, the same machine-checkable scorecard manifest, the same shared validator-first route, the same per-anchor required-approver-set inventory and evidence-archive reporting posture already expected by the broader Phase 15 packet, the same compact crosswalk that says which blocker comes straight from the roadmap freeze and which current repo evidence still keeps each deep-core anchor parked, and an explicit maintenance-mode handoff that says when the packet may reopen and which replay route should be rerun before trusting it again.

The only new maintenance claim is truthfulness: the parked note no longer implies fresh exact-head parity after live compare-against-master showed the prior recorded head had drifted behind current `master`.

## Non-goals

This slice does not claim:

- an Architecture Council roster, schedule, or approval workflow implementation
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- any new deep-core Zig bridge or wrapper for a freeze-in-C anchor

## Gates

1. run the validator-first route
   - `python3 scripts/zigux/validate-phase15.py`
   - `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`
   - `python3 scripts/zigux/check-phase15-review-process-handoff.py`
2. run the dedicated freeze-map governance gate
   - `zig test zigux/tests/phase15_freeze_map_governance.zig`

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode until one of the packet-local reopen conditions fires or a real change in one anchor's blocker evidence lands.