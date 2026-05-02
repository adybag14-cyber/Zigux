# Phase 5 Kobject Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=active`
- `PHASE5_SLICE=kobject-reference-sample-starter`
- `PHASE5_LANE_KEY=P5-L12`
- `PHASE5_SURVEYED_COMMIT=bc64354437727e63caed13a39203148016399d07`
- scope: roadmap-vs-repo sample delivery, approved ownership-and-lifetime guidance, and exact bounded checks for the landed `samples/zigux/` kobject-style replay
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

Fresh repo inspection now shows that current `master` carries all four roadmap-approved bounded Phase 5 reference samples under `samples/zigux/`, including the landed `kobject_example` slice. The kobject-specific job is no longer missing sample delivery; it is to keep this ownership-and-lifetime idiom, its exact checks, and its non-goals honest now that the broader Phase 5 anchor set is complete.
The shared sample-root catalog in `samples/zigux/README.md`, the shared tests-root guide in `zigux/tests/README.md`, plus the shared prompts in `Documentation/zigux/review-checklist.md` are part of that contributor-facing boundary now, because they are the shortest places to keep the landed kobject idiom visibly separate from the later runtime starter families while pointing reviewers back to the direct `zig test samples/zigux/kobject_example.zig` replay, the paired `zig test zigux/tests/phase5_kobject_example_survey.zig` replay, and the exact shipped review packet.

## Survey findings

- `samples/kobject/kobject-example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a subsystem slice.
- the Linux sample mixes three concerns:
  - a named directory under `/sys/kernel/`
  - three integer-backed attributes, with `baz` and `bar` sharing the same show and store path and the attribute array ordered as `foo`, `baz`, `bar`
  - real sysfs and module-lifecycle substrate through `kobject_create_and_add`, `sysfs_create_group`, `kernel_kobj`, and module init or exit hooks
- the honest Phase 5 move is to make the directory name, attribute dispatch, attribute-array order, shared `0664` attribute mode pattern, and lifetime boundaries reviewable in memory while keeping sysfs creation, kernel object registration, and module wiring out of scope.
- the shared sample-root catalog in `samples/zigux/README.md`, the shared tests-root guide in `zigux/tests/README.md`, and the shared `Documentation/zigux/review-checklist.md` prompts are part of that boundary now, because they keep the landed kobject packet discoverable as one approved ownership-and-lifetime idiom instead of leaving the review surface scattered between the sample, deeper note, and shared build entrypoint.
- the shared sample-root catalog now also carries a dedicated kobject review-packet stanza, so contributors can refresh the exact registration contract, ownership boundaries, and out-of-scope sysfs claims without having to infer them from the sample code alone.
- the shared tests-root guide in `zigux/tests/README.md` is part of that same contributor packet now, because it names the direct `zig test samples/zigux/kobject_example.zig` replay, the paired `zig test zigux/tests/phase5_kobject_example_survey.zig` replay, and the wider Phase 5 boundary cues that keep this landed sample distinct from the separate later runtime families.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/kobject_example.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `KobjectExampleSample.descriptor()`
- it models only the directory name, the unnamed attribute group shape, the Linux `foo`/`baz`/`bar` attribute-array order, the shared `0664` attribute mode pattern, integer roundtrips, and the shared `baz` or `bar` dispatch path in memory
- it keeps the static directory-name cue explicit, records no uevent delivery, and leaves dynamic kobjects out of scope for this sample
- it uses a tiny `init()` -> `registerAttributes()` -> `showValue()` or `storeValue()` -> `exit()` lifecycle so the initialized-but-not-registered ownership boundary, the initialized-only abandonment path, and registered teardown remain explicit
- it provides one bounded self-check through `runAnchorReplay()` instead of implying a runtime-ready sysfs or module implementation

The exact checks currently recorded in `zigux/tests/phase5_kobject_example_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the in-memory sample keeps the Linux directory name `kobject_example` and an unnamed attribute group
- the replay summary keeps the Linux attribute array order `foo`, `baz`, `bar` explicit
- the replay summary keeps the Linux `foo`, `baz`, and `bar` attribute mode pattern explicit as `0664` for all three attributes
- `runAnchorReplay()` requires `init()` first, claims attribute ownership through exactly one `register_runs` increment, registers exactly three attributes, and leaves the sample in the `registered` stage with attributes accessible
- the replay summary keeps the static directory name explicit, records no uevent delivery, and leaves dynamic kobjects out of scope for this sample
- the initialized-but-not-registered stage keeps the active attribute count at `0` and rejects show or store calls until `registerAttributes()` claims ownership
- the initialized-only `exit()` path returns an `abandoned_before_registration` teardown summary, keeps `register_runs` at `0`, and still leaves the sample exited with no active attributes
- storing `42` into `foo` renders back as `42\n`
- `baz` and `bar` share the same show and store path while still rendering `7\n` and `-5\n` through their own attribute names
- non-integer writes return `InvalidInteger`, and unknown attribute names remain explicit errors
- registered `exit()` returns a teardown summary, clears the tracked values, removes the active attribute count, and the post-`exit()` `init()`, `registerAttributes()`, `showValue()`, and `storeValue()` calls all remain rejected

## Latest verification snapshot

Current sample behavior was re-verified against `master` commit `bc64354437727e63caed13a39203148016399d07` on 2026-05-01 with the attached Zig toolchain.

The exact verification commands and observed results for this narrow verification pass were:

- `zig fmt --check samples/zigux/kobject_example.zig zigux/tests/phase5_kobject_example_survey.zig`
  - observed result: formatting already matched the checked-in files
