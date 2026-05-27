# Phase 5 Kobject Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 kobject packet truthful when reviewers need one dedicated reminder of the bounded non-runtime idiom that current `master` still approves.

## Status

  * `PHASE5_STATUS=mixed-packet-approved-idiom-note`
  * `PHASE5_LANE_KEY=P5-L20`
  * `PHASE5_SLICE=kobject-approved-idiom-gap`
  * scope: keep the current ownership-and-lifetime sample packet reviewable without widening into sysfs, `kernel_kobj`, uevents, or module registration

## Current approved cue on `master`

The roadmap-backed Phase 5 anchor is still:

  * `samples/kobject/kobject-example.c`

The current mixed packet on `master` is still bounded and concrete.

The direct reminder or replay surfaces currently returned in this runtime are:

  * `Documentation/zigux/phase5-kobject-sample-survey.md`
  * `samples/zigux/kobject_example_attr_group_contract.zig`
  * `zigux/tests/phase5_kobject_attr_group_contract.zig`
  * `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`
  * `zigux/tests/phase5_kobject_example.zig`
  * `zigux/tests/phase5_build.zig`

The same-lane survey note and surrounding shared reminder packet still keep `samples/zigux/kobject_example.zig` explicit as the sample-root owner for this anchor even when the authenticated contents route flakes on that one path.

The current public-tree-backed companions are still:

  * `zigux/tests/phase5_kobject_example_manifest.json`
  * `zigux/tests/phase5_kobject_example_survey.zig`

Keep that mixed packet framed as current sample-backed evidence rather than as either a missing sample or a fully restored direct-authenticated packet.

## Approved idiom to preserve

Keep the approved Phase 5 kobject cue bounded to the current landed packet:

  * `KobjectExampleSample.descriptor()` still names `samples/kobject/kobject-example.c` and keeps `requires_runtime_substrate = false`
  * `runSingleInitBoundaryReplay()` still keeps the one-time `init()` rule explicit, with a second `init()` rejecting while the sample stays initialized with zero active attributes and `1/0/0` counters
  * `runPreRegistrationBoundaryReplay()` still keeps the initialized-but-not-registered zero-active-attributes boundary explicit before `registerAttributes()` opens the sample
  * `runRegistrationOwnershipReplay()` still keeps registration-before-init rejection, the cold-to-initialized-to-registered handoff, the `0` to `3` active-attribute transition, and duplicate-registration rejection reviewable
  * `runRegisteredBoundaryReplay()` still keeps duplicate-registration rejection, registered-stage replay rejection, and the still-usable registered-state `foo` write or read roundtrip explicit while the sample remains registered
  * `runInputValidationReplay()` still keeps the shared `baz` / `bar` dispatch, invalid-integer rejection, and unknown-attribute rejection explicit while the sample remains in the registered stage
  * `ownershipSummary()` and sample-owned `runOwnershipReplay()` still keep the cold, initialized, registered, and exited lifecycle packet explicit together with the `0/0/0` -> `1/0/0` -> `1/1/0` -> `1/1/1` counter progression
  * keep the exit split explicit too: `abandoned_before_registration` stays the initialized-only exit path, while `tore_down_registered_attributes` stays the registered teardown path
  * `samples/zigux/kobject_example_attr_group_contract.zig` plus `zigux/tests/phase5_kobject_attr_group_contract.zig` and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` still keep the bounded `foo` / `baz` / `bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot explicit without turning that companion into a fifth Phase 5 sample family

## Validation routes that keep the idiom repeatable

Keep the direct packet-local checks visible too:

  * `zig test samples/zigux/kobject_example.zig`
  * `zig test --dep kobject_example_sample -Mroot=zigux/tests/phase5_kobject_example.zig -Mkobject_example_sample=samples/zigux/kobject_example.zig`
  * `zig test zigux/tests/phase5_kobject_example_survey.zig`

Keep the bounded attr-group companion checks visible too:

  * `zig test samples/zigux/kobject_example_attr_group_contract.zig`
  * `zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig`
  * `zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig`

Those direct routes should stay the sample-owned self-check, the focused replay proof, the sample-root companion route, the focused attr-group replay route, and the survey guards for this approved idiom. Keep `zigux/tests/phase5_build.zig` framed as the current directly readable shared build-route companion for the same bounded packet rather than as sample-local proof.

## Review boundary

Use this note only to restate the bounded non-runtime idiom that Phase 5 reviewers should preserve inside the roadmap-backed `kobject-example` anchor.

Do not treat this note as proof of:

  * sysfs file creation parity
  * `kernel_kobj` integration
  * uevent delivery
  * loadable module registration
  * the later Phase 9 runtime sample family

## Next bounded step

Leave this note parked unless a fresh reread finds one new one-file drift between this approved-idiom note and the live kobject packet in `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, `zigux/tests/phase5_kobject_example_survey.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, or `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`.
