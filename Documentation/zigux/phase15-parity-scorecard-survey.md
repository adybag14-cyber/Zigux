# Phase 15 Parity Scorecard Gap Survey

This document records the bounded Phase 15 governance lane around the parity-scorecard gap named in the roadmap.

## Status

- `PHASE15_LANE_KEY=P15-L09`
- `PHASE15_STATUS=parity_scorecard_gap_survey`
- `PHASE15_SLICE=parity-tracking-gap-vs-roadmap`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- scope: one survey-grade note that compares the current `master` Phase 15 governance packet against the roadmap's required parity-scorecard surface without claiming a landed scorecard, dedicated manifest, or dedicated Zig replay that is not present on the live head
- survey provenance refreshed against dated current-master readback marker `current-master-readback-2026-05-11` on 2026-05-11
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/phase15-governance-lane-sequencing.md`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `Documentation/zigux/phase15-parity-scorecard-survey.md`

## Why this survey exists

The roadmap's Phase 15 requirements name four governance features for the frozen deep-core anchors:

- freeze map
- Architecture Council review process
- parity scorecard
- policy for code that remains in C indefinitely

Current `master` already carries the freeze map plus the surrounding review-process, handoff, readiness, and governance-lane notes. It does not currently carry a landed Phase 15 parity scorecard note, a dedicated parity-scorecard manifest, or a dedicated `zigux/tests/phase15_parity_scorecard.zig` replay on the live head.

That leaves a real parity-tracking gap between the roadmap and the current repo state. The repo has governance language about how a scorecard should behave, but the reviewable scorecard artifact itself is still missing from `master`.

## Current master readback

The dated 2026-05-11 readback shows:

- present on `master`:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-governance-lane-sequencing.md`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
- not present on `master` during this readback:
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `zigux/tests/phase15_parity_scorecard.zig`
  - `zigux/tests/phase15_parity_scorecard.json`
  - `zigux/tests/phase15_indefinite_c_policy.zig`
  - `zigux/tests/phase15_indefinite_c_policy.json`

This survey stays inside the parity-scorecard lane. It names the adjacent missing indefinite-C policy packet only because the review-process note currently treats both surfaces as already available evidence.

## Gap against the roadmap

The roadmap requirement is not just broad Phase 15 governance language. It explicitly calls for a parity scorecard so the frozen anchors can be tracked with bounded ownership, status, validation, and rollback posture.

Current `master` still lacks that direct parity-tracking record. As a result:

- the live repo cannot point reviewers at one scorecard note for the frozen anchors
- the review-process note overstates current parity-tracking maturity when it speaks as if a landed scorecard baseline already exists
- the current maintenance-mode packet is missing the one artifact that should summarize anchor-by-anchor blocked posture without reopening direct port work

## Honest current posture

The honest bounded Phase 15 statement on current `master` is:

- the freeze-in-C governance packet is partially landed
- the Architecture Council review-process note is present
- the parity-scorecard surface remains a roadmap-required gap
- no Architecture Council approval is recorded for any freeze-map status change
- every frozen anchor remains blocked from a direct Zigux port claim

## Recorded gaps

The current lane state is:

- landed `phase15-freeze-map-governance-note`
- landed `phase15-architecture-council-review-process-note`
- landed `phase15-governance-lane-sequencing-note`
- landed `phase15-handoff-next-steps-survey`
- landed `phase15-readiness-gate-survey`
- open `phase15-parity-scorecard-doc`
- open `phase15-parity-scorecard-manifest`
- open `phase15-parity-scorecard-zig-replay`
- open `phase15-parity-scorecard-review-surface-sync`

This keeps the lane narrow. The missing work is not a deep-core implementation step. It is the reviewable parity-tracking packet that the roadmap says must exist before any stronger Phase 15 status claims become credible.

## Non-goals

This survey does not claim:

- a landed parity scorecard on current `master`
- a landed indefinite-C policy packet on current `master`
- a dedicated Phase 15 parity-scorecard Zig test on current `master`
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- any new deep-core Zig bridge, wrapper, or direct port starter

## Next bounded step

Land the missing parity-scorecard packet itself as a bounded documentation-plus-test surface, then realign the existing review-process, docs-root, and validator-facing reminders so they stop speaking as if the missing scorecard and indefinite-C policy packets are already present on the live head.
