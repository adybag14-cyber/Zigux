# Phase 15 Indefinite-C Policy

This note keeps the roadmap-required Phase 15 stay-in-C policy surface explicit for code that remains in C indefinitely.

## Status

- `PHASE15_STATUS=indefinite_c_policy_packet_landed`
- `PHASE15_LANE_KEY=P15-L13`
- `PHASE15_SLICE=maintenance-mode-policy-truthfulness`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-18`
- current repo reality: the roadmap-required stay-in-C policy packet is landed and remains maintenance-only under the same blocked deep-core posture
- scope: keep the dedicated indefinite-C policy note and its direct policy vocabulary truthful without widening into neighboring Phase 15 packets

## Why this slice exists

Phase 15 is supposed to keep the mixed-language end state honest.

That requires more than a freeze map and a parity scorecard. The repo also needs one reviewable place that says when a deep-core anchor remains in C, what must still be recorded about that choice, and what evidence is required before anyone may reopen the decision later.

This packet keeps that policy surface explicit without claiming a new deep-core Zig bridge, a status change approval, or a broader Phase 15 closure.

## When the indefinite-C policy applies

This policy applies when all of the following are true:

- the anchor is still in the freeze-in-C set recorded by `Documentation/zigux/freeze-map.md`
- the current product truth is that the C implementation remains the source of truth for the present plan horizon
- the review closes with an explicit stay-in-C outcome instead of an open status-change request
- the repo still lacks narrower evidence strong enough to justify a bounded direct-port or dual-implementation claim

## Required recorded fields

When an anchor is recorded under this policy, the reviewable record must keep all of the following explicit:

- the Linux anchor path, roadmap phase, current status bucket, and requested decision bucket
- the decision record ID, lane owner, required approver set, and rollback owner
- the validation gate summary, benchmark-notes status, replay command, latest blocker disposition, and evidence archive path
- the automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh
- the parity scorecard link or blocker record, explicit non-goals, and written rationale for why the anchor remains in C

## Allowed work after an indefinite-C outcome

After an explicit stay-in-C outcome is recorded, Zigux may still carry:

- survey notes, manifests, validation gates, and blocker-accounting upkeep
- narrower evidence gathering that does not claim ownership of deep-core execution
- policy, review-process, or scorecard maintenance that keeps the blocker posture truthful

The repo must not use an indefinite-C record to justify:

- a new deep-core Zig bridge or rewrite for a freeze-in-C anchor
- silent reopening of status review without fresh named evidence
- vague optimism that erases the current blocker or source-of-truth language

## Exception posture

There is no silent exception path around the indefinite-C policy.

The only allowed exception is a documented Architecture Council reopen request that cites a named reopen trigger and carries the trigger-specific evidence refresh showing why the older blocker is no longer the current product truth.

Until that happens, the blocker remains recorded and the C implementation remains the product source of truth.

## Reopen conditions

An anchor recorded as remaining in C indefinitely may re-enter status review only when the repo can point to all of the following:

- a new bounded seam inventory
- an updated validation plan
- fresh linked evidence
- an Architecture Council review request
- the named reopen trigger now being exercised
- the trigger-specific evidence refresh that reopens the packet

## Reopen Trigger Catalog

The bounded reopen-trigger catalog for this packet is:

- `narrower_followup_answers_blocker`
- `evidence_packet_stale_or_contradictory`
- `ownership_or_validation_changed`

## Maintenance-Mode Handoff

- current lane posture: `maintenance_mode`
- replay before trusting this parked handoff:
  - `zig test zigux/tests/phase15_indefinite_c_policy.zig`
- reopen only when one of the packet-local conditions below becomes true:
  - the freeze-in-C blocker posture changes
  - the review-process packet changes its required field inventory for a stay-in-C closeout
  - the parity scorecard changes the blocked-posture accounting that this policy references
- next future target: keep this lane parked unless one of those packet-local conditions fires; if it does, reread `Documentation/zigux/phase15-indefinite-c-policy.md`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/review-checklist.md` together, then keep the repair inside this policy packet and its direct companions only

## Recorded gaps

The current lane state is:

- landed `phase15-indefinite-c-policy-note`
- landed `phase15-indefinite-c-policy-manifest`
- landed `phase15-indefinite-c-policy-test`
- landed `phase15-indefinite-c-roadmap-gap-restoration`
- landed `phase15-indefinite-c-review-process-companion-sync`
- blocked_on_stay_in_c_evidence `phase15-deep-core-status-change-blocker`

## Next bounded step

Keep this lane parked until the blocker posture changes, the Architecture Council review packet changes its stay-in-C field inventory, or the parity scorecard changes the blocked-posture accounting tied to this packet.
