# Phase 15 Freeze-Map Governance

This document records the bounded Phase 15 governance lane around `Documentation/zigux/freeze-map.md`.

## Status

- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_LANE_KEY=P15-L04`
- `PHASE15_SLICE=freeze-map-deep-core-blocker-dated-readback-alignment`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- scope: the live freeze map, the existing dedicated Phase 15 manifest and freeze-map gate, the checker-backed shared reminder packet, the directly materialized handoff manifest, the broader validator-first, dedicated-build, lane-owner, and make-wrapper route names that adjacent reminder surfaces still mention for truthfulness checks, with the current GitHub contents path in this runtime still returning not-found for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`, direct contents readback now resolving `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, and the current `zigux/Makefile` readback still carrying no `phase15-validate`, `phase15-test`, or `phase15` targets, so the lane-owner companion stays recorded as adjacent direct-readback evidence while the validator-first, dedicated-build, and make-wrapper route names remain adjacent repo-reality-gap vocabulary rather than freeze-map-local ownership
- survey provenance refreshed against dated `master` readback marker `current-master-readback-2026-05-20` on 2026-05-20 after a fresh live reread confirmed the freeze anchor set and blocker posture still match current repo reality, the current GitHub contents path in this runtime still returns not-found for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`, direct contents readback now resolves `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, and the current `zigux/Makefile` readback still carries no `phase15-validate`, `phase15-test`, or `phase15` targets, so this lane now keeps the lane-owner companion in the adjacent-evidence bucket while the validator-first, dedicated-build, and wrapper-route names remain adjacent repo-reality-gap vocabulary instead of freeze-map-local landed evidence
- exact branch-head parity is not recorded for this packet; the parked freeze-map governance note now uses an explicit dated readback marker instead of stale exact-head provenance while keeping the same freeze anchor set and blocker posture
- direct lane-owned boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `zigux/tests/phase15_freeze_map_manifest.json`
  - `zigux/tests/phase15_freeze_map_governance.zig`
- adjacent Phase 15 parity-scorecard, review-process, indefinite-C-policy, readiness, handoff, and shared-summary surfaces still inform this lane's truthfulness checks, while the validator-first, dedicated-build, and make-wrapper route names remain gap-tracked reminder vocabulary and the returned lane-owner replay remains adjacent readback evidence rather than a lane-owned boundary file here

## Why this slice exists

The roadmap's Phase 15 work is about governance, not another burst of deep-core implementation.

The live repo now carries much more than the original freeze-map starter: the parity scorecard, Architecture Council review-process note, retained stay-in-C closeout rule, reopen-trigger catalog, indefinite-C policy note, the shared-summary gap note, and the dedicated handoff manifest are already materialized on current `master`. The current GitHub contents path in this runtime still does not resolve the adjacent shared validator and dedicated-build companions, direct contents readback does resolve the lane-owner replay, and the current `zigux/Makefile` readback still carries no `phase15-*` targets.

The honest bounded step is therefore truthfulness maintenance, not expansion: keep the same freeze-map-specific lane record, preserve the current freeze anchor set and blocker posture, keep the compact roadmap-versus-repo blocker crosswalk, refresh the dated readback marker, and keep the lane boundary consistent with the directly materialized handoff plus the adjacent reminder-route vocabulary without promoting the shared validator, dedicated-build, or wrapper routes into freeze-map-local ownership, without demoting the returned lane-owner replay back into gap vocabulary, and while keeping the validator-first, dedicated-build, and wrapper-route names in the adjacent repo-reality-gap bucket.

## Landed governance rules

- changes to the freeze or study lists require an explicit Architecture Council decision with written rationale
- any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate summary, and rollback owner in a reviewable record
- direct Zig bridge or port claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change
- the stay-in-C policy says the C implementation remains the product source of truth, and ambiguous validation must keep the code in C with an explicit blocker
- a freeze-in-C review that closes without a status change must retain the `freeze_in_c` decision, the current blocker, and the required approver set, record `retired_from_active_discussion`, and keep the evidence archive path plus documented reopen triggers attached to the closeout record
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review

## Freeze-In-C Anchor Governance Inventory

- `kernel/sched/core.c`: owner `Architecture Council`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + PMO / Release Management`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + PMO / Release Management`; evidence archive path `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`; benchmark notes `pending_until_bounded_scheduler_seam_exists`; replay command `zig test zigux/tests/phase15_freeze_map_governance.zig`; latest blocker disposition `blocked_no_bounded_scheduler_seam`
- `mm/page_alloc.c`: owner `Architecture Council`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + Validation and Perf Team`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + Validation and Perf Team`; evidence archive path `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`; benchmark notes `pending_until_bounded_allocator_seam_exists`; replay command `zig test zigux/tests/phase15_freeze_map_governance.zig`; latest blocker disposition `blocked_no_bounded_allocator_seam`
- `kernel/rcu/tree.c`: owner `ABI and Runtime Team`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + ABI and Runtime Team`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + ABI and Runtime Team`; evidence archive path `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`; benchmark notes `pending_until_rcu_followup_is_narrower_than_freeze_boundary`; replay command `zig test zigux/tests/phase15_freeze_map_governance.zig`; latest blocker disposition `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `net/core/skbuff.c`: owner `Shared Subsystems Pod`; phase `Phase 15`; status bucket `freeze_in_c`; required approver set `Architecture Council + Shared Subsystems Pod`; validation gate `Phase 15 parity scorecard plus Architecture Council reopen record`; rollback owner `Architecture Council + Shared Subsystems Pod`; evidence archive path `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`; benchmark notes `pending_until_skbuff_followup_is_narrower_than_lifetime_boundary`; replay command `zig test zigux/tests/phase15_freeze_map_governance.zig`; latest blocker disposition `blocked_packet_lifetime_boundary_still_too_wide`

