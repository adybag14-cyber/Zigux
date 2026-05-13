# Phase 5 Kobject Sample Survey

This note tracks the bounded Phase 5 verification packet for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=verified-narrower-readback-packet`
- `PHASE5_LANE_KEY=P5-L20`
- scope: verify current kobject sample behavior and keep the survey note truthful about the exact non-runtime packet that direct readback still exposes on `master`
- current directly verified kobject packet on `master`:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `samples/zigux/README.md`
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`

## Why this note exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and still names `samples/kobject/kobject-example.c` as one of the approved Linux anchors.

The bounded job for this note is to record the current kobject behavior that the directly readable replay surfaces still enforce on `master`. The same-lane task here is to keep the note aligned with the narrower packet that direct readback actually returns today: the sample root, the focused test, and the manifest-backed contract are still readable, while `zigux/tests/phase5_kobject_example_survey.zig` and the shared `zigux/tests/phase5_build.zig` route are current public-tree gaps again.

## Current verified behavior on `master`

Fresh repo-first inspection on 2026-05-13 confirmed that the current directly verified kobject packet still keeps these sample behaviors explicit:

- `samples/zigux/kobject_example.zig` and `zigux/tests/phase5_kobject_example.zig` still keep the descriptor contract explicit for the `samples/kobject/kobject-example.c` anchor, including the in-memory `kobject_example` directory name, `requires_runtime_substrate = false`, and `provides_selfcheck = true`
- `runAnchorReplay()` still requires `init()` first, registers exactly three attributes, leaves the sample in the registered stage, keeps the attribute group unnamed, keeps the shared `baz` and `bar` handlers explicit, and still reads back default values `42`, `7`, and `-5` for `foo`, `baz`, and `bar`
- `runPreRegistrationBoundaryReplay()` still keeps the sample initialized, keeps `active_attr_count` at zero, and keeps pre-registration `show` and `store` rejection explicit
- calling `init()` twice still keeps the sample initialized, leaves `active_attr_count` at zero, and returns `InvalidLifecycleTransition` on the second init without advancing `register_runs` or `exit_runs`
- `runRegisteredBoundaryReplay()` still keeps the sample registered with three active attributes, keeps `init_runs = 1`, `register_runs = 1`, and `exit_runs = 0`, rejects duplicate registration and registered-stage anchor replay, and still allows a bounded `foo` write/read roundtrip afterward
- `runInputValidationReplay()` still keeps the sample registered while storing `9` into `baz` and `10` into `bar`, keeps invalid integer writes on `foo` rejected, leaves the `foo` value at `0` after the failed parse, and keeps unknown-attribute `show` and `store` rejection explicit
- `runOwnershipReplay()` still keeps the lifecycle packet explicit across the cold, initialized, registered, and exited snapshots, including active attribute counts `0`, `0`, `3`, and `0` and the counter progression `0/0/0`, `1/0/0`, `1/1/0`, and `1/1/1`
- the initialized-only exit path still reports `abandoned_before_registration`, while the registered exit path still reports `tore_down_registered_attributes`
- `runTeardownReplay()` still keeps the registered teardown reset explicit by clearing tracked values from `42`, `7`, and `-5` to `0`, `0`, and `0`, dropping the active attribute count back to zero, and rejecting reinit, reregister, post-exit `show`, post-exit `store`, second `exit()`, and post-exit anchor replay
- the public sample-facing replay surface still keeps direct `InvalidInteger` and `UnknownAttribute` failures visible through the focused test instead of hiding them behind survey wording alone
- shared reminder surfaces should keep that narrower sample-root-plus-focused-test-plus-manifest packet explicit and should not restate `zigux/tests/phase5_kobject_example_survey.zig` or `zigux/tests/phase5_build.zig` as directly readable evidence until a fresh reread proves they returned

## Exact checks recorded today

The current manifest-backed exact checks for the kobject packet are now recorded here as the same bounded review contract this note should preserve:

