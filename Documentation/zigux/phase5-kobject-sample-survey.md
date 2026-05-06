# Phase 5 Kobject Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_LANE_KEY=P5-Y03`
- `PHASE5_SURVEYED_COMMIT=545d33b54e22d50ca0aa32565bd73738d9634e24`
- `PHASE5_SLICE=kobject-reference-sample-starter`
- scope: roadmap-vs-repo sample delivery, approved ownership-and-lifetime guidance, and exact bounded checks for the first `samples/zigux/` kobject-style replay
- product boundary:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
  - `zigux/tests/phase5_kobject_example_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kobject/kobject-example.c` as one of the Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection already showed one landed Phase 5 FIFO reference sample plus several later runtime-oriented starters under `samples/zigux/`. The next missing bounded anchor was the kobject sample, especially because it gives Phase 5 a small ownership-and-lifetime example without claiming a real sysfs substrate.

## Survey findings

- `samples/kobject/kobject-example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a subsystem slice.
- the Linux sample mixes three concerns:
  - a named directory under `/sys/kernel/`
  - three integer-backed attributes, with `baz` and `bar` sharing the same show and store path
  - real sysfs and module-lifecycle substrate through `kobject_create_and_add`, `sysfs_create_group`, `kernel_kobj`, and module init or exit hooks
- the honest Phase 5 move is to make the directory name, attribute dispatch, and lifetime boundaries reviewable in memory while keeping sysfs creation, kernel object registration, and module wiring out of scope.
- the live shared contributor packet for this landed sample is broader than the sample file and its paired manifest alone: `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` all help keep this kobject note aligned with the same four-sample Phase 5 packet described from the docs root, scripts root, and tests root.

## Approved idiom for the landed kobject-style sample

Until a bounded runtime substrate exists, the landed Phase 5 `samples/zigux/` reference sample for this anchor should:

- model only the directory name, unnamed attribute group shape, integer-backed attributes, and lifecycle in memory
- keep the Linux anchor path explicit in a descriptor or note
- include a tiny self-check or manifest-backed replay for the registration, duplicate-registration rejection, registered-stage replay rejection, integer roundtrip, teardown expectations, and pre-registration access boundary that make the sample useful to reviewers
- make `ownershipSummary()` and sample-owned `runOwnershipReplay()` explicit so reviewers can read the `cold`, `initialized`, `registered`, and `exited` lifecycle packet without inferring it from counters or focused tests alone
- keep sample-owned `runPreRegistrationBoundaryReplay()` explicit so the initialized-but-not-registered zero-active-attributes plus no-show-or-store boundary stays executable in the sample packet instead of living only in focused tests
- keep initialized-only exit and registered teardown distinct through `abandoned_before_registration` and `tore_down_registered_attributes`
- keep sysfs creation, `kernel_kobj` integration, uevents, and module-registration claims out of scope unless a later lane lands the required substrate first

In practice, that means the approved landed idiom is an approved Phase 5 in-memory ownership-and-lifetime idiom, not a claim that Zigux already has sysfs creation, `kernel_kobj`, or module-registration parity.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/kobject_example.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `KobjectExampleSample.descriptor()`
- it models only the directory name, the unnamed attribute group shape, integer roundtrips, and the shared `baz` or `bar` dispatch path in memory
- it uses a tiny `init()` -> `registerAttributes()` -> `showValue()` or `storeValue()` -> `exit()` lifecycle so ownership and teardown remain explicit
- before `registerAttributes()`, the sample still reports zero active attributes and blocks `showValue()` or `storeValue()`, so the initialized-but-not-registered boundary stays as explicit as the exit boundary
- sample-owned `runPreRegistrationBoundaryReplay()` now keeps that initialized-but-not-registered access block executable instead of leaving it implied by focused tests alone
- once `registerAttributes()` succeeds, duplicate `registerAttributes()` calls and registered-stage `runAnchorReplay()` calls still return `InvalidLifecycleTransition`, so the already-registered boundary is replayable instead of implied
- `ownershipSummary()` keeps the per-stage lifecycle snapshot explicit across `cold`, `initialized`, `registered`, and `exited`
- sample-owned `runOwnershipReplay()` keeps the full cold-to-exited lifecycle and the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit without leaving the ownership replay trapped in focused test scaffolding
- `exit()` now distinguishes initialized-only abandonment with `abandoned_before_registration` from registered teardown with `tore_down_registered_attributes`
- it provides bounded sample-owned self-checks through `runAnchorReplay()` for attribute replay, `runPreRegistrationBoundaryReplay()` for the initialized-but-not-registered access block, `runRegisteredBoundaryReplay()` for the already-registered boundary, and `runOwnershipReplay()` for the lifecycle packet instead of implying a runtime-ready sysfs or module implementation

The exact checks currently recorded in `zigux/tests/phase5_kobject_example_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the in-memory sample keeps the Linux directory name `kobject_example` and an unnamed attribute group
- `runAnchorReplay()` requires `init()` first, registers exactly three attributes, leaves the sample in the `registered` stage, and still blocks duplicate `registerAttributes()` plus registered-stage `runAnchorReplay()` with `InvalidLifecycleTransition`
- `runPreRegistrationBoundaryReplay()` leaves the sample initialized, keeps `activeAttrCount()` at zero, and shows that `showValue()` or `storeValue()` still return `InvalidLifecycleTransition` before `registerAttributes()`
- `ownershipSummary()` and `runOwnershipReplay()` report the `cold`, `initialized`, `registered`, and `exited` stages with active attribute counts `0`, `0`, `3`, and `0`
- initialized-only `exit()` reports `abandoned_before_registration` before attributes are registered
- storing `42` into `foo` renders back as `42\n`
- `baz` and `bar` share the same show and store path while still rendering `7\n` and `-5\n` through their own attribute names
- non-integer writes return `InvalidInteger`, and unknown attribute names remain explicit errors
- registered `exit()` reports `tore_down_registered_attributes`, clears the tracked values, removes the active attribute count, and rejects later show or store calls

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/kobject_example.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `KobjectExampleSample.descriptor()` still name `samples/kobject/kobject-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` still describe the approved Phase 5 in-memory ownership-and-lifetime idiom: the exact registration, duplicate-registration rejection, registered-stage replay rejection, integer roundtrip, shared `baz` and `bar` dispatch, and pre-registration access boundary run through `zigux/tests/phase5_build.zig`?
- do the shared Phase 5 contributor surfaces in `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still point at this exact sample packet and keep it separate from later runtime-backed work instead of leaving this note to carry the boundary alone?
- do the manifest prompts still keep the initialized-but-not-registered zero-active-attributes plus no-show-or-store boundary explicit before `registerAttributes()` opens the sample?
- do the manifest prompts and exact checks still keep sample-owned `runPreRegistrationBoundaryReplay()` explicit for that initialized-but-not-registered boundary?
- do the manifest prompts and exact checks still keep duplicate `registerAttributes()` and registered-stage `runAnchorReplay()` rejection explicit once the sample is already registered?
- do the manifest prompts and exact checks still keep `ownershipSummary()` and sample-owned `runOwnershipReplay()` explicit across `cold`, `initialized`, `registered`, and `exited`?
- do the manifest prompts and exact checks still keep initialized-only `exit()` reporting `abandoned_before_registration` and registered `exit()` reporting `tore_down_registered_attributes`?
- do the manifest prompts and exact checks still keep the unnamed attribute group shape plus the post-`exit()` show or store rejection boundary explicit instead of implying sysfs registration?
- if the sample behavior changes, is the manifest updated alongside the registration and lifecycle contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that sysfs creation, `kernel_kobj` integration, uevents, and loadable module registration remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The current gap is not "Zigux has no kobject sample guidance." The more precise remaining job is:

- the repo now has a reviewable Phase 5 `kobject_example` sample plus manifest-backed checks for registration, duplicate-registration rejection, registered-stage replay rejection, pre-registration access blocking, ownership snapshots, initialized-only abandonment, dispatch, parse failures, and teardown
- contributor guidance still needs to keep the approved Phase 5 in-memory ownership-and-lifetime idiom visibly separate from real sysfs or module substrate claims
- the shared docs-root, sample-root, scripts-root, and tests-root contributor packet should stay explicit here too, so this survey note does not understate the already-shipped review surface for the landed sample
- current `master` now carries all four roadmap-backed Phase 5 reference samples, so this survey should stay explicit about the kobject sample's own ownership-and-lifetime boundary instead of implying that another Phase 5 anchor is still missing

This slice keeps the landed `kobject` sample reviewable by recording the exact lifecycle and non-goal cues reviewers should check before approving future edits.

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux kobject example
   - `rg -n "samples/kobject/kobject-example.c|PHASE5_LANE_KEY=P5-Y03|PHASE5_SURVEYED_COMMIT=545d33b54e22d50ca0aa32565bd73738d9634e24|Phase 5" Documentation/zigux samples`
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

Stay in the Phase 5 samples-and-reference-patterns lane and tighten contributor guidance or one exact replay check only if fresh repo inspection shows a real sample drift on current `master`, while keeping this landed Phase 5 sample distinct from the later Phase 9 runtime starters.
