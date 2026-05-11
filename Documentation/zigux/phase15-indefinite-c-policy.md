# Phase 15 Indefinite-C Policy

This document records the bounded Phase 15 governance lane for the roadmap requirement covering code that remains in C indefinitely.

## Status

- `PHASE15_STATUS=indefinite_c_policy_packet_restored`
- `PHASE15_LANE_KEY=P15-L02`
- `PHASE15_SLICE=indefinite-c-policy-packet-restore`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- survey provenance refreshed against dated current-master readback marker `current-master-readback-2026-05-11` on 2026-05-11 after shared Phase 15 summaries, validator wiring, and governance-lane sequencing still pointed at a dedicated indefinite-C policy packet while the dedicated note and its paired manifest plus Zig guard were missing from current `master`
- scope: one dedicated indefinite-C policy note, one manifest, one Zig test, and the minimum stay-in-C truthfulness record needed to restore the roadmap-required policy packet without reopening freeze-map, parity-scorecard, or shared-summary ownership beyond their existing current-head wording
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-governance-lane-sequencing.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `zigux/tests/phase15_indefinite_c_policy.json`
  - `zigux/tests/phase15_indefinite_c_policy.zig`

## Why this slice exists

The roadmap says Phase 15 must include a policy for code that remains in C indefinitely. Current `master` already carries the freeze map, the review-process packet, the shared validator-first reminders, and the governance-lane sequencing note that all point at a dedicated indefinite-C policy packet.

That gap matters because the current freeze set is not just temporarily blocked work. `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` are the deep-core anchors most likely to remain C-owned for the current product plan unless an unusually strong and narrow seam appears later. Shared summaries cannot honestly point at a dedicated stay-in-C packet if that packet is absent.

The honest bounded step is therefore to restore the missing indefinite-C packet, keep the stay-in-C record reviewable, and close the roadmap-vs-repo policy gap without claiming any new Architecture Council approval or deep-core status change.

## Current Policy Gap

The current roadmap-vs-repo policy gap that motivated this lane was a missing local governance artifact.

Shared Phase 15 surfaces already pointed at an indefinite-C packet, but the dedicated note and its paired manifest plus Zig guard were missing from current `master`.

This slice closes that local governance gap:

- freeze-map stay-in-C policy language exists in `Documentation/zigux/freeze-map.md`
- the dedicated policy packet now exists in `Documentation/zigux/phase15-indefinite-c-policy.md`
- the Architecture Council review-process packet and the review checklist already reuse the same stay-in-C fields, retained closeout state, and reopen-trigger catalog
- the dedicated manifest and Zig test now keep that policy packet machine-checkable in `zigux/tests/phase15_indefinite_c_policy.json` and `zigux/tests/phase15_indefinite_c_policy.zig`

That closes the current policy gap for the roadmap requirement `policy for code that remains in C indefinitely`.

The remaining blocked work is not another missing policy artifact. It is the already-recorded deep-core status-change blocker:

- no bounded scheduler seam is approved yet
- no bounded page-allocator seam is approved yet
- the current RCU follow-up is still wider than the allowed seam
- the current skbuff follow-up is still wider than the allowed packet-lifetime boundary

This lane therefore stays in maintenance mode unless one of those blocker postures changes enough to justify another bounded indefinite-C follow-up.

## When the indefinite-C policy applies

This policy applies when all of the following are true:

- the anchor is still in the freeze-in-C set recorded by `Documentation/zigux/freeze-map.md`
- Architecture Council review, the parity scorecard, and the current evidence-archive packet do not show evidence strong enough for a bounded dual-implementation or direct-port claim
- the current product decision is that the existing C implementation remains the product source of truth for the current plan horizon and remains in C indefinitely for that plan horizon
- the lane needs to close with an explicit stay-in-C outcome instead of leaving the anchor in recurring open discussion

This policy does not claim a permanent forever verdict. It records the current long-term product posture honestly and says what evidence would be needed before the repo reopens the question.

## Required Recorded Fields

When an anchor is recorded under the indefinite-C policy, the reviewable record must keep all of the following explicit:

- the Linux anchor path and the current roadmap phase
- the current status bucket and the requested decision bucket
- the decision record ID, the named owner, the required approver set, and the rollback owner
- the validation gate summary, the current benchmark-notes status, the evidence archive path, and the replay command reviewers should use
- the latest blocker disposition and the written rationale for why the anchor remains in C
- the retained discussion state that closes the packet as `retired_from_active_discussion` when active review ends without a status change
- the automatic return-to-blocked trigger that makes stale evidence, missing record fields, or rollback-threshold drift send the anchor back to blocked review posture
- the reopen triggers and the parity scorecard link or blocker record that keep the closed packet reviewable later
- the explicit non-goals that keep the packet from widening into deep-core delivery

