# Phase 15 Readiness Route Exactness Gap

This note records one bounded Architecture Council governance truthfulness gap in
the parked Phase 15 packet: older readiness-route exactness wording still talks
as if the shared `phase15-validate` route is directly materialized and split
across route, validator, and manifest packets, but current `master` has already
moved to a blocked-route readiness posture.

## Scope

- lane: `arch-council`
- phase: `Phase 15`
- target family: review boundaries, freeze-map compliance, and architecture
  decisions
- bounded subject: keep the parked Phase 15 readiness-route note aligned with
  the current blocked-route governance packet

## Current repo reality

Current dated `master` readback for this gap now shows a different bounded
packet than the older validator-route story:

- `Documentation/zigux/phase15-readiness-gate-survey.md` already treats
  `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and
  `make -C zigux phase15` as blocked route vocabulary rather than directly
  readable shipped replay paths.
- `zigux/Makefile` and `scripts\zigux/validate_phase15.zig` still return missing
  on direct current-`master` reads, so there is no directly materialized shared
  `phase15-validate` route packet to compare against a validator-side route
  inventory.
- `zigux/tests/phase15_readiness_gate_manifest.json` now carries the
  four-checker inventory:
  - `scripts\zigux/check_phase15_docs_readme_alignment.zig`
  - `scripts\zigux/check_phase15_scripts_readme_alignment.zig`
  - `scripts\zigux/check_phase15_review_process_handoff.zig`
  - `scripts\zigux/check_phase15_shared_summary_gap.zig`

That means the older three-packet route-mismatch story is no longer the honest
current gap. The real bounded task is to keep this note from restating a retired
validator-route mismatch after the broader readiness packet moved to blocked
route vocabulary.

## Why this belongs in Architecture Council lane work

This is not a helper-port or driver-delivery task.

It protects review boundaries and freeze-map-adjacent reminder surfaces from
quietly inheriting an outdated route story. If this note keeps implying a live
shared validator route after the current governance packet has parked that route
as blocked vocabulary, later Architecture Council rereads can make approval or
replay assumptions that the current tree no longer supports.

## Machine-checkable guard

`scripts\zigux/check_phase15_readiness_route_exactness.zig` keeps this parked
blocked-route posture explicit and fail-closed.

The checker currently passes only when repo reality still matches the bounded
truthfulness state described here:

- current `master` no longer materializes the shared `phase15-validate` route
  packet directly
- `zigux/Makefile` and `scripts\zigux/validate_phase15.zig` still return missing
  on direct current-`master` reads
- `zigux/tests/phase15_readiness_gate_manifest.json` now carries the
  four-checker inventory
- `Documentation/zigux/phase15-readiness-gate-survey.md` already treats
  `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and
  `make -C zigux phase15` as blocked route vocabulary rather than a directly
  replayable shipped route

If any of those facts move, the checker fails so this note can be tightened,
retired, or replaced instead of silently drifting.

## Non-goals

This note does not claim:

- any Architecture Council approval for a freeze-map status change
- a change to the freeze-in-C or study-only anchor sets
- that `zigux/Makefile` or `scripts\zigux/validate_phase15.zig` have been
  rematerialized on current `master`
- a repair to the broader missing Phase 15 build, validator, or lane-owner
  companion packet

## Replay

- `zig run scripts/zigux/check_phase15_readiness_route_exactness.zig -- --self-test`
- `zig run scripts/zigux/check_phase15_readiness_route_exactness.zig`

## Next bounded step

Keep this note parked until one of two things happens:

- direct current-`master` reads recover `zigux/Makefile` plus
  `scripts\zigux/validate_phase15.zig`, which would justify replacing this
  blocked-route posture with a smaller live route exactness reread
- one of the broad reminder surfaces drifts away from the blocked-route
  readiness posture already recorded by
  `Documentation/zigux/phase15-readiness-gate-survey.md`