- `directory-name`: the in-memory sample keeps the Linux directory name `kobject_example` and an unnamed attribute group
- `registration-step`: `runAnchorReplay()` requires `init()` first, registers exactly three attributes, leaves the sample in the registered stage, and keeps duplicate `registerAttributes()` plus registered-stage `runAnchorReplay()` calls blocked by `InvalidLifecycleTransition`
- `pre-registration-boundary`: `runPreRegistrationBoundaryReplay()` leaves the sample initialized, keeps the active attribute count at zero, and shows that `show` or `store` still return `InvalidLifecycleTransition` before `registerAttributes()` opens the sample
- `single-init-boundary`: calling `init()` twice keeps the sample initialized, leaves the active attribute count at zero, and returns `InvalidLifecycleTransition` on the second init without advancing `register_runs` or `exit_runs`
- `registered-boundary`: `runRegisteredBoundaryReplay()` leaves the sample registered, keeps the active attribute count at three, keeps `register_runs` pinned at one across duplicate registration plus registered-stage anchor-replay rejection, and still allows a bounded `foo` write/read roundtrip afterward
- `ownership-summary`: `ownershipSummary()` and `runOwnershipReplay()` report the cold, initialized, registered, and exited stages with active attribute counts `0`, `0`, `3`, and `0`
- `ownership-counters`: `runOwnershipReplay()` keeps the init/register/exit counter progression explicit as `0/0/0`, `1/0/0`, `1/1/0`, and `1/1/1`
- `initialized-exit-disposition`: `exit()` reports `abandoned_before_registration` when the sample leaves the initialized stage before attributes are registered
- `foo-roundtrip`: storing `42` into `foo` renders back as the string `42` followed by a newline
- `shared-b-dispatch`: `runInputValidationReplay()` keeps `baz` and `bar` on the same `show` and `store` path while rendering `9` and `10` through their own attribute names after the replay stores those exact values
- `parse-failure`: `runInputValidationReplay()` keeps invalid-integer writes returning `InvalidInteger` and unknown attribute names as explicit errors while the sample remains in the registered stage
- `exit-boundary`: `runTeardownReplay()` reports `tore_down_registered_attributes`, clears the tracked values, removes the active attribute count, and keeps reinit, reregister, post-exit `show`, post-exit `store`, second `exit()`, and anchor-replay rejection explicit

## Recorded gap vs roadmap

The roadmap still calls for a reviewable Phase 5 kobject reference-pattern anchor, and the current directly readable packet still keeps that bounded goal visible through the sample root, the focused test, and the manifest-backed replay contract.

The precise same-lane gap is now reminder-surface truthfulness rather than sample behavior: `zigux/tests/phase5_kobject_example_survey.zig` and the shared `zigux/tests/phase5_build.zig` route are not directly readable on current `master`, so shared contributor guidance should keep the narrower packet explicit instead of presenting those missing paths as current evidence.

## Contributor Checklist

When a contributor updates `samples/zigux/kobject_example.zig` or one of its directly coupled review surfaces, keep these packet-local questions explicit here instead of relying on the broader shared guides alone:

- does the packet still keep the one-time `init()` rule explicit so a second `init()` returns `InvalidLifecycleTransition` without advancing `register_runs` or `exit_runs`?
- do `runPreRegistrationBoundaryReplay()`, `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, `runOwnershipReplay()`, and `runTeardownReplay()` still describe the same bounded ownership-and-lifetime packet across the sample root, focused test, and manifest?
- if a shared reminder surface mentions `zigux/tests/phase5_kobject_example_survey.zig` or `zigux/tests/phase5_build.zig`, did a fresh reread confirm those exact paths first?
- does the exit split still stay explicit so initialized-only exit reports `abandoned_before_registration` while registered exit reports `tore_down_registered_attributes`, without implying sysfs, `kernel_kobj`, uevents, or module-registration parity?

## Non-goals

This note still does not claim:

- sysfs file creation parity
- `kernel_kobj` integration
- uevent delivery
- loadable module registration

## Next bounded step

Leave this lane parked unless a fresh kobject reread changes one of two bounded facts:

- `zigux/tests/phase5_kobject_example_survey.zig` or `zigux/tests/phase5_build.zig` return and the survey note should restore broader direct-readback wording
- another shared reminder surface still presents those missing paths as directly readable and needs one more lane-local truthfulness repair

Do not widen that follow-up into sample behavior unless the sample-root file, focused test, or manifest actually changes.