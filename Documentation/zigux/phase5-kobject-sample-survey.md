# Phase 5 Kobject Sample Survey

This note keeps the roadmap-backed `samples/kobject/kobject-example.c` anchor truthful inside the approved non-runtime Phase 5 sample lane.

## Status

- `PHASE5_STATUS=verified-mixed-readback-packet`
- `PHASE5_LANE_KEY=P5-L20`
- `PHASE5_SURVEYED_COMMIT=28a3bde2b3d68612f18d9bdd786be50c71c3173e`
- scope: keep the approved ownership-and-lifetime idiom reviewable while recording the current mixed direct-versus-public-tree-backed kobject packet without widening into sysfs, `kernel_kobj`, uevents, or module registration

## Current bounded packet on 2026-05-23

Fresh repo-first inspection in this run kept the strongest honest kobject packet aligned with the newer shared Phase 5 reminder packet instead of the older narrower split.

Authenticated contents readback in this run directly returned:

- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `samples/zigux/kobject_example_attr_group_contract.zig`
- `zigux/tests/phase5_kobject_attr_group_contract.zig`
- `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_build.zig`

The same-lane shared reminder packet on current `master` still keeps `samples/zigux/kobject_example.zig` explicit as the direct sample-root owner for this anchor even when this run's authenticated contents route flaked on that one path.

Fresh public current-`master` fallback remains the honest companion path for the still-flaky companion set:

- `zigux/tests/phase5_kobject_example_manifest.json`
- `zigux/tests/phase5_kobject_example_survey.zig`

That means the strongest current packet for this lane is:

- the direct sample-owned replay, bounded attr-group companion, focused attr-group replay, attr-group survey guard, and shared build-route companion are current direct evidence again
- the dedicated manifest and survey replay remain current public-tree-backed companions in this runtime when the authenticated contents route flakes on them
- connector-local `404` results on the companion paths are a readback limitation here, not proof that the packet vanished from `master`

## Approved idiom

The current kobject packet still describes the approved Phase 5 in-memory ownership-and-lifetime idiom for the roadmap anchor without implying runtime parity.

Keep these cues explicit:

- `runAnchorReplay()` still requires `init()` first, registers exactly three attributes, leaves the sample in the registered stage, keeps the unnamed attribute group explicit, and reads back `42`, `7`, and `-5` for `foo`, `baz`, and `bar`
- `runSingleInitBoundaryReplay()` keeps the one-time `init()` rule executable so a second `init()` still returns `InvalidLifecycleTransition` while the sample stays initialized with zero active attributes and `1/0/0` counters
- `runPreRegistrationBoundaryReplay()` keeps the initialized-but-not-registered zero-active-attributes boundary explicit before `registerAttributes()` opens the sample
- `runRegistrationOwnershipReplay()` keeps the cold-to-initialized-to-registered handoff, the `0` to `3` active-attribute transition, and duplicate-registration rejection explicit
- `runRegisteredBoundaryReplay()` keeps the already-registered duplicate-registration and replay-restart rejection packet explicit while still proving the registered sample can accept a bounded `foo` write/read roundtrip afterward
- `runInputValidationReplay()` keeps the shared `baz`/`bar` dispatch, invalid-integer rejection, and unknown-attribute rejection explicit while the sample remains in the `registered` stage
- `ownershipSummary()` and sample-owned `runOwnershipReplay()` still keep the cold, initialized, registered, and exited lifecycle packet explicit
- the exit split stays explicit as `abandoned_before_registration` for the initialized-only exit path and `tore_down_registered_attributes` for the registered teardown path
- `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` together keep the bounded `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, NULL-terminated attribute-list slot, and shared build-route linkage explicit rather than turning that companion into a fifth Phase 5 sample

## Direct Validation Routes

Keep the direct sample-owned validation cues explicit too:

- `zig test samples/zigux/kobject_example.zig` stays the sample-owned self-check for the ownership-and-lifetime packet
- `zig test --dep kobject_example_sample -Mroot=zigux/tests/phase5_kobject_example.zig -Mkobject_example_sample=samples/zigux/kobject_example.zig` stays the focused replay route for the same packet
- `zig test zigux/tests/phase5_kobject_example_survey.zig` stays the survey-packet guard for the sample-owned replay, the public-tree-backed manifest-and-survey split, and the shared build-route companion in this runtime

Keep the direct attr-group validation cues explicit too:

- `zig test samples/zigux/kobject_example_attr_group_contract.zig` stays the sample-owned self-check for the bounded attr-group companion
- `zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` stays the focused replay route for the same attr-group packet
- `zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` stays the survey-guard route that checks the companion, focused replay, and shared build-route markers together
- `zigux/tests/phase5_build.zig` remains the broader directly readable shared build-route companion for this packet rather than sample-local proof

## Contributor refresh prompts

When a same-lane change touches this anchor or one of its shared reminder surfaces, keep these questions explicit:

- does the note still treat `zigux/tests/phase5_build.zig` as the current directly readable shared build-route companion rather than parking it in the public-tree-backed bucket?
- does the note still treat `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` as the current public-tree-backed companion set rather than direct readback proof in this runtime?
- does the note still treat `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` as current direct evidence for the bounded attr-group companion packet?
- does the surrounding shared packet in `Documentation/zigux/phase5-sample-review-guide.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still describe the same mixed direct-versus-public-tree-backed split?
- do `runPreRegistrationBoundaryReplay()`, `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, `runOwnershipReplay()`, `runTeardownReplay()`, and the attr-group companion packet still describe the same bounded ownership-and-lifetime surface across the sample root, focused replay, companion survey guard, survey note, and shared build route?

## Non-goals

This note still does not claim:

- sysfs file creation parity
- `kernel_kobj` integration
- uevent delivery
- loadable module registration

## Next bounded step

Leave this lane parked unless a fresh reread changes one bounded fact inside the same packet.

If the lane reopens soon, start with `Documentation/zigux/phase5-kobject-sample-survey.md`, compare `Documentation/zigux/README.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, and verify only whether the current sample-root owner, direct sample-owned replay, bounded attr-group companion, focused attr-group replay, dedicated attr-group survey guard, shared build-route companion, and public-tree-backed manifest-plus-survey companions still keep the same split before widening anything else.
