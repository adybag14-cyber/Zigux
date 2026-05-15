# Phase 7 Roadmap Integration Survey

This note records the shared Phase 7 bootstrap-glue packet that keeps the roadmap-backed runtime helper tranche tied to the current validation substrate.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=roadmap-integration-shared-control-surface`
- `PHASE7_LANE_KEY=P7-L01`
- scope: shared roadmap-to-validation-substrate integration only

## Roadmap Anchor

Phase 7 in the product roadmap moves the first reusable in-kernel leaf helpers into the Zigux product path through these anchors:

- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`

The roadmap also says the shared packet must keep these requirements explicit:

- runtime-safe leaf helpers
- stronger ownership and pointer discipline
- integration with validation substrate

## Current Shared Packet

Current `master` already keeps the helper family tied into one shared control surface through:

- `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
- `scripts/zigux/validate-phase7.py`
- `scripts/zigux/check-phase7-build-wiring.py`
- `zigux/tests/phase7_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

That packet is the current reviewable proof that the four helper-local slices are still routed through the same shared Phase 7 replay surface instead of drifting into ad hoc reminders.

## Survey Result

The remaining lane-local gap versus the roadmap was not a missing helper-local implementation. It was that the shared bootstrap packet did not yet have one dedicated survey note and checker focused on roadmap-required validation-substrate integration.

This survey closes that gap by making the shared packet explicit and by pairing it with:

- `scripts/zigux/check-phase7-roadmap-integration.py --self-test`
- `scripts/zigux/check-phase7-roadmap-integration.py`
- `make -C zigux phase7-validate`
- `make -C zigux phase7-test`

This survey does not claim the whole shared Phase 7 helper bundle is green on current `master`. It only records that the roadmap-backed shared integration packet is present, reviewable, and now has a dedicated survey surface.

## Next Bounded Step

Keep future follow-through inside this shared control surface only when the roadmap-backed integration packet drifts.

- fix the survey note if the roadmap-facing wording falls out of sync with the shared packet
- fix the checker if the dedicated shared packet changes shape
- route helper-local parity or semantics changes back to the helper-owned Phase 7 lanes instead of reopening them here
