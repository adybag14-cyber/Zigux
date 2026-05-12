# Phase 5 Kobject Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_LANE_KEY=P5-L20`
- `PHASE5_SURVEYED_COMMIT=28a3bde2b3d68612f18d9bdd786be50c71c3173e`
- `PHASE5_SLICE=kobject-reference-sample-starter`
- scope: roadmap-vs-repo sample delivery, approved ownership-and-lifetime guidance, and exact bounded checks for the first `samples/zigux/` kobject-style replay
- product boundary:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `.github/workflows/zigux-bootstrap.yml`
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
  - `zigux/tests/phase5_kobject_example_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kobject/kobject-example.c` as one of the Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection shows the bounded roadmap anchor is already landed as `samples/zigux/kobject_example.zig` inside the four-sample Phase 5 packet. The remaining same-lane job is no longer to add a missing kobject anchor; it is to keep the approved ownership-and-lifetime idiom and its coupled contributor surfaces truthful without claiming a real sysfs substrate.

## Survey findings

- `samples/kobject/kobject-example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a subsystem slice.
- the Linux sample mixes three concerns:
  - a named directory under `/sys/kernel/`
  - three integer-backed attributes, with `baz` and `bar` sharing the same show and store path
  - real sysfs and module-lifecycle substrate through `kobject_create_and_add`, `sysfs_create_group`, `kernel_kobj`, and module init or exit hooks
- the honest Phase 5 move is to make the directory name, attribute dispatch, and lifetime boundaries reviewable in memory while keeping sysfs creation, kernel object registration, and module wiring out of scope.
- the live shared contributor packet for this landed sample is broader than the sample file and its paired manifest alone: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `.github/workflows/zigux-bootstrap.yml` all help keep this kobject note aligned with the same four-sample Phase 5 packet described from the docs root, guide, checklist, sample root, scripts root, tests root, and workflow surface.
- the shared Phase 5 guide already keeps the workflow boundary honest for this landed sample: `.github/workflows/zigux-bootstrap.yml` reruns only `zig build test --build-file zigux/tests/phase5_build.zig --summary all`, while `make -C zigux phase5-test` and `make -C zigux phase5` stay local Linux-style wrappers over that same shared build entrypoint.
- the narrower same-lane guidance risk on current `master` is no longer missing broad docs-root coverage alone; it is the shared docs-root, checklist, sample-root, scripts-root, tests-root, and workflow packet drifting away from the exact kobject-owned replay names when a shared guidance edit touches the sample, manifest, review checklist, or survey note together.

## Approved idiom for the landed kobject-style sample

Until a bounded runtime substrate exists, the landed Phase 5 `samples/zigux/` reference sample for this anchor should:

- model only the directory name, unnamed attribute group shape, integer-backed attributes, and lifecycle in memory
- keep the Linux anchor path explicit in a descriptor or note
- include a tiny self-check or manifest-backed replay for the registration, duplicate-registration rejection, registered-stage replay rejection, integer roundtrip, shared `baz` and `bar` dispatch, and pre-registration access boundary that make the sample useful to reviewers
- make `ownershipSummary()` and sample-owned `runOwnershipReplay()` explicit so reviewers can read the `cold`, `initialized`, `registered`, and `exited` lifecycle packet without inferring it from counters or focused tests alone
- keep sample-owned `runPreRegistrationBoundaryReplay()` explicit so the initialized-but-not-registered zero-active-attributes plus no-show-or-store boundary stays executable in the sample packet instead of living only in focused tests
- keep sample-owned `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, and `runTeardownReplay()` explicit so the already-registered duplicate-registration and replay-restart rejection, the still-usable registered-state foo roundtrip afterward, the shared `baz`/`bar` dispatch plus parse-failure packet, and the registered teardown reset-and-rejection packet stay reviewable without forcing contributors to infer those boundaries from code or teardown assertions alone
- keep initialized-only exit and registered teardown distinct through `abandoned_before_registration` and `tore_down_registered_attributes`
- keep sysfs creation, `kernel_kobj` integration, uevents, and module-registration claims out of scope unless a later lane lands the required substrate first

