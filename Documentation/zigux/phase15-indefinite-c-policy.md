# Phase 15 Indefinite-C Policy

This document records the bounded Phase 15 governance lane for the roadmap requirement covering code that remains in C indefinitely.

## Status

- `PHASE15_STATUS=indefinite_c_policy_survey_landed`
- `PHASE15_SLICE=indefinite-c-policy-current-gap-survey`
- scope: one dedicated indefinite-C policy note, one manifest, one Zig test, and one current-roadmap-gap survey refresh that records the present indefinite-C policy posture against the surrounding Phase 15 governance bundle, the docs root, and the shared replay path
- survey provenance refreshed against verified `master` head `410ee4c7aa6bdadf6b0c3b7c51a2ac90b05c5f73`
- product boundary:
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-evidence-archives/`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `zigux/tests/phase15_indefinite_c_policy.json`
  - `zigux/tests/phase15_indefinite_c_policy.zig`
  - `zigux/tests/phase15_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The roadmap says Phase 15 must include a policy for code that remains in C indefinitely. Current `master` already carries the dedicated policy note, the review checklist prompt, the Architecture Council review-process note, the parity scorecard, and the reserved per-anchor evidence-archive templates, but this lane still needs one explicit survey of the current roadmap-vs-repo gap so the policy packet records whether anything remains missing beyond the deep-core blocker posture itself.

That gap matters because the current freeze set is not just temporarily blocked work. `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` are the deep-core anchors most likely to remain C-owned for the current product plan unless an unusually strong and narrow seam appears later. Without one current survey section in the dedicated policy packet, the repo can carry the policy and its field sync while still leaving unclear whether the roadmap requirement is now locally satisfied or whether another missing governance artifact remains.

The honest bounded step is therefore to record the current answer explicitly: the roadmap-required policy bundle is now landed locally, the dedicated indefinite-C policy gap is closed at the governance layer, and the only remaining blocked work is the stronger stay-in-C exception evidence that would be needed before any deep-core status change could even reopen.

## Current Policy Gap

The current roadmap-vs-repo policy gap inside this lane is no longer a missing local governance artifact.

The roadmap-required indefinite-C policy bundle is already present locally:

- freeze-map stay-in-C policy language exists in `Documentation/zigux/freeze-map.md`
- the dedicated policy packet exists in `Documentation/zigux/phase15-indefinite-c-policy.md`
- the Architecture Council review-process packet and the parity scorecard reuse the same stay-in-C fields and reopen-trigger catalog
- the dedicated manifest and Zig test keep that policy packet machine-checkable in `zigux/tests/phase15_indefinite_c_policy.json` and `zigux/tests/phase15_indefinite_c_policy.zig`
- `Documentation/zigux/README.md` keeps the same Phase 15 governance bundle visible at the docs root
- `zigux/tests/phase15_build.zig` and `zigux/Makefile` keep the same bundle on the shared replay path through `zig build test --build-file zigux/tests/phase15_build.zig` and `make -C zigux phase15`

That keeps the current roadmap-vs-repo policy gap explicit at the docs root and the shared replay path instead of leaving the closure signal buried only in this note.

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

## Required recorded fields

When an anchor is recorded under the indefinite-C policy, the reviewable record must keep all of the following explicit:

- the Linux anchor path and the current roadmap phase
- the current status bucket and the requested decision bucket
- the decision record ID, the named owner, and the rollback owner
- the validation gate summary, the current benchmark-notes status, the evidence archive path, and the replay command reviewers should use
- the latest blocker disposition and the written rationale for why the anchor remains in C
- the retained discussion state that closes the packet as `retired_from_active_discussion` when active review ends without a status change
- the reopen triggers and the parity scorecard link or blocker record that keep the closed packet reviewable later
- the explicit non-goals that keep the packet from widening into deep-core delivery

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

The only allowed exception is an Architecture Council reopen request that cites at least one named reopen-trigger catalog item and carries the trigger-specific evidence refresh needed to show why the old packet is no longer the current product truth.

Until that happens, the existing blocker remains recorded, the C implementation remains the product source of truth, and the anchor stays in the freeze-in-C set for the current plan horizon.

## Reopen conditions

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
  - `zig build test --build-file zigux/tests/phase15_build.zig`
  - `make -C zigux phase15`
- reopen only when one of the named catalog triggers now fits the evidence packet, or when the deep-core blocker posture changes enough to justify a new bounded indefinite-C follow-up
- next future target: wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another Phase 15 slice

## Recorded gaps

The current lane state is:

- landed `phase15-indefinite-c-policy-note`
- landed `phase15-indefinite-c-policy-manifest`
- landed `phase15-indefinite-c-policy-test`
- landed `phase15-build-gate-indefinite-c-policy`
- landed `phase15-indefinite-c-field-sync-followup`
- landed `phase15-indefinite-c-current-gap-survey`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane narrow. Zigux gains a dedicated, reviewable Phase 15 policy for code that remains in C indefinitely, but it still does not claim Architecture Council approval for any status change or any new deep-core Zig ownership.

## Non-goals

This slice does not claim:

- a new decision bucket implementation across every existing Phase 15 artifact
- Architecture Council approval for any freeze-map status change
- any deep-core Zig starter, bridge, wrapper, or direct port
- removal of `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c` from the freeze-in-C set

## Gates

1. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

2. run the convenience target
- `make -C zigux phase15`

## Next bounded step

No narrower indefinite-C follow-up is justified yet. Keep this lane in maintenance mode until new stay-in-C evidence changes one of the named reopen triggers or the deep-core blocker posture changes.