## Current blocker posture

- `kernel/sched/core.c` remains blocked as `blocked_no_bounded_scheduler_seam` because the repo still has no bounded scheduler seam
- `mm/page_alloc.c` remains blocked as `blocked_no_bounded_allocator_seam` because the repo still has no bounded allocator seam
- `kernel/rcu/tree.c` remains blocked as `blocked_phase14_followup_still_wider_than_allowed_rcu_seam` because `Documentation/zigux/phase14-rcu-tree-survey.md` on lane P14-L16 still records blocked `phase14-rcu-tree-bridge-blocker`
- `net/core/skbuff.c` remains blocked as `blocked_packet_lifetime_boundary_still_too_wide` because `Documentation/zigux/phase14-skbuff-bridge-survey.md` on lane P14-L11 now records live blocker `phase14-skbuff-live-ownership-blocker` while keeping the surviving skbuff packet review-first and `boundary_map_only`, and that note says explicit stay-in-C ownership for qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, destructor coordination, segmentation metadata, and the final sock-owned tail transfer remains the Phase 14 boundary, while `Documentation/zigux/phase14-core-boundary-traceability.md` still keeps skbuff in retained-in-C posture and warns against treating the packet as a live bridge or status-change claim
- the freeze-map anchor set and study-only scope therefore stay unchanged on current `master`, and this parked note now records that posture through dated readback marker `current-master-readback-2026-05-20` instead of the older 2026-05-19 marker

## Deep-core blockers versus roadmap and repo reality

- `kernel/sched/core.c`: roadmap basis `Phase 15 freeze-in-C anchor that cannot leave the deep-core freeze set until a narrower scheduler seam earns Architecture Council review.` Current repo reality: `Current master still carries the freeze map, the dedicated freeze-map governance packet, and the parity scorecard baseline for scheduler core, while the current GitHub contents path in this runtime still returns not-found for the shared Phase 15 validator and dedicated-build companions, direct contents readback now resolves zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig, the current zigux/Makefile readback still carries no phase15-validate, phase15-test, or phase15 targets, and there is still no carried-forward Phase 14 blocker survey or bounded scheduler seam.` Current blocker: `blocked_no_bounded_scheduler_seam`
- `mm/page_alloc.c`: roadmap basis `Phase 15 freeze-in-C anchor that cannot leave the deep-core freeze set until a narrower allocator seam earns Architecture Council review.` Current repo reality: `Current master still carries the freeze map, the dedicated freeze-map governance packet, and the parity scorecard baseline for page allocator core, while the current GitHub contents path in this runtime still returns not-found for the shared Phase 15 validator and dedicated-build companions, direct contents readback now resolves zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig, the current zigux/Makefile readback still carries no phase15-validate, phase15-test, or phase15 targets, and there is still no carried-forward Phase 14 blocker survey or bounded allocator seam.` Current blocker: `blocked_no_bounded_allocator_seam`
- `kernel/rcu/tree.c`: roadmap basis `Phase 15 keeps Tree RCU frozen unless a narrower-than-freeze follow-up answers the current blocker with Architecture Council reviewable evidence.` Current repo reality: `Current master already carries Documentation/zigux/phase14-rcu-tree-survey.md, where lane P14-L16 still records blocked phase14-rcu-tree-bridge-blocker and keeps Tree RCU parked in a freeze-in-C posture, while the current GitHub contents path in this runtime still returns not-found for the shared Phase 15 validator and dedicated-build companions, direct contents readback now resolves zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig, and the current zigux/Makefile readback still carries no phase15-validate, phase15-test, or phase15 targets.` Current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `net/core/skbuff.c`: roadmap basis `Phase 15 keeps skbuff frozen unless a narrower-than-lifetime follow-up answers the current blocker with Architecture Council reviewable evidence.` Current repo reality: `Current master already carries Documentation/zigux/phase14-skbuff-bridge-survey.md, where lane P14-L11 now records live blocker phase14-skbuff-live-ownership-blocker while keeping the surviving skbuff packet review-first and boundary_map_only, stating that explicit stay-in-C ownership for qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, destructor coordination, segmentation metadata, and the final sock-owned tail transfer remains the Phase 14 boundary, while Documentation/zigux/phase14-core-boundary-traceability.md still keeps skbuff in retained-in-C posture and warns against treating the packet as a live bridge or status-change claim; the current GitHub contents path in this runtime still returns not-found for the shared Phase 15 validator and dedicated-build companions, direct contents readback now resolves zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig, and the current zigux/Makefile readback still carries no phase15-validate, phase15-test, or phase15 targets.` Current blocker: `blocked_packet_lifetime_boundary_still_too_wide`