In practice, that means the approved landed idiom is an approved Phase 5 in-memory ownership-and-lifetime idiom, not a claim that Zigux already has sysfs creation, `kernel_kobj`, or module-registration parity.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/kobject_example.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `KobjectExampleSample.descriptor()`
- it models only the directory name, the unnamed attribute group shape, integer roundtrips, and the shared `baz`/`bar` dispatch path in memory
- it uses a tiny `init()` -> `registerAttributes()` -> `showValue()` or `storeValue()` -> `exit()` lifecycle so ownership and teardown remain explicit
- before `registerAttributes()`, the sample still reports zero active attributes and blocks `showValue()` or `storeValue()`, so the initialized-but-not-registered boundary stays as explicit as the exit boundary
- sample-owned `runPreRegistrationBoundaryReplay()` now keeps that initialized-but-not-registered access block executable instead of leaving it implied by focused tests alone
- once `registerAttributes()` succeeds, duplicate `registerAttributes()` calls and registered-stage `runAnchorReplay()` calls still return `InvalidLifecycleTransition`, so the already-registered boundary is replayable instead of implied
- sample-owned `runRegisteredBoundaryReplay()` keeps that already-registered duplicate-registration and replay-restart packet executable while still proving the registered sample can accept a bounded foo write/read roundtrip afterward instead of leaving that recovery cue buried in focused tests alone
- sample-owned `runInputValidationReplay()` keeps the shared `baz`/`bar` dispatch, invalid-integer rejection, and unknown-attribute rejection packet executable while the sample remains in the `registered` stage instead of leaving those contributor cues split between helper methods and focused assertions
- `ownershipSummary()` keeps the per-stage lifecycle snapshot explicit across `cold`, `initialized`, `registered`, and `exited`
- sample-owned `runOwnershipReplay()` keeps the full cold-to-exited lifecycle and the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit without leaving the ownership replay trapped in focused test scaffolding
- `exit()` now distinguishes initialized-only abandonment with `abandoned_before_registration` from registered teardown with `tore_down_registered_attributes`
- sample-owned `runTeardownReplay()` keeps the registered teardown reset, post-`exit()` show-or-store rejection, second-`exit()` rejection, and anchor-replay rejection explicit without implying a runtime-ready sysfs or module implementation
- it provides bounded sample-owned self-checks through `runAnchorReplay()` for attribute replay, `runPreRegistrationBoundaryReplay()` for the initialized-but-not-registered access block, `runRegisteredBoundaryReplay()` for the already-registered boundary plus the still-usable foo roundtrip afterward, `runInputValidationReplay()` for the shared dispatch and parse-failure packet, `runOwnershipReplay()` for the lifecycle packet, and `runTeardownReplay()` for the registered teardown reset-and-rejection packet instead of implying a runtime-ready sysfs or module implementation

