# Phase 15 Indefinite-C Policy

This document records the bounded Phase 15 governance lane for the roadmap requirement covering code that remains in C indefinitely.

## Status

- `PHASE15_STATUS=indefinite_c_policy_packet_landed`
- `PHASE15_LANE_KEY=P15-L16`
- `PHASE15_SLICE=indefinite-c-policy-lane-owner-and-exception-posture-sync`
- `PHASE15_PROVENANCE_MODE=exact_master_commit_readback`
- survey provenance refreshed against current `master` commit `7b5519444e8f73f84c68dc3e63580fcaef06ffb6`
- scope: one dedicated indefinite-C policy note, one manifest, one Zig test, the focused blocker-evidence and lane-owner-alignment replays already shipped in the shared Phase 15 build, and one packet-local maintenance handoff that keeps future truthfulness repairs inside the stay-in-C packet

## Why this slice exists

The roadmap says Phase 15 must include a policy for code that remains in C indefinitely.

Current `master` already carries the freeze map, the review-process note, the parity scorecard, the reserved per-anchor evidence archives, and the focused blocker-evidence plus lane-owner-alignment replays. This dedicated policy packet keeps that long-term stay-in-C posture reviewable in one place instead of leaving it distributed only across adjacent governance artifacts.

## When the indefinite-C policy applies

This policy applies when all of the following are true:

- the anchor is still in the freeze-in-C set recorded by `Documentation/zigux/freeze-map.md`
- the current product decision is that the existing C implementation remains the product source of truth for the current plan horizon and remains in C indefinitely for that plan horizon
- the lane needs to close with an explicit stay-in-C outcome instead of leaving the anchor in recurring open discussion
- the current evidence still does not justify a bounded dual-implementation or direct-port claim

## Required recorded fields

When an anchor is recorded under the indefinite-C policy, the reviewable record must keep all of the following explicit:

- the exact Linux anchor path, the current roadmap phase, the current status bucket, and the requested decision bucket
- the decision record ID, the lane owner, the required approver set, and the rollback owner
- the validation gate summary, the current benchmark-notes status, the replay command, the latest blocker disposition, and the evidence archive path
- the automatic return-to-blocked trigger, the retained discussion state that closes the packet as `retired_from_active_discussion` when active review ends without a status change, and the named reopen-trigger catalog item or items that justify later reopening
- the parity scorecard link or blocker record, the explicit non-goals, and the written rationale for why the anchor remains in C

## Allowed work after an indefinite-C outcome

After an explicit stay-in-C outcome is recorded, Zigux may still carry:

- survey notes, boundary manifests, validation gates, and explicit non-goal records
- narrower evidence gathering that does not claim ownership of scheduler, MM, RCU, skbuff, or other deep-core execution
- checklist, scorecard, policy-note, or archive upkeep that keeps blocker state honest

The repo must not use an indefinite-C record to justify:

- a new `kernel/sched/core.zig` or `mm/page_alloc.zig`
- a new `kernel/rcu/tree_bridge.zig` or direct `net/core/skbuff.c` rewrite
- silent reopening of status review without new evidence
- vague optimism that erases the current blocker or source-of-truth language

## Exception posture

There is no silent exception path around the indefinite-C policy.

The only allowed exception is an Architecture Council reopen request that satisfies the documented reopen conditions and carries fresh linked evidence showing why the old blocker is no longer the current product truth.

That reopen request must cite a named reopen-trigger catalog item and a trigger-specific evidence refresh before it can ask the repo to revisit the retained stay-in-C outcome.

Until that happens, the existing blocker remains recorded, the C implementation remains the product source of truth, and the anchor stays in the freeze-in-C set for the current plan horizon.

## Reopen conditions

An anchor recorded as remaining in C indefinitely may re-enter status review only when the repo can point to all of the following:

- a new bounded seam inventory
- an updated validation plan
- fresh linked evidence
- an Architecture Council review request
- the named reopen-trigger catalog item that now applies
- the trigger-specific evidence refresh that reopens the packet

## Reopen Trigger Catalog

The bounded reopen-trigger catalog for a retained stay-in-C packet is:

- `narrower_followup_answers_blocker`
- `evidence_packet_stale_or_contradictory`
- `ownership_or_validation_changed`

## Maintenance-Mode Handoff

- current lane posture: `maintenance_mode`
- replay before trusting this parked handoff:
  - `zig test zigux/tests/phase15_indefinite_c_policy.zig`
  - `zig test zigux/tests/phase15_indefinite_c_blocker_evidence.zig`
  - `zig test zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
  - `zig build test --build-file zigux/tests/phase15_build.zig`
- reopen only when one of the packet-local conditions below becomes true:
  - a named reopen-trigger catalog item now fits fresh stay-in-C evidence and includes the trigger-specific evidence refresh
  - the deep-core blocker posture, parity scorecard blocker record, or freeze-in-C anchor inventory changes enough to invalidate the parked policy packet
  - the Architecture Council review-process fields, lane-owner vocabulary, or supporting-artifact route drift enough to change the policy packet's truthfulness
- next future target: keep this lane in maintenance mode unless one of those packet-local reopen conditions fires; if a future truthfulness drift is indefinite-C-policy-local, reread `Documentation/zigux/phase15-indefinite-c-policy.md`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `Documentation/zigux/phase15-architecture-council-review-process.md`, and `Documentation/zigux/phase15-parity-scorecard.md` together, then keep the repair inside the policy packet and its direct replays instead of reopening freeze-map, readiness, handoff, or shared-summary maintenance

## Recorded gaps

The current lane state is:

- landed `phase15-indefinite-c-policy-note`
- landed `phase15-indefinite-c-policy-manifest`
- landed `phase15-indefinite-c-policy-test`
- landed `phase15-build-gate-indefinite-c-policy`
- landed `phase15-indefinite-c-field-sync-followup`
- landed `phase15-indefinite-c-maintenance-handoff`
- blocked `phase15-deep-core-status-change-blocker`

## Next bounded step

Keep this lane in maintenance mode until new stay-in-C evidence changes one of the named reopen triggers or the deep-core blocker posture changes.