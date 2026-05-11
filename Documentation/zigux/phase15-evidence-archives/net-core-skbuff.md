# Phase 15 Evidence Archive: `net/core/skbuff.c`

This reserved Architecture Council evidence archive keeps the current stay-in-C record explicit for `net/core/skbuff.c`.

## Current Posture

- Linux anchor path: `net/core/skbuff.c`
- current roadmap phase: `Phase 15`
- current status bucket: `freeze_in_c`
- requested decision bucket: `keep_in_c`
- current approval state: `no_freeze_map_status_change_approved`
- decision record ID: `reserved-for-future-architecture-council-reopen-request`
- lane owner: `Shared Subsystems Pod`
- required approver set: `Architecture Council + Shared Subsystems Pod`
- rollback owner: `Architecture Council + Shared Subsystems Pod`
- validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`
- evidence archive path: `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`
- parity scorecard link: `Documentation/zigux/phase15-parity-scorecard.md`
- indefinite-C policy link: `Documentation/zigux/phase15-indefinite-c-policy.md`

## Blocker Evidence

- latest blocker disposition: `blocked_packet_lifetime_boundary_still_too_wide`
- benchmark-notes status: `pending_until_skbuff_followup_is_narrower_than_lifetime_boundary`
- replay command: `zig build test --build-file zigux/tests/phase15_build.zig`
- rollback threshold: reopen and return the anchor to an explicitly blocked review state immediately if the evidence packet becomes stale or contradictory, if ownership or validation changes, or if any proposed skbuff follow-up is still wider than the approved lifetime boundary
- automatic return-to-blocked trigger: any attempted status-change claim without fresh Architecture Council reopen evidence, current blocker refresh, and replay-backed validation

## Retained Stay-In-C Closeout

- retained discussion state: `retired_from_active_discussion`
- reopen triggers:
  - `narrower_followup_answers_blocker`
  - `evidence_packet_stale_or_contradictory`
  - `ownership_or_validation_changed`
- written rationale: the current product plan still lacks a skbuff follow-up that is narrower than the blocked packet-lifetime boundary, so the C implementation remains the product source of truth for this plan horizon

## Explicit Non-Goals

- no `net/core/skbuff.zig` starter
- no direct skbuff ownership claim for Zigux
- no silent freeze-map status change
- no implied Architecture Council approval beyond the blocked maintenance posture already recorded on current `master`