The exact checks currently recorded in `zigux/tests/phase5_kobject_example_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the in-memory sample keeps the Linux directory name `kobject_example` and an unnamed attribute group
- `runAnchorReplay()` requires `init()` first, registers exactly three attributes, leaves the sample in the `registered` stage, and still blocks duplicate `registerAttributes()` plus registered-stage `runAnchorReplay()` with `InvalidLifecycleTransition`
- `runPreRegistrationBoundaryReplay()` leaves the sample initialized, keeps `activeAttrCount()` at zero, and shows that `showValue()` or `storeValue()` still return `InvalidLifecycleTransition` before `registerAttributes()`
- `runRegisteredBoundaryReplay()` leaves the sample registered, keeps `activeAttrCount()` at three, makes duplicate `registerAttributes()` plus registered-stage `runAnchorReplay()` rejection explicit, and still allows a bounded foo write/read roundtrip afterward
- `runInputValidationReplay()` keeps the shared `baz`/`bar` dispatch plus invalid-integer and unknown-attribute rejection explicit while leaving the sample in the `registered` stage
- `ownershipSummary()` and `runOwnershipReplay()` report the `cold`, `initialized`, `registered`, and `exited` stages with active attribute counts `0`, `0`, `3`, and `0`
- `runOwnershipReplay()` keeps the init/register/exit counter progression explicit as `0/0/0`, `1/0/0`, `1/1/0`, and `1/1/1` across those same lifecycle snapshots
- initialized-only `exit()` reports `abandoned_before_registration` before attributes are registered
- storing `42` into `foo` renders back as `42\n`
- `baz` and `bar` share the same show and store path while still rendering `7\n` and `-5\n` through their own attribute names
- non-integer writes return `InvalidInteger`, and unknown attribute names remain explicit errors
- `runTeardownReplay()` reports `tore_down_registered_attributes`, clears the tracked values, removes the active attribute count, and keeps reinit, reregister, post-`exit()` show-or-store, second-`exit()`, and anchor-replay rejection explicit

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/kobject_example.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `KobjectExampleSample.descriptor()` still name `samples/kobject/kobject-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` still describe the approved Phase 5 in-memory ownership-and-lifetime idiom: the exact registration, duplicate-registration rejection, registered-stage replay rejection, integer roundtrip, shared `baz` and `bar` dispatch, and pre-registration access boundary run through `zigux/tests/phase5_build.zig`?
- does `Documentation/zigux/phase5-sample-review-guide.md` still route the shared Phase 5 contributor packet back through this exact kobject sample packet when a change touches more than one sample surface, while keeping the kobject note distinct from the later Phase 9 runtime starters?
- do the shared Phase 5 contributor surfaces in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still point at this exact sample packet, keep `ownershipSummary()` and sample-owned `runOwnershipReplay()` explicit as the shared ownership cues, keep the shared `phase5_build.zig` route plus the shipped `make -C zigux phase5-test` and `make -C zigux phase5` wrappers explicit, and keep it separate from later runtime-backed work instead of leaving this note to carry the boundary alone?
- do those same shared contributor surfaces plus `.github/workflows/zigux-bootstrap.yml` still keep workflow wording honest by treating `zig build test --build-file zigux/tests/phase5_build.zig --summary all` as the only shared CI replay while `make -C zigux phase5-test` and `make -C zigux phase5` stay local Linux-style wrappers over that same build entrypoint?
- does the shared docs-root, checklist, sample-root, scripts-root, and tests-root contributor packet still keep sample-owned `runPreRegistrationBoundaryReplay()`, `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, `runTeardownReplay()`, and the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit enough that reviewers do not have to reconstruct the authoritative kobject packet by hand?
- do the manifest prompts still keep the initialized-but-not-registered zero-active-attributes plus no-show-or-store boundary explicit before `registerAttributes()` opens the sample?
- do the manifest prompts and exact checks still keep sample-owned `runPreRegistrationBoundaryReplay()` explicit for that initialized-but-not-registered boundary?
- do the manifest prompts and exact checks still keep sample-owned `runRegisteredBoundaryReplay()` explicit for the already-registered duplicate-registration and replay-restart rejection packet while also keeping the still-usable registered-state foo roundtrip explicit afterward?
- do the manifest prompts and exact checks still keep sample-owned `runInputValidationReplay()` explicit for the shared `baz`/`bar` dispatch plus parse-failure visibility packet while the sample stays in the `registered` stage?
- do the manifest prompts and exact checks still keep `ownershipSummary()` and sample-owned `runOwnershipReplay()` explicit across `cold`, `initialized`, `registered`, and `exited`?
- do the manifest prompts and exact checks still keep sample-owned `runTeardownReplay()` explicit for the registered teardown reset, post-`exit()` show-or-store rejection, second-`exit()` rejection, and anchor-replay rejection packet?
- do the manifest prompts and exact checks still keep initialized-only `exit()` reporting `abandoned_before_registration` and registered `exit()` reporting `tore_down_registered_attributes`?
- do the manifest prompts and exact checks still keep the unnamed attribute group shape plus the post-`exit()` show or store rejection boundary explicit instead of implying sysfs registration?
- if the sample behavior changes, is the manifest updated alongside the registration and lifecycle contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that sysfs creation, `kernel_kobj` integration, uevents, and loadable module registration remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The current gap is not "Zigux has no kobject sample guidance." The more precise remaining job is:

