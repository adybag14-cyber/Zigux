# Phase 15 Evidence Archive: `kernel/sched/core.c`

This reserved Architecture Council evidence archive keeps the current stay-in-C record explicit for `kernel/sched/core.c`.

## Current Posture

- Linux anchor path: `kernel/sched/core.c`
- current roadmap phase: `Phase 15`
- current status bucket: `freeze_in_c`
- requested decision bucket: `keep_in_c`
- current approval state: `no_freeze_map_status_change_approved`
- decision record ID: `reserved-for-future-architecture-council-reopen-request`
- lane owner: `Architecture Council`
- required approver set: `Architecture Council + PMO / Release Management`
- rollback owner: `Architecture Council + PMO / Release Management`
- validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`
- evidence archive path: `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`
- parity scorecard link: `Documentation/zigux/phase15-parity-scorecard.md`
- indefinite-C policy link: `Documentation/zigux/phase15-indefinite-c-policy.md`

## Blocker Evidence

- latest blocker disposition: `blocked_no_bounded_scheduler_seam`
- benchmark-notes status: `pending_until_bounded_scheduler_seam_exists`
- replay command: `zig build test --build-file zigux/tests/phase15_build.zig`
- rollback threshold: reopen and return the anchor to an explicitly blocked review state immediately if the evidence packet becomes stale or contradictory, if ownership or validation changes, or if any proposed scheduler seam is still wider than the approved freeze boundary
- automatic return-to-blocked trigger: any attempted status-change claim without fresh Architecture Council reopen evidence, current blocker refresh, and replay-backed validation

## Retained Stay-In-C Closeout

- retained discussion state: `retired_from_active_discussion`
- reopen triggers:
  - `narrower_followup_answers_blocker`
  - `evidence_packet_stale_or_contradictory`
  - `ownership_or_validation_changed`
- written rationale: the current product plan still has no bounded scheduler seam that is narrow enough to justify a direct Zigux status-change claim, so the C implementation remains the product source of truth for this plan horizon

## Explicit Non-Goals

- no `kernel/sched/core.zig` starter
- no direct scheduler ownership claim for Zigux
- no silent freeze-map status change
- no implied Architecture Council approval beyond the blocked maintenance posture already recorded on current `master`