## Maintenance-Mode Handoff

- current lane posture: `maintenance_mode`
- replay before trusting this parked handoff:
  - `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-review-process-handoff.py`
  - `python3 scripts/zigux/check-phase15-shared-summary-gap.py`
  - `zig test zigux/tests/phase15_freeze_map_governance.zig`
- adjacent gap-tracked validator-first, dedicated-build, and make-wrapper route names plus the returned lane-owner replay that still inform this packet's truthfulness checks:
  - `scripts/zigux/validate-phase15.py`
  - `zigux/tests/phase15_build.zig`
  - `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
  - `make -C zigux phase15-validate`
  - `make -C zigux phase15-test`
  - `make -C zigux phase15`
- the current GitHub contents path in this runtime still returns not-found for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`, direct contents readback now resolves `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, and the current `zigux/Makefile` readback still carries no `phase15-validate`, `phase15-test`, or `phase15` targets, so the lane-owner replay stays direct landed evidence while the validator-first, dedicated-build, and wrapper-route names remain adjacent gap vocabulary.
- reopen only when one of the packet-local conditions below becomes true:
  - a freeze-map anchor changes status bucket, blocker disposition, or required approver set
  - the freeze-in-C or study-only anchor set changes in `Documentation/zigux/freeze-map.md`
  - the checker-backed shared reminder packet or an adjacent Phase 15 governance packet drifts enough to change the per-anchor evidence-archive, replay-command, stay-in-C, or no-silent-exception posture recorded here
- next future target: stay in maintenance mode unless one of those packet-local reopen conditions fires; if a future truthfulness drift is freeze-map-local, reread `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `zigux/tests/phase15_freeze_map_manifest.json`, `zigux/tests/phase15_freeze_map_governance.zig`, `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, and `scripts/zigux/check-phase15-shared-summary-gap.py` together, then re-check whether the current GitHub contents path in this runtime still returns not-found for `scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`, whether direct contents readback still resolves `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, and whether `zigux/Makefile` still lacks any phase15 routes before keeping the repair inside the freeze-map packet and its direct machine-checkable guard while keeping the lane-owner replay as direct contents-readback evidence and the validator-first, dedicated-build, and wrapper-route names as adjacent repo-reality-gap evidence instead of freeze-map-local ownership

## Recorded gaps

The current lane state is:

- landed `phase15-freeze-map-governance-doc`
- landed `phase15-freeze-map-governance-note`
- landed `phase15-freeze-map-manifest`
- landed `phase15-freeze-map-governance-gate`
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
- materialized_in_contents_readback `phase15-shared-lane-owner-readback`
- repo_reality_gap_confirmed `phase15-shared-validator-route-gap`
- repo_reality_gap_confirmed `phase15-shared-build-route-gap`
- repo_reality_gap_confirmed `phase15-shared-wrapper-route-gap`
- blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`

This keeps the lane tight: Zigux keeps the same reviewable governance rule for the freeze map, the same current stay-in-C policy family, the same adjacent parity-scorecard lane-owner and rollback-owner records, the same checker-backed shared reminder packet, the same per-anchor required-approver-set inventory and evidence-archive reporting posture already expected by the broader Phase 15 packet, the same compact crosswalk that says which blocker comes straight from the roadmap freeze and which current repo evidence still keeps each deep-core anchor parked, and an explicit maintenance-mode handoff that says when the packet may reopen and which direct checker and dedicated freeze-map gate should be rerun before trusting it again.

The only new maintenance claim is truthfulness: the parked note now records the current 2026-05-20 dated readback, keeps the direct checker-backed governance packet explicit, keeps the directly readable lane-owner replay visible as adjacent materialized evidence, and keeps the validator-first, dedicated-build, and wrapper-route names visible as adjacent shared repo-reality gaps instead of treating any of them as freeze-map-local ownership.

## Non-goals

This slice does not claim:

- an Architecture Council roster, schedule, or approval workflow implementation
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- any new deep-core Zig bridge or wrapper for a freeze-in-C anchor

## Gates

1. run the checker-backed shared reminder packet
   - `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`
   - `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`
   - `python3 scripts/zigux/check-phase15-review-process-handoff.py`
   - `python3 scripts/zigux/check-phase15-shared-summary-gap.py`
2. run the dedicated freeze-map governance gate
   - `zig test zigux/tests/phase15_freeze_map_governance.zig`

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode until one of the packet-local reopen conditions fires, one of the adjacent checker-backed reminder surfaces drifts away from the packet's recorded posture, or a real change in one anchor's blocker evidence lands.