- the repo now has a reviewable Phase 5 `kobject_example` sample plus manifest-backed checks for registration, duplicate-registration rejection, registered-stage replay rejection, pre-registration access blocking, shared-dispatch and parse-failure visibility through `runInputValidationReplay()`, ownership snapshots, initialized-only abandonment, and teardown
- the broader shared contributor packet is now already present across `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, but those shared summaries still need to keep the exact kobject-owned replay names explicit enough that the authoritative packet can be re-read from the broader contributor surfaces instead of being reconstructed from code or focused tests alone
- the live same-lane reviewability risk is drift between that shared packet and the exact kobject-owned replay names: `runPreRegistrationBoundaryReplay()`, `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, `runOwnershipReplay()`, and `runTeardownReplay()`
- follow-up in this lane should therefore stay inside survey-note, manifest-prompt, or shared-guide truthfulness for those existing replays instead of widening into new sample semantics, runtime substrate claims, or another Phase 5 anchor

This slice keeps the landed `kobject` sample reviewable by recording the exact lifecycle and non-goal cues reviewers should check before approving future edits.

## Latest verification snapshot

Fresh focused current-`master` review-surface readback on 2026-05-11 kept the shipped kobject packet repo-local and explicit after this workflow-surface sync.

- connector-backed current-`master` inspection confirmed that `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, `zigux/tests/phase5_kobject_example_survey.zig`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `.github/workflows/zigux-bootstrap.yml`, and the shared `zigux/tests/phase5_build.zig` route still describe the same bounded non-runtime packet
- the shared contributor packet still keeps workflow wording honest for this note too: `.github/workflows/zigux-bootstrap.yml` reruns only `zig build test --build-file zigux/tests/phase5_build.zig --summary all`, while `make -C zigux phase5-test` and `make -C zigux phase5` remain local Linux-style wrappers over that same build entrypoint
- the landed survey note still keeps sample-owned `runPreRegistrationBoundaryReplay()`, `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, `runOwnershipReplay()`, and `runTeardownReplay()` explicit across the same initialized-only, registered, parse-failure, lifecycle, and teardown boundaries the manifest-backed packet already names
- the broader Phase 5 contributor packet still keeps this sample distinct from the no-sample `string`, `cmdline`, `argv_split`, and `rbtree` Phase 7 helper surfaces, from the direct no-sample Phase 5 `bitmap` boundary, and from later runtime-backed work instead of implying a fifth helper sample, a fifth direct bitmap sample, or a sysfs-backed Phase 5 runtime surface
- the note still keeps sysfs creation, `kernel_kobj` integration, uevents, and module registration marked out of scope, so the current review surface remains an in-memory ownership-and-lifetime sample rather than a runtime substrate claim

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux kobject example
   - `rg -n "samples/kobject/kobject-example.c|PHASE5_LANE_KEY=P5-L20|PHASE5_SURVEYED_COMMIT=28a3bde2b3d68612f18d9bdd786be50c71c3173e|Phase 5" Documentation/zigux samples`
2. confirm the current `samples/zigux/` surface stays distinct from this reference-sample lane
   - `find samples/zigux -maxdepth 1 -type f | sort`
3. run the exact bounded Phase 5 sample checks
   - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
   - `make -C zigux phase5-test`
   - `make -C zigux phase5`

## Non-goals

This survey does not yet claim:

- sysfs file creation parity
- `kernel_kobj` integration
- uevent delivery
- loadable module registration

## Next bounded step

Leave this lane parked unless fresh repo inspection shows the shared Phase 5 guide, the per-sample kobject survey note, or the manifest-backed replay prompts drifting apart. If that happens, keep the follow-through limited to the smallest truthfulness repair across those existing contributor surfaces instead of widening into new sample semantics or runtime substrate claims.
