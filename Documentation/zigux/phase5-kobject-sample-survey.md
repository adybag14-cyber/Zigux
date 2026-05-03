# Phase 5 Kobject Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=active`
- `PHASE5_SLICE=kobject-reference-sample-starter`
- `PHASE5_LANE_KEY=P5-L12`
- `PHASE5_SURVEYED_COMMIT=affdebd460c9c33ce939c7535cdb929352648e93`
- scope: roadmap-vs-repo sample reviewability, approved ownership-and-lifetime guidance, and exact bounded checks for the landed `samples/zigux/` kobject-style replay
- product boundary:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
  - `zigux/tests/phase5_kobject_example_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kobject/kobject-example.c` as one of the Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection still shows that current `master` carries all four roadmap-approved bounded Phase 5 reference samples under `samples/zigux/`, including the landed `kobject_example` slice. The kobject-specific job is no longer missing sample delivery; it is to keep this ownership-and-lifetime idiom, its exact checks, and its non-goals honest now that the broader Phase 5 anchor set is complete.

The current bounded gap was not new sysfs behavior. It was reviewability inside the shipped in-memory sample: lifecycle reviewers still had to infer cold, initialized, registered, and exited ownership state from internal fields and scattered assertions. This lane closes that gap by making `ownershipSummary()` part of the direct sample packet, so the same review surface now exposes stage, active attribute count, access state, lifecycle counters, and register-or-exit availability without widening into runtime substrate claims.

The shared sample-root catalog in `samples/zigux/README.md`, the top-level docs-root guide in `Documentation/zigux/README.md`, the shared prompts in `Documentation/zigux/review-checklist.md`, and the shared tests-root guide in `zigux/tests/README.md` remain part of that contributor-facing boundary, because they are the shortest places to keep the landed kobject idiom visibly separate from the later runtime starter families while pointing reviewers back to the direct `zig test samples/zigux/kobject_example.zig` replay, the paired `zig test zigux/tests/phase5_kobject_example_survey.zig` replay, and the exact shipped review packet.

## Survey findings

- `samples/kobject/kobject-example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a subsystem slice.
- the Linux sample mixes three concerns:
  - a named directory under `/sys/kernel/`
  - three integer-backed attributes, with `baz` and `bar` sharing the same show and store path and the attribute array ordered as `foo`, `baz`, `bar`
  - real sysfs and module-lifecycle substrate through `kobject_create_and_add`, `sysfs_create_group`, `kernel_kobj`, and module init or exit hooks
- the honest Phase 5 move remains to make the directory name, attribute dispatch, attribute-array order, the shared `0664` attribute mode pattern, and lifetime boundaries reviewable in memory while keeping sysfs creation, kernel object registration, and module wiring out of scope.
- the shipped sample now also exposes `ownershipSummary()` so that the cold, initialized, registered, and exited stages stay directly reviewable through one bounded sample-local summary instead of only through internal-field inspection.
- the top-level docs-root guide in `Documentation/zigux/README.md` is part of that same contributor packet now, because it keeps the landed kobject survey note indexed beside the shared sample-root catalog, shared tests-root guide, the direct sample replay, the paired survey replay, and the shared `phase5_build.zig` entrypoint.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/kobject_example.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `KobjectExampleSample.descriptor()`
- it models only the directory name, the unnamed attribute group shape, the Linux `foo`/`baz`/`bar` attribute-array order, the shared `0664` attribute mode pattern, integer roundtrips, and the shared `baz` or `bar` dispatch path in memory
- it keeps the static directory-name cue explicit, records no uevent delivery, and leaves dynamic kobjects out of scope for this sample
- it uses a tiny `init()` -> `registerAttributes()` -> `showValue()` or `storeValue()` -> `exit()` lifecycle so the initialized-but-not-registered ownership boundary, the initialized-only abandonment path, registered teardown, and the new `ownershipSummary()` snapshot all stay explicit
- it provides one bounded self-check through `runAnchorReplay()` instead of implying a runtime-ready sysfs or module implementation

The exact checks currently recorded in `zigux/tests/phase5_kobject_example_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the in-memory sample keeps the Linux directory name `kobject_example` and an unnamed attribute group
- the replay summary keeps the Linux attribute array order `foo`, `baz`, `bar` explicit
- the replay summary keeps the Linux `foo`, `baz`, and `bar` attribute mode pattern explicit as `0664` for all three attributes
- `runAnchorReplay()` requires `init()` first, claims attribute ownership through exactly one `register_runs` increment, registers exactly three attributes, and leaves the sample in the `registered` stage with attributes accessible
- the replay summary keeps the static directory name explicit, records no uevent delivery, and leaves dynamic kobjects out of scope for this sample
- the initialized-but-not-registered stage keeps the active attribute count at `0` and rejects show or store calls until `registerAttributes()` claims ownership
- `ownershipSummary()` reports the `cold`, `initialized`, `registered`, and `exited` stages directly, keeps active attribute counts at `0`, `0`, `3`, and `0`, and makes register-or-exit availability reviewable without reading internal fields
- the initialized-only `exit()` path returns an `abandoned_before_registration` teardown summary, keeps `register_runs` at `0`, and still leaves the sample exited with no active attributes
- storing `42` into `foo` renders back as `42\n`
- `baz` and `bar` share the same show and store path while still rendering `7\n` and `-5\n` through their own attribute names
- non-integer writes return `InvalidInteger`, and unknown attribute names remain explicit errors
- registered `exit()` returns a teardown summary, clears the tracked values, removes the active attribute count, and the post-`exit()` `init()`, `registerAttributes()`, `showValue()`, and `storeValue()` calls all remain rejected

