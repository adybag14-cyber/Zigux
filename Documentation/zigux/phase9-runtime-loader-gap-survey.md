# Phase 9 Runtime Loader Gap Survey

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-loader-gap-survey`
- `PHASE9_LANE_KEY=P9-L18`

## Current Repo Reality

Current `master` ships the shared loader-facing packet directly:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/phase9_build.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`

The current honest shared replay routes are literal on `master`:

1. `make -C zigux phase9-runtime-loader-shared-tests`
2. `make -C zigux phase9-test`
3. `make -C zigux phase9`

There is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`,
or `phase9-validate` route on current `master`.

## What Is Reviewable Now

- the shared request lifecycle remains explicit through `prepared`,
  `waiting_on_runtime_substrate`, and `released_without_substrate`
- `zigux/tests/runtime_loader_allocator_init_flow.zig` keeps the shared allocator
  and init-flow proof bundle explicit for the four shipped pilot families
- `samples/zigux/runtime_trace_events_loader.zig` keeps
  `registrationSnapshot`, `prepareSharedRequest`,
  `requestSharedRuntimeLoad`, and `releaseSharedWithoutSubstrate`
  reviewable as metadata-only loader handoff evidence

## Boundaries

The shared loader packet is still a review-only handoff surface, not a shipped
publication surface.

- `.modinfo`
- `MODULE_ALIAS()`
- `modules.alias`
- `modules.order`
- `modules.builtin`
- module install-root state
- `depmod` script or manifest state

Those publication surfaces remain blocked boundaries rather than landed Phase 9
runtime-module delivery evidence.

Keep the older Phase 8 command and environment cue owners out of this packet:

- `tools/lib/subcmd/exec-cmd.zig`
- `tools/lib/subcmd/help.zig`

## Next Bounded Step

If the shared loader packet drifts again, tighten only this packet's survey
evidence, gating, or rollback wording. Keep the exact shared owner map in
`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, and treat
`Documentation/zigux/review-checklist.md` as the next reviewer-facing reminder
surface for the still-blocked `.modinfo`, `MODULE_ALIAS()`, `modules.alias`,
`modules.order`, `modules.builtin`, module install-root state, and `depmod`
script or manifest state boundary. Keep pilot-family lifecycle claims and
module-publication work in their owning lanes until real publication surfaces
land.