## Allowed Work After an Indefinite-C Outcome

After an explicit stay-in-C outcome is recorded, Zigux may still carry:

- survey notes, boundary manifests, validation gates, and explicit non-goal records
- narrower evidence gathering that does not claim ownership of scheduler, MM, RCU, skbuff, or other deep-core execution
- checklist, scorecard, policy-note, or archive upkeep that keeps blocker state honest

The repo must not use an indefinite-C record to justify:

- a new `kernel/sched/core.zig` or `mm/page_alloc.zig`
- a new `kernel/rcu/tree_bridge.zig` or direct `net/core/skbuff.c` rewrite
- silent reopening of status review without new evidence
- vague optimism that erases the current blocker or source-of-truth language

## Exception Posture

There is no silent exception path around the indefinite-C policy.

The only allowed exception is an Architecture Council reopen request that cites at least one named reopen-trigger catalog item and carries the trigger-specific evidence refresh needed to show why the old packet is no longer the current product truth.

Until that happens, the existing blocker remains recorded, the C implementation remains the product source of truth, and the anchor stays in the freeze-in-C set for the current plan horizon.

## Reopen Conditions

An anchor recorded as remaining in C indefinitely may re-enter status review only when the repo can point to an Architecture Council review request that names at least one bounded reopen-trigger catalog item explicitly instead of implying silent drift.

Each trigger keeps its own minimum evidence:

- `narrower_followup_answers_blocker`: a new bounded seam inventory that is narrower than the current freeze boundary, plus an updated validation plan and rollback owner for that narrower seam
- `evidence_packet_stale_or_contradictory`: refreshed linked evidence in the evidence archive showing which validation, benchmark, survey, or blocker record has become stale or contradictory and what the current blocker disposition should be now
- `ownership_or_validation_changed`: refreshed lane-owner, rollback-owner, or validation-gate evidence showing exactly which ownership or validation change invalidated the closed stay-in-C packet

If none of those trigger-specific reopen conditions is met, the anchor remains in C and the review closes with the existing blocker still recorded.

## Reopen Trigger Catalog

The bounded reopen-trigger catalog for a retained stay-in-C packet is:

- `narrower_followup_answers_blocker`: a narrower seam inventory or follow-up now answers the latest blocker disposition without widening the approved boundary
- `evidence_packet_stale_or_contradictory`: linked validation, benchmark, survey, or blocker evidence has become stale or contradictory enough that the closed packet no longer stands on its own
- `ownership_or_validation_changed`: rollback ownership, lane ownership, or validation gates changed enough to invalidate the closed stay-in-C packet

Every retained stay-in-C closeout must cite at least one of these catalog items in its evidence archive so the policy note, review-process packet, parity scorecard, and per-anchor archive template keep the same reopen vocabulary.

## Maintenance-Mode Handoff

- current lane posture: `maintenance_mode`
- replay before trusting this parked handoff:
  - `make -C zigux phase15-validate`
  - `make -C zigux phase15-test`
  - `make -C zigux phase15`
- reopen only when one of the named catalog triggers now fits the evidence packet, or when the deep-core blocker posture changes enough to justify a new bounded indefinite-C follow-up
- next future target: wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another Phase 15 slice

## Recorded Gaps

The current lane state is:

- landed `phase15-indefinite-c-policy-note`
- landed `phase15-indefinite-c-policy-manifest`
- landed `phase15-indefinite-c-policy-test`
- landed `phase15-indefinite-c-current-gap-survey`
- landed `phase15-indefinite-c-maintenance-handoff`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane narrow. Zigux gains the dedicated, reviewable Phase 15 policy for code that remains in C indefinitely that the shared governance packet already expected, but it still does not claim Architecture Council approval for any status change or any new deep-core Zig ownership.

## Non-goals

This slice does not claim:

- Architecture Council approval for any freeze-map status change
- any deep-core Zig starter, bridge, wrapper, or direct port
- removal of `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c` from the freeze-in-C set
- broader shared-summary rewrites outside the restored stay-in-C packet

## Next Bounded Step

No narrower indefinite-C follow-up is justified yet. Keep this lane in maintenance mode until new stay-in-C evidence changes one of the named reopen triggers or the deep-core blocker posture changes.