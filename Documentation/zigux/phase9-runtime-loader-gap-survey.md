# Phase 9 Runtime Loader Gap Survey

## Status

- `PHASE9_STATUS=shared-reminder-packet-aligned`
- `PHASE9_SLICE=runtime-loader-gap-survey`
- `PHASE9_LANE_KEY=P9-L18`

## Current Repo Reality

Current `master` ships the shared loader-facing packet directly:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`
- `zigux/tests/phase9_build.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
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
- `zigux/tests/runtime_trace_events_loader_substrate_drift.zig` keeps the
  prepared shared runtime-substrate drift rejection explicit for the
  trace-events pilot family, so the cleared sample-local parity proof stays
  reviewable beside the shared loader packet

## Boundaries

The shared loader packet is still a review-only handoff surface, not a shipped
publication or registration-control surface.

- metadata-only `registrationSnapshot`, `tracepoint_probe_register`, and
  `tracepoint_probe_unregister` cues are review evidence, not shared runtime
  registration APIs
- `.modinfo`
- `MODULE_ALIAS()`
- `modules.alias`
- `modules.order`
- `modules.builtin`
- `Module.symvers`
- module install-root state
- `depmod` script, manifest, or alias publication state

Those publication and registration-summary surfaces remain blocked boundaries
rather than landed Phase 9 runtime-module delivery evidence.

Keep the older Phase 8 command and environment cue owners out of this packet:

- `tools/lib/subcmd/exec-cmd.zig`
- `tools/lib/subcmd/help.zig`

Keep the earlier-phase config-surface and symbol-export owners out of this
packet too:

- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `rust/exports.c`
- `zigux/kernel/export_shim.zig`

Those surfaces remain Phase 2 config-surface bridge references and Phase 3
symbol-export boundary references rather than Phase 9 runtime evidence.

Fresh repo-first inspection now also shows `zigux/kernel/runtime_loader_contract.zig`
keeps `register_api`, `unregister_api`, `summary`, `registration_snapshot`,
`module_symvers_path`, and `depmod_aliases` outside the shared `LoadPlan`, so
this note should treat that blocked registration-summary and publication
boundary as already-landed review-only contract evidence instead of as future
runtime command or environment follow-through.

## Current Shared Reminder State

Fresh repo-first inspection now shows `Documentation/zigux/README.md` and
`scripts/zigux/README.md` both keep
`Documentation/zigux/phase9-runtime-loader-gap-survey.md`,
`zigux/tests/runtime_loader_gap_manifest.json`, and
`zigux/tests/runtime_loader_gap_survey.zig` explicit beside
`zigux/tests/runtime_loader_allocator_init_flow.zig`,
`zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`,
the shared `zigux/tests/phase9_build.zig` replay, and the focused
`make -C zigux phase9-runtime-loader-shared-tests` route, while still deferring
the exact shared owner map and blocked publication boundary back to
`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`.

Fresh repo-first inspection now also shows `zigux/tests/README.md` keeps that
same shared Phase 9 loader-gap packet explicit through a dedicated Phase 9 flow
section that names `Documentation/zigux/phase9-runtime-loader-gap-survey.md`,
`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`,
`scripts/zigux/check-phase9-build-only-surface.py`,
`zigux/tests/runtime_loader_gap_manifest.json`,
`zigux/tests/runtime_loader_gap_survey.zig`,
`zigux/tests/runtime_loader_allocator_init_flow.zig`,
`zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`,
and the focused `make -C zigux phase9-runtime-loader-shared-tests`,
`make -C zigux phase9-test`, and `make -C zigux phase9` replay routes instead
of leaving that packet blurred into the tail of the Phase 8 flow.

Fresh repo-first inspection now also shows
`Documentation/zigux/review-checklist.md` keeps the no-dedicated-validator
posture, the blocked module-metadata and depmod-publication boundary, the older
Phase 8 command and environment cue owners, and the older Phase 2 Kconfig plus
Phase 3 export non-owner boundaries explicit. The dedicated
`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` checker now
fail-closes that cross-phase non-owner reminder directly, and
`zigux/tests/runtime_loader_gap_manifest.json` now records
`review_checklist_cross_phase_non_owner_boundary_present: true` instead of
leaving that reviewer-facing follow-through open.

Fresh repo-first inspection now also shows
`zigux/tests/runtime_loader_gap_manifest.json` no longer records any remaining
sample-local parity gap for trace-events and instead points at
`zigux/tests/runtime_trace_events_loader_substrate_drift.zig` as the cleared
replay surface, so this note should keep that landed proof visible as shipped
shared-loader evidence rather than treating trace-events loader drift as open
family-local follow-through.

That means the earlier docs-root undercount, the later tests-root undercount,
and the checklist-local cross-phase non-owner reminder are all cleared on
current `master`. The remaining same-lane job is just keeping the shared
reviewer-facing packet truthful when one of those already-landed reminder or
boundary surfaces moves again.

## Next Bounded Step

Leave this note parked unless `Documentation/zigux/review-checklist.md`,
`Documentation/zigux/README.md`, `scripts/zigux/README.md`,
`zigux/tests/README.md`,
`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, or
`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` drifts again
around the shared loader-gap packet, the landed
`zigux/tests/runtime_trace_events_loader_substrate_drift.zig` proof, the older
Phase 2 Kconfig and Phase 3 export non-owner boundaries, or the blocked
module-metadata and depmod-publication boundary.

If this packet reopens, start by rereading the shared survey note,
`zigux/tests/runtime_loader_gap_manifest.json`,
`Documentation/zigux/review-checklist.md`, and
`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` together on a
fresh readback, then repair the smallest reminder surface that actually drifted
while keeping the exact owner map and blocked publication boundary deferred back
to `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`.
