# Phase 5 Kobject Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kobject/kobject-example.c` anchor.

The sample-backed survey note keeps `samples/zigux/README.md`, `zigux/tests/phase5_kobject_example_manifest.json`, `zigux/tests/phase5_kobject_example_survey.zig`, the shared `phase5_build.zig` packet, and the focused `phase5_kobject_only_build.zig` replay in one reviewable place.

## Status

- `PHASE5_STATUS=active`
- `PHASE5_SLICE=kobject-reference-sample-starter`
- `PHASE5_LANE_KEY=P5-L09`
- `PHASE5_SURVEYED_COMMIT=0f512415f8c7d0c844861139648eacb96d727a56`
- scope: roadmap-vs-repo sample delivery, approved ownership-and-lifetime guidance, and exact bounded checks for the landed `samples/zigux/` kobject-style replay

## Latest verification snapshot

Current sample behavior was re-verified against `master` commit `0f512415f8c7d0c844861139648eacb96d727a56` on 2026-04-30 with the attached Zig toolchain.

- `zig test samples/zigux/kobject_example.zig`
- observed result: `1/2 kobject_example.test.kobject sample replay keeps the anchor reviewable and non-runtime...OK`
- observed result: `2/2 kobject_example.test.kobject sample teardown keeps ownership boundaries explicit...OK`
- observed result: `All 2 tests passed.`
- `zig build test --build-file zigux/tests/phase5_kobject_only_build.zig --summary all`
- observed result: `Build Summary: 5/5 steps succeeded; 7/7 tests passed`
- observed result: `phase5-kobject-example-tests 5 pass (5 total)`
- observed result: `phase5-kobject-example-survey-tests 2 pass (2 total)`
- `zig test zigux/tests/phase5_kobject_example_survey.zig`
- observed result: `1/2 phase5_kobject_example_survey.test.phase 5 kobject manifest records the exact bounded checks...OK`
- observed result: `2/2 phase5_kobject_example_survey.test.phase 5 kobject contributor docs stay aligned with the shipped review surface...OK`
- observed result: `All 2 tests passed.`

The shared sample-root catalog in `samples/zigux/README.md` plus the shared prompts in `Documentation/zigux/review-checklist.md` remain part of the shipped review surface, while the focused replay for this exact packet now lives at `zigux/tests/phase5_kobject_only_build.zig` instead of relying on a full shared Phase 5 bundle rerun.

## Contributor guidance

- keep the unnamed attribute group shape explicit in the note and the coupled survey packet
- keep the shared `0664` attribute mode pattern explicit beside the Linux `foo` or `baz` or `bar` ordering cues
- keep the static directory-name cue explicit, keep no uevent delivery explicit, and keep dynamic kobjects out of scope for this sample
- keep the initialized-but-not-registered stage explicit: the initialized-but-not-registered stage keeps the active attribute count at `0` until `registerAttributes()` claims ownership
- keep the initialized-only abandonment path explicit: the initialized-only `exit()` path returns an `abandoned_before_registration` teardown summary
- keep the terminal lifetime boundary explicit: post-`exit()` `init()`, `registerAttributes()`, `showValue()`, and `storeValue()` calls all remain rejected
