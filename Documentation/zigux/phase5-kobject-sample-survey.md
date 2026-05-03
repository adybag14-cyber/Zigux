# Phase 5 Kobject Sample Survey

- `PHASE5_STATUS=parked`
- `PHASE5_SLICE=kobject-reference-sample-starter`
- `PHASE5_LANE_KEY=P5-L12`
- `PHASE5_SURVEYED_COMMIT=affdebd460c9c33ce939c7535cdb929352648e93`
- scope: roadmap-vs-repo sample reviewability, approved ownership-and-lifetime guidance, and exact bounded checks for the landed `samples/zigux/` kobject-style replay
- product boundary:
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
  - `zigux/tests/phase5_kobject_example_survey.zig`

This sample-backed survey note keeps the top-level docs-root guide in `Documentation/zigux/README.md`, the shared sample-root catalog in `samples/zigux/README.md`, the shared tests-root guide in `zigux/tests/README.md`, and the shared review checklist aligned with the shipped review surface.

The landed sample remains an approved Phase 5 ownership-and-lifetime idiom. `ownershipSummary()` now keeps replay readiness reviewable alongside the cold, initialized, registered, and exited stages, so reviewers do not have to infer when `runAnchorReplay()` is valid from method guards alone. `runInitializedExitReplay()` now keeps the initialized-only abandonment path sample-owned too, so the direct sample packet no longer leaves that exit summary as a one-off assertion trail.

The note still points back to the direct `zig test samples/zigux/kobject_example.zig` replay, the focused shared-build replay in `zigux/tests/phase5_kobject_example.zig`, the paired `zig test zigux/tests/phase5_kobject_example_survey.zig` replay, and the shared `phase5_build.zig` entrypoint.

Exact reviewability cues remain explicit:

- `ownershipSummary()` keeps replay readiness plus the `cold`, `initialized`, `registered`, and `exited` stages directly reviewable
- the replay-readiness boundary only allows `runAnchorReplay()` in the initialized stage
- the pre-registration zero-active-attributes boundary, the sample-owned initialized-only abandonment replay, and the post-exit rejection boundaries remain explicit
- sysfs creation, `kernel_kobj` integration, uevents, and loadable module registration remain out of scope

Latest verification snapshot:

- `zig test samples/zigux/kobject_example.zig`
  - `All 5 tests passed.`
- `zig test zigux/tests/phase5_kobject_example_survey.zig`
  - `All 2 tests passed.`

The shared `zigux/tests/phase5_build.zig` entrypoint remains the umbrella review gate recorded in the manifest and contributor prompts, but this bounded verification pass did not rerun the whole Phase 5 sample bundle.

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/kobject_example.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `KobjectExampleSample.descriptor()` still name `samples/kobject/kobject-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- does `zigux/tests/phase5_kobject_example_manifest.json` still pin `surveyed_commit` to the exact inspected `master` head while this note carries the same `PHASE5_SURVEYED_COMMIT` marker instead of a floating branch label?
- do `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` still describe the exact directory-name, attribute-order, attribute-mode, registration-step, static-name-no-uevent boundary, pre-registration boundary, ownership-summary, initialized-exit teardown, foo roundtrip, shared `b` dispatch, parse-failure, and exit-boundary contract run through `zigux/tests/phase5_build.zig`?
- does `zigux/tests/phase5_kobject_example.zig` still stay wired through `zigux/tests/phase5_build.zig` via the `kobject_example_sample` import so the focused replay remains explicit even though it is not a standalone `zig test` entrypoint?
- do the sample-backed survey note, `samples/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md` still keep this landed Phase 5 kobject slice distinct from the later runtime starters while pointing reviewers back to the direct sample replay, the focused shared-build replay, the paired survey replay, and the shared `phase5_build.zig` entrypoint?
- does `ownershipSummary()` still keep replay readiness plus the `cold`, `initialized`, `registered`, and `exited` lifecycle summary explicit without forcing reviewers to infer it from guards alone?
- does the sample keep the pre-registration zero-active-attributes boundary, initialized-only abandonment path, registered teardown summary, and post-exit rejection boundaries explicit instead of leaving them to ad hoc test-body assembly?
- if the sample behavior changes, is the manifest updated alongside the replay and teardown contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that sysfs creation, `kernel_kobj` integration, uevents, and loadable module registration remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The current gap is no longer "Zigux has no kobject sample guidance." The more precise state is:

- the repo now has a reviewable Phase 5 `kobject_example` sample plus manifest-backed checks for directory naming, ordered attributes, shared `b` dispatch, parse failures, ownership summaries, initialized-only abandonment, and teardown
- this sample must remain visibly separate from later runtime-facing work so contributors do not over-claim runtime substrate coverage
- this approved ownership-and-lifetime idiom is pinned to `PHASE5_SURVEYED_COMMIT=affdebd460c9c33ce939c7535cdb929352648e93` so the survey note, manifest-backed checks, shared sample-root catalog, shared tests-root guide, shared review checklist, and focused shared-build replay all point at the same inspected `master` head
- the Phase 5 roadmap's four named sample anchors are now all represented by bounded `samples/zigux/` reference readings, but that does not widen this slice into runtime sysfs or module-delivery claims

## Next bounded step

Leave this kobject survey lane parked unless fresh repo inspection finds one more directly coupled contributor-guidance or exact-replay wording drift inside the landed `kobject_example` packet.