- `zig test samples/zigux/kobject_example.zig`
  - observed result: `1/3 kobject_example.test.kobject sample replay keeps the anchor reviewable and non-runtime...OK`
  - observed result: `2/3 kobject_example.test.kobject sample keeps shared dispatch and parse failures explicit...OK`
  - observed result: `3/3 kobject_example.test.kobject sample teardown keeps ownership boundaries explicit...OK`
  - observed result: `All 3 tests passed.`
- `zig test zigux/tests/phase5_kobject_example_survey.zig`
  - observed result: `1/2 phase5_kobject_example_survey.test.phase 5 kobject manifest records the exact bounded checks...OK`
  - observed result: `2/2 phase5_kobject_example_survey.test.phase 5 kobject contributor docs stay aligned with the shipped review surface...OK`
  - observed result: `All 2 tests passed.`

The shared `zigux/tests/phase5_build.zig` entrypoint remains the umbrella review gate recorded in the manifest and contributor prompts, and the current published Phase 5 bundle snapshot for that same shared lane remains `Build Summary: 17/17 steps succeeded; 28/28 tests passed`, but this bounded verification pass did not rerun the whole Phase 5 sample bundle.

Those live runs confirmed that the shipped kobject sample still matches the exact bounded checks above: the in-memory replay keeps the Linux `foo`/`baz`/`bar` attribute order and shared `0664` mode pattern explicit, makes the single `register_runs` ownership claim visible before leaving the sample registered with attributes accessible, keeps the initialized-but-not-registered stage at an active attribute count of `0` while rejecting show or store access, reports `abandoned_before_registration` for the initialized-only `exit()` path, keeps the shared sample-root catalog and review-checklist prompts aligned with the manifest-backed packet, and clears registered teardown state while rejecting later `init()`, `registerAttributes()`, `showValue()`, and `storeValue()` calls.

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/kobject_example.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `KobjectExampleSample.descriptor()` still name `samples/kobject/kobject-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_kobject_example_manifest.json`, `zigux/tests/phase5_kobject_example_survey.zig`, `samples/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` still describe the exact registration, single `register_runs` ownership claim, Linux `foo`/`baz`/`bar` attribute order, shared `0664` attribute mode pattern, integer roundtrip, and shared `baz` or `bar` dispatch contract run through `zigux/tests/phase5_build.zig`?
- do the replay contract and survey note still keep the static directory-name cue explicit, keep `emits_uevent = false`, and say dynamic kobjects stay out of scope for this Phase 5 sample?
- does this sample-backed survey note stay aligned with the manifest-backed survey, `samples/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, and the shared `zigux/tests/phase5_build.zig` entrypoint so reviewers can see the whole shipped kobject review surface in one place?
- do the manifest prompts and exact checks still keep the unnamed attribute group shape plus the pre-registration ownership boundary, the initialized-only exit summary, and the post-`exit()` rejection boundaries explicit instead of implying sysfs registration?
- do the ownership checks still keep the initialized-but-not-registered stage explicit by requiring zero active attributes and no show or store access until `registerAttributes()` claims ownership?
- if the sample behavior changes, is the manifest updated alongside the registration, attribute-order, teardown-summary, and lifecycle contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that sysfs creation, `kernel_kobj` integration, uevents, and loadable module registration remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The roadmap delivery gap is already closed. The more precise ongoing review job is:

- the repo now has a reviewable Phase 5 `kobject_example` sample plus manifest-backed checks for registration, a single replay-side ownership claim, attribute order, shared `0664` attribute mode, initialized-only abandonment, dispatch, parse failures, and teardown
- this approved ownership-and-lifetime idiom is now pinned to `PHASE5_SURVEYED_COMMIT=bc64354437727e63caed13a39203148016399d07` so the survey note, manifest-backed checks, shared sample-root catalog, shared tests-root guide, shared review checklist, and contributor review path all point at the same inspected `master` head
- the full four-anchor Phase 5 reference-sample set is already landed on current `master`, so this note should describe the kobject slice as one approved ownership-and-lifetime idiom inside that completed anchor set rather than as a placeholder for a still-missing tranche item
- contributor guidance still needs to keep the in-memory directory, unnamed-group shape, attribute-array order, initialized-only abandonment path, and pre-registration ownership boundary visibly separate from real sysfs or module substrate claims and from the later runtime pilot families

This slice keeps the landed `kobject` sample reviewable by recording the exact lifecycle, replay-side ownership claim, initialized-only abandonment path, attribute-order, shared `0664` attribute mode, and non-goal cues reviewers should check before approving future edits, without reopening the closed Phase 5 sample-delivery gap.

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux kobject example
   - `rg -n "samples/kobject/kobject-example.c|Phase 5" Documentation/zigux/phase5-kobject-sample-survey.md Documentation/zigux/review-checklist.md samples/zigux/README.md`
2. confirm the current `samples/zigux/` surface stays distinct from this reference-sample lane
   - `find samples/zigux -maxdepth 1 -type f | sort`
3. run the focused self-check that keeps the in-memory replay explicit
   - `zig test samples/zigux/kobject_example.zig`
4. run the dedicated manifest-backed survey gate
   - `zig test zigux/tests/phase5_kobject_example_survey.zig`
5. run the exact bounded Phase 5 sample checks
   - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`

## Non-goals

This survey does not yet claim:

- sysfs file creation parity
- `kernel_kobj` integration
- uevent delivery
- loadable module registration

## Next bounded step

Leave this narrow kobject-survey lane parked unless fresh repo inspection shows one more directly coupled wording drift in the landed sample-backed review surface, while keeping this Phase 5 idiom distinct from the later Phase 9 runtime starters and preserving the exact verification packet recorded under `P5-L12`.
