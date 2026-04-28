# Phase 5 Kobject Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=active`
- `PHASE5_SLICE=kobject-reference-sample-starter`
- scope: roadmap-vs-repo sample delivery, approved ownership-and-lifetime guidance, and exact bounded checks for the landed `samples/zigux/` kobject-style replay
- product boundary:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
  - `zigux/tests/phase5_kobject_example_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kobject/kobject-example.c` as one of the Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection now shows that current `master` carries all four roadmap-approved bounded Phase 5 reference samples under `samples/zigux/`, including the landed `kobject_example` slice. The kobject-specific job is no longer missing sample delivery; it is to keep this ownership-and-lifetime idiom, its exact checks, and its non-goals honest now that the broader Phase 5 anchor set is complete.

## Survey findings

- `samples/kobject/kobject-example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a subsystem slice.
- the Linux sample mixes three concerns:
  - a named directory under `/sys/kernel/`
  - three integer-backed attributes, with `baz` and `bar` sharing the same show and store path, the attribute array ordered as `foo`, `baz`, `bar`, and each attribute declared with mode `0664`
  - real sysfs and module-lifecycle substrate through `kobject_create_and_add`, `sysfs_create_group`, `kernel_kobj`, and module init or exit hooks
- the honest Phase 5 move is to make the directory name, attribute dispatch, attribute-array order, shared `0664` attribute mode pattern, and lifetime boundaries reviewable in memory while keeping sysfs creation, kernel object registration, and module wiring out of scope.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/kobject_example.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `KobjectExampleSample.descriptor()`
- it models only the directory name, the unnamed attribute group shape, the Linux `foo`/`baz`/`bar` attribute-array order, the shared `0664` attribute mode pattern, integer roundtrips, and the shared `baz` or `bar` dispatch path in memory
- it uses a tiny `init()` -> `registerAttributes()` -> `showValue()` or `storeValue()` -> `exit()` lifecycle so the initialized-but-not-registered ownership boundary and teardown remain explicit
- it provides one bounded self-check through `runAnchorReplay()` instead of implying a runtime-ready sysfs or module implementation

The exact checks currently recorded in `zigux/tests/phase5_kobject_example_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the in-memory sample keeps the Linux directory name `kobject_example` and an unnamed attribute group
- the replay summary keeps the Linux attribute array order `foo`, `baz`, `bar` explicit
- the replay summary keeps the Linux `foo`, `baz`, and `bar` attribute mode pattern explicit as `0664` for all three attributes
- `runAnchorReplay()` requires `init()` first, registers exactly three attributes, and leaves the sample in the `registered` stage
- the initialized-but-not-registered stage keeps the active attribute count at `0` and rejects show or store calls until `registerAttributes()` claims ownership
- storing `42` into `foo` renders back as `42\n`
- `baz` and `bar` share the same show and store path while still rendering `7\n` and `-5\n` through their own attribute names
- non-integer writes return `InvalidInteger`, and unknown attribute names remain explicit errors
- `exit()` clears the tracked values, removes the active attribute count, and rejects later show or store calls

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/kobject_example.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `KobjectExampleSample.descriptor()` still name `samples/kobject/kobject-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` still describe the exact registration, Linux `foo`/`baz`/`bar` attribute order, shared `0664` attribute mode pattern, integer roundtrip, and shared `baz` or `bar` dispatch contract run through `zigux/tests/phase5_build.zig`?
- does this sample-backed survey note stay aligned with the manifest-backed survey, `Documentation/zigux/review-checklist.md`, and the shared `zigux/tests/phase5_build.zig` entrypoint so reviewers can see the whole shipped kobject review surface in one place?
- do the manifest prompts and exact checks still keep the unnamed attribute group shape plus the pre-registration and post-`exit()` show or store rejection boundaries explicit instead of implying sysfs registration?
- do the ownership checks still keep the initialized-but-not-registered stage explicit by requiring zero active attributes and no show or store access until `registerAttributes()` claims ownership?
- if the sample behavior changes, is the manifest updated alongside the registration, attribute-order, attribute-mode, and lifecycle contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that sysfs creation, `kernel_kobj` integration, uevents, and loadable module registration remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The roadmap delivery gap is already closed. The more precise ongoing review job is:

- the repo now has a reviewable Phase 5 `kobject_example` sample plus manifest-backed checks for registration, attribute order, shared `0664` attribute mode, dispatch, parse failures, and teardown
- the full four-anchor Phase 5 reference-sample set is already landed on current `master`, so this note should describe the kobject slice as one approved ownership-and-lifetime idiom inside that completed anchor set rather than as a placeholder for a still-missing tranche item
- contributor guidance still needs to keep the in-memory directory, unnamed-group shape, attribute-array order, and pre-registration ownership boundary visibly separate from real sysfs or module substrate claims and from the later runtime pilot families

This slice keeps the landed `kobject` sample reviewable by recording the exact lifecycle, attribute-order, attribute-mode, ownership-boundary, and non-goal cues reviewers should check before approving future edits, without reopening the closed Phase 5 sample-delivery gap.

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux kobject example
   - `rg -n "samples/kobject/kobject-example.c|Phase 5" Documentation/zigux samples /workspace/agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP\ \(1\).md`
2. confirm the current `samples/zigux/` surface stays distinct from this reference-sample lane
   - `find samples/zigux -maxdepth 1 -type f | sort`
3. run the exact bounded Phase 5 sample checks
   - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`

## Non-goals

This survey does not yet claim:

- sysfs file creation parity
- `kernel_kobj` integration
- uevent delivery
- loadable module registration

## Next bounded step

Leave this narrow kobject-survey lane parked unless fresh repo inspection shows one more directly coupled wording drift in the landed sample-backed review surface, while keeping this Phase 5 idiom distinct from the later Phase 9 runtime starters.
