# Phase 5 Kobject Sample Survey

This note tracks the bounded Phase 5 reviewability survey for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=parked-doc-accuracy`
- `PHASE5_LANE_KEY=P5-L23`
- scope: keep the kobject sample note truthful against the current public repo tree and the still-present focused validation surfaces
- current directly readable kobject packet on `master`:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
- current public-tree gaps:
  - `samples/zigux/kobject_example.zig` is not present in the current `samples/zigux/` tree readback
  - `zigux/tests/phase5_kobject_example_survey.zig` is not present in the current `zigux/tests/` tree readback

## Why this note exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and still names `samples/kobject/kobject-example.c` as one of the approved Linux anchors.

Current repo reality is narrower than several shared reminders imply. The public tree does not currently expose a shipped `samples/zigux/kobject_example.zig` module or a dedicated `zigux/tests/phase5_kobject_example_survey.zig` replay, so this note should not describe those paths as already landed. The truthful same-lane job is to record what the repo actually ships today and leave the next step bounded.

## Current repo reality on `master`

Fresh repo-first inspection for this lane found these kobject-adjacent surfaces directly readable today:

- `zigux/tests/phase5_kobject_example.zig` exists and keeps a focused Phase 5 replay surface for descriptor, anchor replay, pre-registration boundary, registered boundary, shared `baz` and `bar` dispatch plus parse-failure visibility, initialized-only exit, ownership replay, teardown replay, and public parse-failure behavior.
- `zigux/tests/phase5_kobject_example_manifest.json` exists and still records the ownership-and-lifetime prompts, exact checks, and non-goals for the kobject anchor.
- `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still talk about a broader landed kobject packet than the public tree currently exposes.

The same inspection also found two important absences that this note should keep explicit instead of papering over:

- `samples/zigux/kobject_example.zig` is not visible in the current `samples/zigux/` directory tree.
- `zigux/tests/phase5_kobject_example_survey.zig` is not visible in the current `zigux/tests/` directory tree.

## What the focused validation surfaces still prove

Even without the sample module currently visible in the public tree, the remaining kobject-focused validation surfaces still make the intended review packet legible:

- the focused test expects the Linux anchor `samples/kobject/kobject-example.c`
- the focused test keeps `runPreRegistrationBoundaryReplay()` explicit for the initialized-but-not-registered zero-active-attributes plus show-or-store rejection boundary
- the focused test keeps `runRegisteredBoundaryReplay()` explicit for the already-registered duplicate-registration and replay-restart rejection packet plus the still-usable bounded foo roundtrip afterward
- the focused test keeps `runInputValidationReplay()` explicit for the shared `baz` and `bar` dispatch plus parse-failure visibility while the sample stays registered
- the focused test keeps `ownershipSummary()` plus `runOwnershipReplay()` explicit for the lifecycle packet
- the focused test keeps `runTeardownReplay()` explicit for the registered teardown reset plus post-`exit()` rejection packet
- the manifest still records the same non-goals around sysfs creation, `kernel_kobj` integration, uevents, and module registration

Those surfaces are useful as review evidence, but they are not the same as a publicly readable landed `samples/zigux/kobject_example.zig` reference sample.

## Recorded gap vs roadmap

The precise gap is now narrower and more honest than the older note claimed:

- the roadmap still calls for a reviewable Phase 5 kobject reference-pattern anchor
- current `master` still carries focused test and manifest evidence for that anchor
- current `master` does not currently expose the sample module path and dedicated survey replay path that several shared Phase 5 reminder surfaces describe as already landed

That means the next same-lane step should stay inside one of these bounded repairs:

- restore the missing `samples/zigux/kobject_example.zig` and `zigux/tests/phase5_kobject_example_survey.zig` files if they are meant to be part of the shipped Phase 5 packet
- or narrow the remaining shared Phase 5 docs so they stop claiming those two paths are already present on current `master`

## Non-goals

This note still does not claim:

- sysfs file creation parity
- `kernel_kobj` integration
- uevent delivery
- loadable module registration

## Next bounded step

Keep this lane parked unless a follow-up run is specifically restoring the missing kobject sample files or tightening another directly coupled shared reminder surface. If the repo stays in its current state, prefer the next smallest doc-accuracy repair over widening into new sample semantics or runtime-substrate claims.