## Latest verification snapshot

Current sample behavior was re-verified against the latest visible `master` head `affdebd460c9c33ce939c7535cdb929352648e93` on 2026-05-03 with the attached Zig toolchain.

The exact verification commands and observed results for this narrow verification pass were:

- `zig fmt --check samples/zigux/kobject_example.zig zigux/tests/phase5_kobject_example_survey.zig`
  - observed result: formatting already matched the edited files
- `zig test samples/zigux/kobject_example.zig`
  - observed result: `1/5 kobject_example.test.kobject sample replay keeps the anchor reviewable and non-runtime...OK`
  - observed result: `2/5 kobject_example.test.kobject sample keeps shared dispatch and parse failures explicit...OK`
  - observed result: `3/5 kobject_example.test.kobject sample keeps the pre-registration ownership boundary explicit...OK`
  - observed result: `4/5 kobject_example.test.kobject sample makes ownership snapshots reviewable across lifecycle stages...OK`
  - observed result: `5/5 kobject_example.test.kobject sample teardown keeps ownership boundaries explicit...OK`
  - observed result: `All 5 tests passed.`
- `zig test zigux/tests/phase5_kobject_example_survey.zig`
  - observed result: `1/2 phase5_kobject_example_survey.test.phase 5 kobject manifest records the exact bounded checks...OK`
  - observed result: `2/2 phase5_kobject_example_survey.test.phase 5 kobject contributor docs stay aligned with the shipped review surface...OK`
  - observed result: `All 2 tests passed.`

The shared `zigux/tests/phase5_build.zig` entrypoint remains the umbrella review gate recorded in the manifest and contributor prompts, but this bounded verification pass did not rerun the whole Phase 5 sample bundle.

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/kobject_example.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `KobjectExampleSample.descriptor()` still name `samples/kobject/kobject-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_kobject_example_manifest.json`, `zigux/tests/phase5_kobject_example_survey.zig`, `samples/zigux/README.md`, `Documentation/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` still describe the exact registration, single `register_runs` ownership claim, Linux `foo`/`baz`/`bar` attribute order, shared `0664` attribute mode pattern, integer roundtrip, and shared `baz` or `bar` dispatch contract run through `zigux/tests/phase5_build.zig`?
- do the replay contract and survey note still keep the static directory-name cue explicit, keep `emits_uevent = false`, and say dynamic kobjects stay out of scope for this Phase 5 sample?
- does this sample-backed survey note stay aligned with the manifest-backed survey, `samples/zigux/README.md`, `Documentation/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, and the shared `zigux/tests/phase5_build.zig` entrypoint so reviewers can see the whole shipped kobject review surface in one place?
- do the manifest prompts and exact checks still keep the unnamed attribute group shape plus the pre-registration ownership boundary, the initialized-only exit summary, the `ownershipSummary()` lifecycle snapshot, and the post-`exit()` rejection boundaries explicit instead of implying sysfs registration?
- do the ownership checks still keep the initialized-but-not-registered stage explicit by requiring zero active attributes and no show or store access until `registerAttributes()` claims ownership, while `ownershipSummary()` exposes the cold, initialized, registered, and exited stage transitions directly?
- if the sample behavior changes, is the manifest updated alongside the registration, attribute-order, teardown-summary, and lifecycle contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that sysfs creation, `kernel_kobj` integration, uevents, and loadable module registration remain out of scope for this Phase 5 sample?

## Next bounded step

Leave this narrow kobject-survey lane parked unless fresh repo inspection shows one more directly coupled wording drift in the landed sample-backed review surface. The next valid move, if the lane reopens, should stay inside one exact ownership, lifetime, or reviewability repair only.
