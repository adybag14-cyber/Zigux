# Phase 5 Kobject Sample Survey

This note tracks the bounded Phase 5 reviewability survey for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=parked-doc-accuracy`
- `PHASE5_LANE_KEY=P5-Y04`
- scope: keep the kobject sample note truthful against the current repo readback and keep the next bounded step inside the kobject packet only
- current directly readable kobject packet on `master`:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`

## Why this note exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and still names `samples/kobject/kobject-example.c` as one of the approved Linux anchors.

The bounded job for this note is not to reopen sample behavior. It is to say exactly what the current repo inspection could read back today and to stop treating older restored-packet wording as live evidence when the same paths are not directly readable through the main repo read path anymore.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-13 found these kobject-adjacent surfaces directly readable through the GitHub connector:

- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_kobject_example_manifest.json`

The same inspection hit direct-readback gaps for these kobject packet paths on current `master`:

- `samples/zigux/kobject_example.zig`
- `zigux/tests/phase5_build.zig`
- `zigux/tests/phase5_kobject_example_survey.zig`

That means this note should not currently present the full restored sample-root-plus-shared-build packet as directly readable shipped evidence. The honest same-lane posture is narrower: the focused test and manifest are still directly readable, while the sample-root module, shared Phase 5 build file, and dedicated survey replay were not directly readable through the main connector path during this run.

## What the directly readable validation surfaces still prove

Even with that narrower readback, the current directly readable kobject packet still keeps the bounded sample contract reviewable:

- `zigux/tests/phase5_kobject_example.zig` still keeps the descriptor contract explicit for the `samples/kobject/kobject-example.c` anchor and keeps the slice non-runtime
- the focused test still keeps `runPreRegistrationBoundaryReplay()` explicit for the initialized-but-not-registered zero-active-attributes plus show-or-store rejection boundary
- the focused test still keeps `runRegisteredBoundaryReplay()` explicit for the already-registered duplicate-registration and replay-restart rejection packet plus the still-usable bounded foo roundtrip afterward
- the focused test still keeps `runInputValidationReplay()` explicit for the shared `baz` and `bar` dispatch plus parse-failure visibility while the sample stays registered
- the focused test still keeps `ownershipSummary()` plus `runOwnershipReplay()` explicit for the lifecycle packet
- the focused test still keeps `runTeardownReplay()` explicit for the registered teardown reset plus post-`exit()` rejection packet
- `zigux/tests/phase5_kobject_example_manifest.json` still records the same ownership-and-lifetime prompts, exact checks, and non-goals around sysfs creation, `kernel_kobj` integration, uevents, and module registration

## Recorded gap vs roadmap

The roadmap still calls for a reviewable Phase 5 kobject reference-pattern anchor, but the current same-lane issue is readback truthfulness rather than missing new behavior:

- shared Phase 5 reminder surfaces still talk about the kobject anchor
- the focused kobject test and manifest are still directly readable
- the sample-root module, shared `phase5_build.zig` route, and dedicated survey replay were not directly readable through the main connector path in this run

So the honest gap is not "restore the kobject packet." The honest gap is "keep the note and shared guidance from overstating which parts of that packet are directly readable today."

## Sample-local next-step boundary

Fresh same-packet inspection shows the remaining truthful follow-through is now sample-local, not shared-guide work:

- this survey packet should carry the kobject lane for this packet, not the unrelated trace-events label `P5-L23`
- `zigux/tests/phase5_kobject_example_manifest.json` still records `surveyed_commit` as `28a3bde2b3d68612f18d9bdd786be50c71c3173e`, which anchors the older restored-packet survey state instead of this narrower readback-truthfulness posture
- because the sample-root module, shared `phase5_build.zig` route, and dedicated survey replay were still not directly readable through the same connector path in this run, widening into shared Phase 5 guide or README edits would leave this sample-only lane and risk overlapping broader reminder work

That leaves the next same-sample step smaller than any shared-guide edit: if the readback state stays the same, the next honest follow-through is one manifest-only `surveyed_commit` refresh so the kobject packet agrees on which survey state is current before any broader shared reminder surface moves.

## Non-goals

This note still does not claim:

- sysfs file creation parity
- `kernel_kobj` integration
- uevent delivery
- loadable module registration

## Next bounded step

Keep this lane parked unless a follow-up run can directly read back `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_build.zig`, and `zigux/tests/phase5_kobject_example_survey.zig` through the same repo path used for the rest of this packet, or publish the one sample-local manifest sync described above. If the readback state stays the same, prefer that manifest-only `surveyed_commit` sync before reopening shared guide, checklist, or README wording.
