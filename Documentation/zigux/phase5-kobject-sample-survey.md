# Phase 5 Kobject Sample Survey

This note tracks the bounded Phase 5 reviewability survey for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_LANE_KEY=P5-L23`
- scope: keep the kobject sample note truthful against the current public repo tree, the shared Phase 5 build route, and the directly readable sample-backed validation packet
- current directly readable kobject packet on `master`:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
  - `zigux/tests/phase5_kobject_example_survey.zig`

## Why this note exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and still names `samples/kobject/kobject-example.c` as one of the approved Linux anchors.

Fresh repo-first inspection for this lane hit a readback split: the GitHub contents API stayed flaky on a few kobject paths, but public raw readback for current `master` confirmed that the sample-root module and the dedicated survey replay are both directly readable again. The truthful same-lane job is to record that restored packet clearly and keep the next step bounded to review-surface accuracy rather than reopen sample behavior.

## Current repo reality on `master`

Fresh repo-first inspection for this lane found these kobject-adjacent surfaces directly readable today:

- `samples/zigux/kobject_example.zig` exists and restores the public sample-root half of the kobject packet beside the shared Phase 5 sample family.
- `zigux/tests/phase5_build.zig` exists and keeps the kobject replay wired through the shared four-anchor Phase 5 build route.
- `zigux/tests/phase5_kobject_example.zig` exists and keeps a focused Phase 5 replay surface for descriptor, anchor replay, pre-registration boundary, registered boundary, shared `baz` and `bar` dispatch plus parse-failure visibility, initialized-only exit, ownership replay, teardown replay, and public parse-failure behavior.
- `zigux/tests/phase5_kobject_example_manifest.json` exists and still records the ownership-and-lifetime prompts, exact checks, and non-goals for the kobject anchor.
- `zigux/tests/phase5_kobject_example_survey.zig` exists and restores the dedicated survey replay path for the same bounded kobject packet.

Those directly readable paths mean the current kobject packet is no longer limited to note-plus-tests truthfulness alone. Current `master` again exposes the sample module, the focused replay, the dedicated survey replay, the manifest, and the shared `phase5_build.zig` route together as one bounded non-runtime Phase 5 packet.

## What the focused validation surfaces still prove

The current directly readable kobject packet keeps these review cues explicit:

- the shared `zigux/tests/phase5_build.zig` route still exists, so the kobject packet remains part of the shipped four-anchor Phase 5 replay surface
- the sample and focused replay still expect the Linux anchor `samples/kobject/kobject-example.c`
- the focused test keeps `runPreRegistrationBoundaryReplay()` explicit for the initialized-but-not-registered zero-active-attributes plus show-or-store rejection boundary
- the focused test keeps `runRegisteredBoundaryReplay()` explicit for the already-registered duplicate-registration and replay-restart rejection packet plus the still-usable bounded foo roundtrip afterward
- the focused test keeps `runInputValidationReplay()` explicit for the shared `baz` and `bar` dispatch plus parse-failure visibility while the sample stays registered
- the focused test keeps `ownershipSummary()` plus `runOwnershipReplay()` explicit for the lifecycle packet
- the focused test keeps `runTeardownReplay()` explicit for the registered teardown reset plus post-`exit()` rejection packet
- the manifest still records the same non-goals around sysfs creation, `kernel_kobj` integration, uevents, and module registration
- the dedicated `zigux/tests/phase5_kobject_example_survey.zig` replay is directly readable again, so contributor guidance can point to a sample-backed survey path instead of treating it as a public-tree gap

## Recorded gap vs roadmap

The earlier missing-path framing is no longer the honest gap:

- the roadmap still calls for a reviewable Phase 5 kobject reference-pattern anchor
- current `master` now exposes the sample module path, the focused test, the manifest, the dedicated survey replay, and the shared `zigux/tests/phase5_build.zig` route for that anchor
- the remaining same-lane risk is now shared review-surface drift, not the absence of the core kobject sample packet itself

That means the next same-lane step should stay inside one of these bounded repairs:

- refresh any shared Phase 5 guide, README, or checklist surface that still understates the restored kobject packet
- or leave the lane parked if current shared reminder surfaces already match this directly readable packet closely enough

## Non-goals

This note still does not claim:

- sysfs file creation parity
- `kernel_kobj` integration
- uevent delivery
- loadable module registration

## Next bounded step

Keep this lane parked unless fresh repo inspection shows a shared Phase 5 reminder surface still describing `samples/zigux/kobject_example.zig` or `zigux/tests/phase5_kobject_example_survey.zig` as missing. If that happens, reopen only for the next smallest shared guide, README, or checklist sync and keep the work tied to the directly readable non-runtime kobject packet rather than widening into new sample behavior.
