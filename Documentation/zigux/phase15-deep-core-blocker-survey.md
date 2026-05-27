# Phase 15 Deep-Core Blocker Survey

This note records the bounded Phase 15 survey of the roadmap-backed deep-core blockers against current repo reality on `master`.

## Status

- `PHASE15_STATUS=deep_core_blocker_survey_landed`
- `PHASE15_LANE_KEY=P15-L01`
- `PHASE15_SLICE=roadmap_vs_repo_reality_deep_core_blocker_crosswalk`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-27`
- role: keep one dedicated reviewable crosswalk for the four freeze-in-C anchors so the current blocker posture can be read directly against the roadmap, the freeze-map packet, the directly materialized shared build companion, and the adjacent Phase 14 evidence without implying a status change, a wrapper-route recovery, or deep-core port readiness

## Why this note exists

Phase 15 is a governance tranche. The roadmap says the repo must govern the final mixed-language steady state honestly through a freeze map, an Architecture Council review process, a parity scorecard, and an explicit stay-in-C policy for code that remains in C indefinitely.

Current `master` already carries those owner notes. It also carries the adjacent readiness, sequencing, handoff, and shared-summary gap packet that keeps reminder surfaces truthful while the broader dedicated wrapper routes and shared-CI route remain absent.

What was still missing as a standalone reviewable surface was the direct survey that answers one narrow question in one place: for each deep-core freeze-in-C anchor, what does the roadmap require, what current repo evidence exists, and what exact blocker still keeps the anchor in C?

This note closes that gap without widening the lane into implementation work.

## Roadmap basis

The roadmap keeps these four anchors in the active freeze-in-C set for the current product plan:

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

The same roadmap keeps these two neighboring deep-core areas as study-only boundary context rather than freeze-in-C scorecard rows:

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

The required Phase 15 governance features remain:

- freeze map
- Architecture Council review process
- parity scorecard
- policy for code that remains in C indefinitely

## Current repo reality packet

Current `master` directly materializes the owner packet that governs these anchors through:

- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_freeze_map_governance.zig`
- `zigux/tests/phase15_parity_scorecard.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- `zigux/tests/phase15_build.zig`

The same reread now shows the shared build companion as directly materialized while the broader wrapper and shared-CI surfaces remain current gaps:

- `zigux/tests/phase15_build.zig` is directly materialized on current `master` as the shared Phase 15 governance replay companion
- `zigux/Makefile` still lacks `phase15-validate`, `phase15-test`, and `phase15`
- `.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route
- no Architecture Council approval is currently recorded for a freeze-map status change

That means the honest posture is still blocker accounting and reminder-surface maintenance, not deep-core delivery.

## Deep-core blockers versus roadmap and repo reality

### `kernel/sched/core.c`

- roadmap basis: Phase 15 freeze-in-C anchor that must stay in C until a narrower scheduler seam exists and an Architecture Council review packet can name reviewable evidence
- current repo reality: the freeze map, freeze-map governance note, parity scorecard, review-process note, and stay-in-C policy are all landed; the validator-first maintenance gate and shared build companion are directly readable; the broader wrapper and shared-CI routes still remain absent
- current blocker: `blocked_no_bounded_scheduler_seam`
- next honest posture: keep the anchor frozen until a bounded scheduler seam exists and a reopen trigger can be recorded without widening beyond the freeze boundary

### `mm/page_alloc.c`

- roadmap basis: Phase 15 freeze-in-C anchor that must stay in C until a narrower allocator seam exists and an Architecture Council review packet can name reviewable evidence
- current repo reality: the same landed Phase 15 owner packet exists for allocator governance; the validator-first maintenance gate and shared build companion are directly readable; and the broader wrapper and shared-CI routes still remain absent on current `master`
- current blocker: `blocked_no_bounded_allocator_seam`
- next honest posture: keep the anchor frozen until a bounded allocator seam exists and a reopen trigger can be recorded without widening beyond the freeze boundary

### `kernel/rcu/tree.c`

- roadmap basis: Phase 15 freeze-in-C anchor that may only reopen if a narrower-than-freeze follow-up exists and the Architecture Council can review bounded evidence instead of broad bridge intent
- current repo reality: `Documentation/zigux/phase14-rcu-tree-survey.md` still records blocked `phase14-rcu-tree-bridge-blocker` and keeps Tree RCU in freeze-in-C posture; the Phase 15 owner packet, validator-first maintenance gate, and shared build companion are landed; but the broader wrapper and shared-CI routes still remain absent
- current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- next honest posture: keep the anchor frozen until a narrower-than-freeze RCU seam exists and the blocker evidence changes inside the owner packet

### `net/core/skbuff.c`

- roadmap basis: Phase 15 freeze-in-C anchor that may only reopen if a narrower-than-lifetime follow-up exists and the Architecture Council can review bounded evidence instead of broad bridge intent
- current repo reality: `Documentation/zigux/phase14-skbuff-bridge-survey.md` still records live blocker `phase14-skbuff-live-ownership-blocker`, while `Documentation/zigux/phase14-core-boundary-traceability.md` still keeps skbuff in retained-in-C posture; the Phase 15 owner packet, validator-first maintenance gate, and shared build companion are landed; but the broader wrapper and shared-CI routes still remain absent
- current blocker: `blocked_packet_lifetime_boundary_still_too_wide`
- next honest posture: keep the anchor frozen until a narrower-than-lifetime skbuff seam exists and the blocker evidence changes inside the owner packet

## Study-only boundary context

`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain relevant to deep-core governance, but they stay outside the blocked status-change scorecard tracked here. Keep them routed through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` until the freeze map itself changes.

## Maintenance handoff

- current lane posture: `maintenance_mode`
- replay before trusting this survey:
  - `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
  - `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-tests-readme-alignment.py`
  - `python3 scripts/zigux/check-phase15-review-process-handoff.py`
  - `python3 scripts/zigux/check-phase15-handoff-note-alignment.py`
  - `python3 scripts/zigux/check-phase15-shared-summary-gap.py`
  - `python3 scripts/zigux/check-phase15-readiness-gate-packet.py`
  - `python3 scripts/zigux/validate-phase15.py`
  - `zig test zigux/tests/phase15_freeze_map_governance.zig`
  - `zig test zigux/tests/phase15_parity_scorecard.zig`
  - `zig build test --build-file zigux/tests/phase15_build.zig`
- reopen only when one of these packet-local conditions becomes true:
  - a freeze-in-C anchor changes blocker disposition, owner, approver set, or evidence path
  - the roadmap changes the active freeze-in-C anchor set
  - the broader wrapper routes or shared-CI Phase 15 route return on current `master`
  - a shared reminder surface drifts far enough that this dedicated crosswalk no longer matches the owner packet

## Non-goals

This note does not claim:

- an Architecture Council approval for any freeze-map status change
- a direct Zig bridge or dual implementation for any deep-core freeze-in-C anchor
- that the broader wrapper routes or shared-CI Phase 15 route are already landed on current `master`

## Next bounded step

Keep this survey parked unless one anchor's blocker evidence changes, the roadmap changes the freeze-in-C set, the missing broader wrapper routes or shared-CI Phase 15 route return, or the surrounding Phase 15 reminder packet drifts enough that this dedicated blocker crosswalk stops matching the owner notes.
